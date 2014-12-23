from __future__ import absolute_import

from os import environ

from docker import Client
from docker.utils import kwargs_from_env
from docker.errors import APIError

_docker_kwargs = kwargs_from_env()
_docker = Client(**_docker_kwargs)

class WebCommandError(Exception):
    pass


def is_boot2docker():
    return 'boot2docker' in _docker_kwargs.get('base_url', '')

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
        preload_ckan_version=None):
    """
    Run a single command in a web image preloaded with the ckan
    source and virtual envrionment.

    :param command: command to execute
    :param ro: {localdir: binddir} dict for read-only volumes
    :param rw: {localdir: binddir} dict for read-write volumes
    :param links: links passed to start
    :param preload_ckan_version: 'master' for preload image
    """
    image = 'datacats/web'
    if preload_ckan_version:
        image='datacats/web:preload_{0}'.format(preload_ckan_version)

    binds = ro_rw_to_binds(ro, rw)
    c = _docker.create_container(
        image=image,
        command=command,
        volumes=binds_to_volumes(binds),
        detach=False)
    _docker.start(
        container=c['Id'],
        links=links,
        binds=binds)
    if _docker.wait(c['Id']):
        raise WebCommandError(command)
    _docker.remove_container(container=c['Id'])

def run_container(name, image, command=None, environment=None,
        ro=None, rw=None, links=None, detach=True, volumes_from=None):
    """
    simple wrapper for docker create_container, start calls

    :returns: container info dict or None if container couldn't be created
    """
    binds = ro_rw_to_binds(ro, rw)
    try:
        c = _docker.create_container(
            name=name,
            image=image,
            command=command,
            environment=environment,
            volumes=binds_to_volumes(binds),
            detach=detach)
    except APIError as e:
        return None
    _docker.start(
        container=c['Id'],
        links=links,
        binds=binds,
        volumes_from=volumes_from)
    return c

def remove_container(name, force=True):
    """
    Wrapper for docker remove_container

    :returns: True if container was found and removed
    """

    try:
        _docker.remove_container(name, force=force)
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
        image='scratch', # minimal container
        command='true',
        volumes=volumes,
        detach=True)
    return c
