# Copyright 2014-2015 Boxkite Inc.

# This file is part of the DataCats package and is released under
# the terms of the GNU Affero General Public License version 3.0.
# See LICENSE.txt or http://www.fsf.org/licensing/licenses/agpl-3.0.html

from __future__ import absolute_import

from os import environ
import json
from urlparse import urlparse
from functools import cmp_to_key
from warnings import warn

from docker import Client
try:
    # Versions after 1.2.0
    from docker.constants import DEFAULT_DOCKER_API_VERSION
except ImportError:
    # Versions before 1.2.0
    from docker.client import DEFAULT_DOCKER_API_VERSION
from docker.utils import kwargs_from_env, compare_version, create_host_config
from docker.errors import APIError

MINIMUM_API_VERSION = '1.16'

def get_api_version(*versions):
    # compare_version is backwards
    def cmp(a, b):
        return -1 * compare_version(a, b)
    return min(versions, key=cmp_to_key(cmp))

_docker_kwargs = kwargs_from_env()
_version_client = Client(version=MINIMUM_API_VERSION, **_docker_kwargs)
_version = get_api_version(DEFAULT_DOCKER_API_VERSION,
    _version_client.version()['ApiVersion'])

_docker = Client(version=_version, **_docker_kwargs)

class WebCommandError(Exception):
    def __str__(self):
        return ('Command failed: {0}\n  View output:'
            ' docker logs {1}\n  Remove stopped container:'
            ' docker rm {1}'.format(*self.args))

class PortAllocatedError(Exception):
    pass

_boot2docker = None
def is_boot2docker():
    global _boot2docker
    if _boot2docker is None:
        _boot2docker = 'Boot2Docker' in _docker.info()['OperatingSystem']
    return _boot2docker

def docker_host():
    url = _docker_kwargs.get('base_url')
    if not url:
        return 'localhost'
    return urlparse(url).netloc.split(':')[0]


def ro_rw_to_binds(ro, rw):
    """
    ro and rw {localdir: binddir} dicts to docker-py's
    {localdir: {'bind': binddir, 'ro': T/F}} binds dicts
    """
    out = {}
    if ro:
        for localdir, binddir in ro.iteritems():
            out[localdir] = {'bind': binddir, 'ro': True}
    if rw:
        for localdir, binddir in rw.iteritems():
            out[localdir] = {'bind': binddir, 'ro': False}
    return out

def binds_to_volumes(volumes):
    """
    Return the target 'bind' dirs of volumnes from a volumes dict
    for passing to create_container
    """
    return [v['bind'] for v in volumes.itervalues()]

def web_command(command, ro=None, rw=None, links=None,
        image='datacats/web', volumes_from=None, commit=False,
        clean_up=False, stream_output=None):
    """
    Run a single command in a web image optionally preloaded with the ckan
    source and virtual envrionment.

    :param command: command to execute
    :param ro: {localdir: binddir} dict for read-only volumes
    :param rw: {localdir: binddir} dict for read-write volumes
    :param links: links passed to start
    :param image: docker image name to use
    :param volumes_from:
    :param commit: True to create a new image based on result
    :param clean_up: True to remove container even on error
    :param stream_output: file to write stderr+stdout from command

    :returns: image id if commit=True
    """
    binds = ro_rw_to_binds(ro, rw)
    c = _docker.create_container(
        image=image,
        command=command,
        volumes=binds_to_volumes(binds),
        detach=False,
        host_config=create_host_config(binds=binds))
    _docker.start(
        container=c['Id'],
        links=links,
        binds=binds,
        volumes_from=volumes_from)
    if stream_output:
        for output in _docker.attach(
                c['Id'], stdout=True, stderr=True, stream=True):
            stream_output.write(output)
    if _docker.wait(c['Id']):
        if clean_up:
            remove_container(c['Id'])
        raise WebCommandError(command, c['Id'][:12])
    if commit:
        rval = _docker.commit(c['Id'])
    if not remove_container(c['Id']):
        # circle ci doesn't let us remove containers, quiet the warnings
        if not environ.get('CIRCLECI', False):
            warn('failed to remove container: {0}'.format(c['Id']))
    if commit:
        return rval['Id']

def run_container(name, image, command=None, environment=None,
        ro=None, rw=None, links=None, detach=True, volumes_from=None,
        port_bindings=None):
    """
    Wrapper for docker create_container, start calls

    :returns: container info dict or None if container couldn't be created

    Raises PortAllocatedError if container couldn't start on the
    requested port.
    """
    binds = ro_rw_to_binds(ro, rw)
    c = _docker.create_container(
        name=name,
        image=image,
        command=command,
        environment=environment,
        volumes=binds_to_volumes(binds),
        detach=detach,
        stdin_open=False,
        tty=False,
        ports=list(port_bindings) if port_bindings else None,
        host_config=create_host_config(binds=binds))
    try:
        _docker.start(
            container=c['Id'],
            links=links,
            binds=binds,
            volumes_from=volumes_from,
            port_bindings=port_bindings)
    except APIError as e:
        if 'address already in use' in e.explanation:
            try:
                _docker.remove_container(name, force=True)
            except APIError:
                pass
            raise PortAllocatedError()
        raise
    return c

def remove_container(name, force=False):
    """
    Wrapper for docker remove_container

    :returns: True if container was found and removed
    """

    try:
        if not force:
            _docker.stop(name)
    except APIError as e:
        pass
    try:
        _docker.remove_container(name, force=True)
        return True
    except APIError as e:
        return False

def inspect_container(name):
    """
    Wrapper for docker inspect_container

    :returns: container info dict or None if not found
    """
    try:
        return _docker.inspect_container(name)
    except APIError as e:
        return None

def container_logs(name, tail, follow, timestamps):
    """
    Wrapper for docker logs, attach commands.
    """
    if follow:
        return _docker.attach(
            name,
            stdout=True,
            stderr=True,
            stream=True
            )
    return _docker.logs(
        name,
        stdout=True,
        stderr=True,
        tail=tail,
        timestamps=timestamps,
        )

def pull_stream(image):
    """
    Return generator of pull status objects
    """
    return (json.loads(s) for s in _docker.pull(image, stream=True))

def data_only_container(name, volumes):
    """
    create "data-only container" if it doesn't already exist.

    We'd like to avoid these, but postgres + boot2docker make
    it difficult, see issue #5
    """
    info = inspect_container(name)
    if info:
        return
    c = _docker.create_container(
        name=name,
        image='datacats/postgres', # any image will do
        command='true',
        volumes=volumes,
        detach=True)
    return c

remove_image = _docker.remove_image
