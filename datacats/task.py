# Copyright 2014-2015 Boxkite Inc.

# This file is part of the DataCats package and is released under
# the terms of the GNU Affero General Public License version 3.0.
# See LICENSE.txt or http://www.fsf.org/licensing/licenses/agpl-3.0.html

"""
This modle includes the implementations for many Environment methods
separated from their configuration object to make them easier to test.
"""

# import modules not names inside so tests can mock functions
# inside these modules more easily
import os
from os import path
import ConfigParser
import shutil

from datacats import docker, validate, migrate
from datacats.error import DatacatsError
from datacats.cli.pull import retrying_pull_image


DEFAULT_REMOTE_SERVER_TARGET = 'datacats@command.datacats.com'


def list_sites(datadir):
    """
    Return a list of the site names valid for this environment
    """
    try:
        return os.listdir(datadir + '/sites')
    except OSError:
        return []


def save_new_site(site_name, sitedir, srcdir, port, address, site_url,
        passwords):
    """
    Add a site's configuration to the source dir and site dir
    """
    cp = ConfigParser.SafeConfigParser()
    cp.read([srcdir + '/.datacats-environment'])

    section_name = 'site_' + site_name

    if not cp.has_section(section_name):
        cp.add_section(section_name)
    cp.set(section_name, 'port', str(port))
    cp.set(section_name, 'address', address or '127.0.0.1')

    if site_url:
        cp.set(section_name, 'site_url', site_url)

    with open(srcdir + '/.datacats-environment', 'w') as config:
        cp.write(config)

    # save passwords to datadir
    cp = ConfigParser.SafeConfigParser()

    cp.add_section('passwords')
    for n in sorted(passwords):
        cp.set('passwords', n.lower(), passwords[n])

    # Write to the sitedir so we maintain separate passwords.
    with open(sitedir + '/passwords.ini', 'w') as config:
        cp.write(config)


def save_new_environment(name, datadir, srcdir, ckan_version,
        deploy_target=None, always_prod=False):
    """
    Save an environment's configuration to the source dir and data dir
    """
    with open(datadir + '/.version', 'w') as f:
        f.write('2')

    cp = ConfigParser.SafeConfigParser()

    cp.read(srcdir + '/.datacats-environment')

    if not cp.has_section('datacats'):
        cp.add_section('datacats')
    cp.set('datacats', 'name', name)
    cp.set('datacats', 'ckan_version', ckan_version)

    if deploy_target:
        if not cp.has_section('deploy'):
            cp.add_section('deploy')
        cp.set('deploy', 'target', deploy_target)

    if always_prod:
        cp.set('datacats', 'always_prod', 'true')

    with open(srcdir + '/.datacats-environment', 'w') as config:
        cp.write(config)

    save_srcdir_location(datadir, srcdir)


def save_srcdir_location(datadir, srcdir):
    """
    Store the location of srcdir in datadir/project-dir
    """
    # project-dir because backwards compatibility
    with open(datadir + '/project-dir', 'w') as pdir:
        pdir.write(srcdir)


def find_environment_dirs(environment_name=None, data_only=False):
    """
    :param environment_name: exising environment name, path or None to
        look in current or parent directories for project

    returns (srcdir, extension_dir, datadir)

    extension_dir is the  name of extension directory user was in/referenced,
    default: 'ckan'. This value is used by the paster cli command.

    datadir will be None if environment_name was a path or None (not a name)
    """
    docker.require_images()

    if environment_name is None:
        environment_name = '.'

    extension_dir = 'ckan'
    if validate.valid_name(environment_name) and path.isdir(
            path.expanduser('~/.datacats/' + environment_name)):
        # loading from a name
        datadir = path.expanduser('~/.datacats/' + environment_name)
        with open(datadir + '/project-dir') as pd:
            srcdir = pd.read()

        if not data_only and not path.exists(srcdir + '/.datacats-environment'):
            raise DatacatsError(
                'Environment data found but environment directory is'
                ' missing. Try again from the new environment directory'
                ' location or remove the environment data with'
                ' "datacats purge"')

        return srcdir, extension_dir, datadir

    # loading from a path
    srcdir = path.abspath(environment_name)
    if not path.isdir(srcdir):
        raise DatacatsError('No environment found with that name')

    wd = srcdir
    oldwd = None
    while not path.exists(wd + '/.datacats-environment'):
        oldwd = wd
        wd, _ = path.split(wd)
        if wd == oldwd:
            raise DatacatsError(
                'Environment not found in {0} or above'.format(srcdir))
    srcdir = wd

    if oldwd:
        _, extension_dir = path.split(oldwd)

    return srcdir, extension_dir, None


