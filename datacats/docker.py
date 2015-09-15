# Copyright 2014-2015 Boxkite Inc.

# This file is part of the DataCats package and is released under
# the terms of the GNU Affero General Public License version 3.0.
# See LICENSE.txt or http://www.fsf.org/licensing/licenses/agpl-3.0.html

from __future__ import absolute_import

import sys

from datacats.scripts import get_script_path
from os import environ, devnull
import json
import subprocess
import tempfile
from urlparse import urlparse
from functools import cmp_to_key
from warnings import warn

# XXX our fixes on top of fixes to work with docker-py and docker
# incompatibilities are approaching the level of superstition.
# let's hope docker calms down a bit so we can clean this out
# in the future.

from docker import Client
from docker.constants import DEFAULT_DOCKER_API_VERSION
from docker.utils import kwargs_from_env, compare_version, create_host_config, LogConfig
from docker.errors import APIError, TLSParameterError
from requests import ConnectionError

from datacats.error import (DatacatsError,
        WebCommandError, PortAllocatedError)

MINIMUM_API_VERSION = '1.16'


def get_api_version(*versions):
    # compare_version is backwards
    def rev_cmp(a, b):
        return -1 * compare_version(a, b)
    return min(versions, key=cmp_to_key(rev_cmp))

# Lazy instantiation of _docker
_docker = None

try:
    _docker_kwargs = kwargs_from_env()
except TLSParameterError:
    print ('Please create your docker-machine VM with the command'
           ' "docker-machine create --driver=virtualbox dev"')
    exit(1)


def _boot2docker_check_connectivity():
    # HACK: We determine from commands if we're boot2docker
    # Needed cause this method is called from is_boot2docker...
    with open(devnull, 'w') as devnull_f:
        try:
            status = subprocess.check_output(
                ['docker-machine', 'status', 'dev'],
                stderr=devnull_f).strip()
            if status == 'Stopped':
                raise DatacatsError('Please start your docker-machine '
                                    'VM with "docker-machine start dev"')

            # XXX HACK: This exists because of
            #           http://github.com/datacats/datacats/issues/63,
            # as a temporary fix.
            if 'tls' in _docker_kwargs:
                # It will print out messages to the user otherwise.
                _docker_kwargs['tls'].assert_hostname = False
        except OSError:
            # Docker machine isn't installed.
            try:
                status = subprocess.check_output(
                    ['boot2docker', 'status'],
                    stderr=devnull_f).strip()
                if status == 'poweroff':
                    raise DatacatsError('Your boot2docker machine is '
                                        'powered off. Please run "boot2docker up"'
                                        'to power it on. Alternatively you '
                                        'can migrate to the newer docker-machine.')
                print ('Please note that boot2docker support in datacats is '
                       'deprecated in favour of docker-machine')
                # XXX HACK: This exists because of
                #           http://github.com/datacats/datacats/issues/63,
                # as a temporary fix.
                if 'tls' in _docker_kwargs:
                    # It will print out messages to the user otherwise.
                    _docker_kwargs['tls'].verify = False
            except OSError:
                # We're probably on Linux or a new Mac.
                pass
            except subprocess.CalledProcessError:
                raise DatacatsError('Boot2docker VM is not created. '
                                    'You can create a VM through '
                                    'the command "boot2docker init". '
                                    'Boot2docker has been deprecated '
                                    'and we at DataCats suggest you '
                                    'migrate to docker-machine.')
        except subprocess.CalledProcessError:
            raise DatacatsError('Please create a docker-machine with '
                                '"docker-machine start dev"')


def _get_docker():
    global _docker

    if not _docker:
        if sys.platform.startswith('darwin'):
            _boot2docker_check_connectivity()

        # Create the Docker client
        version_client = Client(version=MINIMUM_API_VERSION, **_docker_kwargs)
        try:
            api_version = version_client.version()['ApiVersion']
        except ConnectionError:
            # workaround for connection issue when old version specified
            # on some clients
            version_client = Client(**_docker_kwargs)
            api_version = version_client.version()['ApiVersion']

        version = get_api_version(DEFAULT_DOCKER_API_VERSION, api_version)
        _docker = Client(version=version, **_docker_kwargs)

    return _docker

_boot2docker = None