def load_environment(srcdir, datadir=None):
    """
    Load configuration values for an environment

    :param srcdir: environment source directory
    :param datadir: environment data direcory, if None will be discovered
                    from srcdir
    if datadir is None it will be discovered from srcdir

    Returns (datadir, name, ckan_version, always_prod, deploy_target,
             remote_server_key)
    """
    cp = ConfigParser.SafeConfigParser()
    try:
        cp.read([srcdir + '/.datacats-environment'])
    except ConfigParser.Error:
        raise DatacatsError('Error reading environment information')

    name = cp.get('datacats', 'name')

    if datadir:
        # update the link in case user moved their srcdir
        save_srcdir_location(datadir, srcdir)
    else:
        datadir = path.expanduser('~/.datacats/' + name)
        # FIXME: check if datadir is sane, project-dir points back to srcdir

    if migrate.needs_format_conversion(datadir):
        raise DatacatsError('This environment uses an old format. You must'
                            ' migrate to the new format. To do so, use the'
                            ' "datacats migrate" command.')

    if migrate.is_locked(datadir):
        raise DatacatsError('Migration in progress, cannot continue.\n'
                            'If you interrupted a migration, you should'
                            ' attempt manual recovery or contact us by'
                            ' filing an issue at http://github.com/datacats/'
                            'datacats.\nAs a last resort, you could delete'
                            ' all your stored data and create a new environment'
                            ' by running "datacats purge" followed by'
                            ' "datacats init".')

    # FIXME: consider doing data_complete check here

    ckan_version = cp.get('datacats', 'ckan_version')
    try:
        always_prod = cp.getboolean('datacats', 'always_prod')
    except ConfigParser.NoOptionError:
        always_prod = False

    try:
        extra_containers = cp.get('datacats', 'extra_containers').split(' ')
    except ConfigParser.NoOptionError:
        extra_containers = ()

    # if remote_server's custom ssh connection
    # address is defined,
    # we overwrite the default datacats.com one
    try:
        deploy_target = cp.get('deploy', 'remote_server_user') \
            + "@" + cp.get('deploy', 'remote_server')
    except (ConfigParser.NoOptionError, ConfigParser.NoSectionError):
        deploy_target = DEFAULT_REMOTE_SERVER_TARGET

    # if remote_server's ssh public key is given,
    # we overwrite the default datacats.com one
    try:
        remote_server_key = cp.get('deploy', 'remote_server_key')
    except (ConfigParser.NoOptionError, ConfigParser.NoSectionError):
        remote_server_key = None

    return (datadir, name, ckan_version, always_prod, deploy_target,
        remote_server_key, extra_containers)


def load_site(srcdir, datadir, site_name=None):
    """
    Load configuration values for a site.

    Returns (port, address, site_url, passwords)
    """
    if site_name is None:
        site_name = 'primary'
    if not validate.valid_name(site_name):
        raise DatacatsError('{} is not a valid site name.'.format(site_name))

    cp = ConfigParser.SafeConfigParser()
    try:
        cp.read([srcdir + '/.datacats-environment'])
    except ConfigParser.Error:
        raise DatacatsError('Error reading environment information')

    site_section = 'site_' + site_name
    try:
        port = cp.getint(site_section, 'port')
    except (ConfigParser.NoOptionError, ConfigParser.NoSectionError):
        port = None
    try:
        address = cp.get(site_section, 'address')
    except (ConfigParser.NoOptionError, ConfigParser.NoSectionError):
        address = None
    try:
        site_url = cp.get(site_section, 'site_url')
    except (ConfigParser.NoOptionError, ConfigParser.NoSectionError):
        site_url = None

    passwords = {}
    cp = ConfigParser.SafeConfigParser()
    cp.read(datadir + '/sites/' + site_name + '/passwords.ini')
    try:
        pw_options = cp.options('passwords')
    except ConfigParser.NoSectionError:
        pw_options = []

    for n in pw_options:
        passwords[n.upper()] = cp.get('passwords', n)

    return port, address, site_url, passwords


SUPPORTED_PRELOADS = ['2.3', '2.4', 'latest']


def new_environment_check(srcpath, site_name, ckan_version):
    """
    Check if a new environment or site can be created at the given path.

    Returns (name, datadir, sitedir, srcdir) or raises DatacatsError
    """
    docker.require_images()

    workdir, name = path.split(path.abspath(path.expanduser(srcpath)))

    if not validate.valid_name(name):
        raise DatacatsError('Please choose an environment name starting'
                            ' with a letter and including only lowercase letters'
                            ' and digits')
    if not path.isdir(workdir):
        raise DatacatsError('Parent directory for environment'
                            ' does not exist')

    datadir = path.expanduser('~/.datacats/' + name)
    sitedir = datadir + '/sites/' + site_name
    # We track through the datadir to the target if we are just making a
    # site
    if path.isdir(datadir):
        with open(datadir + '/project-dir') as pd:
            srcdir = pd.read()
    else:
        srcdir = workdir + '/' + name

    if ckan_version not in SUPPORTED_PRELOADS:
        raise DatacatsError('''Datacats does not currently support CKAN version {}.
Versions that are currently supported are: {}'''.format(ckan_version,
                                                        ', '.join(SUPPORTED_PRELOADS)))

    preload_name = str(ckan_version)

    # Get all the versions from the tags
    downloaded_versions = [tag for tag in docker.get_tags('datacats/ckan')]

    if ckan_version not in downloaded_versions:
        retrying_pull_image('datacats/ckan:{}'.format(preload_name))

    if path.isdir(sitedir):
        raise DatacatsError('Site data directory {0} already exists'.format(
                            sitedir))
    # This is the case where the data dir has been removed,
    if path.isdir(srcdir) and not path.isdir(datadir):
        raise DatacatsError('Environment directory exists, but data directory does not.\n'
                            'If you simply want to recreate the data directory, run '
                            '"datacats init" in the environment directory.')

    return name, datadir, srcdir


def data_complete(datadir, sitedir, get_container_name):
    """
    Return True if the directories and containers we're expecting
    are present in datadir, sitedir and containers
    """
    if any(not path.isdir(sitedir + x)
            for x in ('/files', '/run', '/solr')):
        return False

    if docker.is_boot2docker():
        # Inspect returns None if the container doesn't exist.
        return all(docker.inspect_container(get_container_name(x))
                for x in ('pgdata', 'venv'))

    return path.isdir(datadir + '/venv') and path.isdir(sitedir + '/postgres')


def source_missing(srcdir):
    """
    Return list of expected files missing from source directory srcdir
    """
    return [
        x for x in ('schema.xml', 'ckan', 'development.ini', 'who.ini')
        if not path.exists(srcdir + '/' + x)]


def create_directories(datadir, sitedir, srcdir=None):
    """
    Create expected directories in datadir, sitedir
    and optionally srcdir
    """
    # It's possible that the datadir already exists
    # (we're making a secondary site)
    if not path.isdir(datadir):
        os.makedirs(datadir, mode=0o700)
    try:
        # This should take care if the 'site' subdir if needed
        os.makedirs(sitedir, mode=0o700)
    except OSError:
        raise DatacatsError("Site already exists.")

    # venv isn't site-specific, the rest are.
    if not docker.is_boot2docker():
        if not path.isdir(datadir + '/venv'):
            os.makedirs(datadir + '/venv')
        os.makedirs(sitedir + '/postgres')
    os.makedirs(sitedir + '/solr')
    os.makedirs(sitedir + '/files')
    os.makedirs(sitedir + '/run')

    if srcdir:
        os.makedirs(srcdir)