def is_boot2docker():
    global _boot2docker
    if _boot2docker is None:
        _boot2docker = 'Boot2Docker' in _get_docker().info()['OperatingSystem']
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
                clean_up=False, stream_output=None, entrypoint=None):
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
    :param entrypoint: override entrypoint (script that runs command)

    :returns: image id if commit=True
    """
    binds = ro_rw_to_binds(ro, rw)
    c = _get_docker().create_container(
        image=image,
        command=command,
        volumes=binds_to_volumes(binds),
        detach=False,
        host_config=create_host_config(binds=binds),
        entrypoint=entrypoint)
    _get_docker().start(
        container=c['Id'],
        links=links,
        binds=binds,
        volumes_from=volumes_from)
    if stream_output:
        for output in _get_docker().attach(
                c['Id'], stdout=True, stderr=True, stream=True):
            stream_output.write(output)
    if _get_docker().wait(c['Id']):
        # Before the (potential) cleanup, grab the logs!
        logs = _get_docker().logs(c['Id'])

        if clean_up:
            remove_container(c['Id'])
        raise WebCommandError(command, c['Id'][:12], logs)
    if commit:
        rval = _get_docker().commit(c['Id'])
    if not remove_container(c['Id']):
        # circle ci doesn't let us remove containers, quiet the warnings
        if not environ.get('CIRCLECI', False):
            warn('failed to remove container: {0}'.format(c['Id']))
    if commit:
        return rval['Id']


def remote_server_command(command, environment, user_profile, **kwargs):
    """
      Wraps web_command function with docker bindings needed to connect to
      a remote server (such as datacats.com) and run commands there
      (for example, when you want to copy your catalog to that server).

      The files binded to the docker image include the user's ssh credentials:
          ssh_config file,
          rsa and rsa.pub user keys
          known_hosts whith public keys of the remote server (if known)

      The **kwargs (keyword arguments) are passed on to the web_command call
      intact, see the web_command's doc string for details
    """

    if environment.remote_server_key:
        temp = tempfile.NamedTemporaryFile(mode="wb")
        temp.write(environment.remote_server_key)
        temp.seek(0)
        known_hosts = temp.name
    else:
        known_hosts = get_script_path('known_hosts')

    binds = {
        user_profile.profiledir + '/id_rsa': '/root/.ssh/id_rsa',
        known_hosts: '/root/.ssh/known_hosts',
        get_script_path('ssh_config'): '/etc/ssh/ssh_config'
    }

    if kwargs.get("include_project_dir", None):
        binds[environment.target] = '/project'
        del kwargs["include_project_dir"]

    kwargs["ro"] = binds
    try:
        web_command(command, **kwargs)
    except WebCommandError as e:
        e.user_description = 'Sending a command to remote server failed'
        raise e


def run_container(name, image, command=None, environment=None,
                  ro=None, rw=None, links=None, detach=True, volumes_from=None,
                  port_bindings=None, log_syslog=False):
    """
    Wrapper for docker create_container, start calls

    :param log_syslog: bool flag to redirect container's logs to host's syslog

    :returns: container info dict or None if container couldn't be created

    Raises PortAllocatedError if container couldn't start on the
    requested port.
    """
    binds = ro_rw_to_binds(ro, rw)
    log_config = LogConfig(type=LogConfig.types.JSON)
    if log_syslog:
        log_config = LogConfig(
            type=LogConfig.types.SYSLOG,
            config={'syslog-tag': name})
    host_config = create_host_config(binds=binds, log_config=log_config)

    c = _get_docker().create_container(
        name=name,
        image=image,
        command=command,
        environment=environment,
        volumes=binds_to_volumes(binds),
        detach=detach,
        stdin_open=False,
        tty=False,
        ports=list(port_bindings) if port_bindings else None,
        host_config=host_config)
    try:
        _get_docker().start(
            container=c['Id'],
            links=links,
            binds=binds,
            volumes_from=volumes_from,
            port_bindings=port_bindings)
    except APIError as e:
        if 'address already in use' in e.explanation:
            try:
                _get_docker().remove_container(name, force=True)
            except APIError:
                pass
            raise PortAllocatedError()
        raise
    return c


def rename_container(old_name, new_name):
    _docker.rename(old_name, new_name)


def image_exists(name):
    """
    Queries Docker about if a particular image has been downloaded.

    :param name: The name of the image to check for.
    """
    # This returns a list of container dicts matching (exactly)
    # the name `name`.
    return bool(_get_docker().images(name=name))


def remove_container(name, force=False):
    """
    Wrapper for docker remove_container

    :returns: True if container was found and removed
    """

    try:
        if not force:
            _get_docker().stop(name)
    except APIError:
        pass
    try:
        _get_docker().remove_container(name, force=True)
        return True
    except APIError:
        return False


def container_running(name):
    return inspect_container(name)


def inspect_container(name):
    """
    Wrapper for docker inspect_container

    :returns: container info dict or None if not found
    """
    try:
        return _get_docker().inspect_container(name)
    except APIError:
        return None


def container_logs(name, tail, follow, timestamps):
    """
    Wrapper for docker logs, attach commands.
    """
    if follow:
        return _get_docker().attach(
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


def collect_logs(name):
    """
    Returns a string representation of the logs from a container.
    This is similar to container_logs but uses the `follow` option
    and flattens the logs into a string instead of a generator.

    :param name: The container name to grab logs for
    :return: A string representation of the logs
    """
    logs = container_logs(name, "all", True, None)
    string = ""
    for s in logs:
        string += s
    return string


def check_connectivity():
    c = run_container(None, 'datacats/web', '/project/check_connectivity.sh',
                      ro={get_script_path('check_connectivity.sh'):
                          '/project/check_connectivity.sh'},
                      detach=False)
    return collect_logs(c['Id'])


def pull_stream(image):
    """
    Return generator of pull status objects
    """
    return (json.loads(s) for s in _get_docker().pull(image, stream=True))


def data_only_container(name, volumes):
    """
    create "data-only container" if it doesn't already exist.

    We'd like to avoid these, but postgres + boot2docker make
    it difficult, see issue #5
    """
    info = inspect_container(name)
    if info:
        return
    c = _get_docker().create_container(
        name=name,
        image='datacats/postgres',  # any image will do
        command='true',
        volumes=volumes,
        detach=True)
    return c


def remove_image(image, force=False, noprune=False):
    _get_docker().remove_image(image, force=force, noprune=noprune)


def get_tags(image):
    return [i['RepoTags'][0].split(':')[1] for i in _get_docker().images(image)]


def require_images():
    """
    Raises a DatacatsError if the images required to use Datacats don't exist.
    """
    if (not image_exists('datacats/web') or
            not image_exists('datacats/solr') or
            not image_exists('datacats/postgres')):
        raise DatacatsError(
            'You do not have the needed Docker images. Please run "datacats pull"')