def create_virtualenv(srcdir, datadir, preload_image, get_container_name):
    """
    Populate venv from preloaded image
    """
    try:
        if docker.is_boot2docker():
            docker.data_only_container(
                get_container_name('venv'),
                ['/usr/lib/ckan'],
                )
            img_id = docker.web_command(
                '/bin/mv /usr/lib/ckan/ /usr/lib/ckan_original',
                image=preload_image,
                commit=True,
                )
            docker.web_command(
                command='/bin/cp -a /usr/lib/ckan_original/. /usr/lib/ckan/.',
                volumes_from=get_container_name('venv'),
                image=img_id,
                )
            docker.remove_image(img_id)
            return

        docker.web_command(
            command='/bin/cp -a /usr/lib/ckan/. /usr/lib/ckan_target/.',
            rw={datadir + '/venv': '/usr/lib/ckan_target'},
            image=preload_image,
            )
    finally:
        rw = {datadir + '/venv': '/usr/lib/ckan'} if not docker.is_boot2docker() else {}
        volumes_from = get_container_name('venv') if docker.is_boot2docker() else None
        # fix venv permissions
        docker.web_command(
            command='/bin/chown -R --reference=/project /usr/lib/ckan',
            rw=rw,
            volumes_from=volumes_from,
            ro={srcdir: '/project'},
            )


def create_source(srcdir, preload_image, datapusher=False):
    """
    Copy ckan source, datapusher source (optional), who.ini and schema.xml
    from preload image into srcdir
    """
    try:
        docker.web_command(
            command='/bin/cp -a /project/ckan /project_target/ckan',
            rw={srcdir: '/project_target'},
            image=preload_image)
        if datapusher:
            docker.web_command(
                command='/bin/cp -a /project/datapusher /project_target/datapusher',
                rw={srcdir: '/project_target'},
                image=preload_image)
        shutil.copy(
            srcdir + '/ckan/ckan/config/who.ini',
            srcdir)
        shutil.copy(
            srcdir + '/ckan/ckan/config/solr/schema.xml',
            srcdir)
    finally:
        # fix srcdir permissions
        docker.web_command(
            command='/bin/chown -R --reference=/project /project',
            rw={srcdir: '/project'},
            )


# Maps container extra names to actual names
EXTRA_IMAGE_MAPPING = {'redis': 'redis'}


def start_supporting_containers(sitedir, srcdir, passwords,
        get_container_name, extra_containers, log_syslog=False):
    """
    Start all supporting containers (containers required for CKAN to
    operate) if they aren't already running, along with some extra
    containers specified by the user
    """
    if docker.is_boot2docker():
        docker.data_only_container(get_container_name('pgdata'),
            ['/var/lib/postgresql/data'])
        rw = {}
        volumes_from = get_container_name('pgdata')
    else:
        rw = {sitedir + '/postgres': '/var/lib/postgresql/data'}
        volumes_from = None

    running = set(containers_running(get_container_name))

    needed = set(extra_containers).union({'postgres', 'solr'})

    if not needed.issubset(running):
        stop_supporting_containers(get_container_name, extra_containers)

        # users are created when data dir is blank so we must pass
        # all the user passwords as environment vars
        # XXX: postgres entrypoint magic
        docker.run_container(
            name=get_container_name('postgres'),
            image='datacats/postgres',
            environment=passwords,
            rw=rw,
            volumes_from=volumes_from,
            log_syslog=log_syslog)

        docker.run_container(
            name=get_container_name('solr'),
            image='datacats/solr',
            rw={sitedir + '/solr': '/var/lib/solr'},
            ro={srcdir + '/schema.xml': '/etc/solr/conf/schema.xml'},
            log_syslog=log_syslog)

        for container in extra_containers:
            # We don't know a whole lot about the extra containers so we're just gonna have to
            # mount /project and /datadir r/o even if they're not needed for ease of
            # implementation.
            docker.run_container(
                name=get_container_name(container),
                image=EXTRA_IMAGE_MAPPING[container],
                ro={
                    sitedir: '/datadir',
                    srcdir: '/project'
                },
                log_syslog=log_syslog
            )


def stop_supporting_containers(get_container_name, extra_containers):
    """
    Stop postgres and solr containers, along with any specified extra containers
    """
    docker.remove_container(get_container_name('postgres'))
    docker.remove_container(get_container_name('solr'))
    for container in extra_containers:
        docker.remove_container(get_container_name(container))


def containers_running(get_container_name):
    """
    Return a list of containers tracked by this environment that are running
    """
    running = []
    for n in ['web', 'postgres', 'solr', 'datapusher', 'redis']:
        info = docker.inspect_container(get_container_name(n))
        if info and not info['State']['Running']:
            running.append(n + '(halted)')
        elif info:
            running.append(n)
    return running
