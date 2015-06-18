# Copyright 2014-2015 Boxkite Inc.
# This file is part of the DataCats package and is released under
# the terms of the GNU Affero General Public License version 3.0.
# See LICENSE.txt or http://www.fsf.org/licensing/licenses/agpl-3.0.html

from os import makedirs
import os
from os.path import isdir, exists, join as path_join, split as path_split
from ConfigParser import SafeConfigParser
import sys

from lockfile import LockFile

from datacats.docker import (is_boot2docker, remove_container,
                             rename_container, web_command,
                             inspect_container, require_images)
from datacats.scripts import MIGRATE
from datacats.password import generate_password
from datacats.error import DatacatsError

CURRENT_FORMAT_VERSION = 2


def _get_current_format(datadir):
    if not exists(path_join(datadir, '.version')):
        # Format v1 didn't have a .version file.
        return 1

    with open(path_join(datadir, '.version')) as version_file:
        return int(version_file.read())


def needs_format_conversion(datadir, version=CURRENT_FORMAT_VERSION):
    """
    Returns True if `datadir` requires conversion to format version specified by `version`

    :param datadir: The datadir to convert.
    :param version: The version to convert TO.
    """
    return isdir(datadir) and version != _get_current_format(datadir)


def _split_path(path):
    """
    A wrapper around the normal split function that ignores any trailing /.

    :return: A tuple of the form (dirname, last) where last is the last element
             in the path.
    """
    # Get around a quirk in path_split where a / at the end will make the
    # dirname (split[0]) the entire path
    path = path[:-1] if path[-1] == '/' else path
    split = path_split(path)
    return split


def _one_to_two(datadir):
    """After this command, your environment will be converted to format version {}.
and will only work with datacats version exceeding and including 1.0.0.
This migration is necessary to support multiple sites within the same environment.
Your current site will be kept and will be named "primary".

Would you like to continue the migration? (y/n) [n]:"""
    new_site_name = 'primary'

    split = _split_path(datadir)

    print 'Making sure that containers are stopped...'
    env_name = split[1]
    # Old-style names on purpose! We need to stop old containers!
    remove_container('datacats_web_' + env_name)
    remove_container('datacats_solr_' + env_name)
    remove_container('datacats_postgres_' + env_name)

    print 'Doing conversion...'
    # Begin the actual conversion
    to_move = (['files', 'passwords.ini', 'run', 'solr'] +
               (['postgres'] if not is_boot2docker() else []))
    # Make a primary site
    site_path = path_join(datadir, 'sites', new_site_name)
    if not exists(site_path):
        makedirs(site_path)

    web_command(
        command=['/scripts/migrate.sh',
                 '/project/data',
                 '/project/data/sites/' + new_site_name] +
        to_move,
        ro={MIGRATE: '/scripts/migrate.sh'},
        rw={datadir: '/project/data'},
        clean_up=True
        )

    if is_boot2docker():
        rename_container('datacats_pgdata_' + env_name,
                         'datacats_pgdata_' + env_name + '_' + new_site_name)

    # Lastly, grab the project directory and update the ini file
    with open(path_join(datadir, 'project-dir')) as pd:
        project = pd.read()

    cp = SafeConfigParser()
    config_loc = path_join(project, '.datacats-environment')
    cp.read([config_loc])

    new_section = 'site_' + new_site_name
    cp.add_section(new_section)

    # Ports need to be moved into the new section
    port = cp.get('datacats', 'port')
    cp.remove_option('datacats', 'port')

    cp.set(new_section, 'port', port)

    with open(config_loc, 'w') as config:
        cp.write(config)

    # Make a session secret for it (make it per-site)
    cp = SafeConfigParser()
    config_loc = path_join(site_path, 'passwords.ini')
    cp.read([config_loc])

    # Generate a new secret
    cp.set('passwords', 'beaker_session_secret', generate_password())

    with open(config_loc, 'w') as config:
        cp.write(config)

    with open(path_join(datadir, '.version'), 'w') as f:
        f.write('2')


def _two_to_one(datadir):
    """After this command, your environment will be converted to format version {}
and will not work with Datacats versions beyond and including 1.0.0.
This format version doesn't support multiple sites, and after this only your
"primary" site will be usable, though other sites will be maintained if you
wish to do a migration back to a version which supports multisite.

Would you like to continue the migration? (y/n) [n]:"""
    _, env_name = _split_path(datadir)

    print 'Making sure that containers are stopped...'
    # New-style names
    remove_container('datacats_web_{}_primary'.format(env_name))
    remove_container('datacats_postgres_{}_primary'.format(env_name))
    remove_container('datacats_solr_{}_primary'.format(env_name))

    print 'Doing conversion...'

    if exists(path_join(datadir, '.version')):
        os.remove(path_join(datadir, '.version'))

    to_move = (['files', 'passwords.ini', 'run', 'solr'] +
               (['postgres'] if not is_boot2docker() else []))

    web_command(
        command=['/scripts/migrate.sh',
                 '/project/data/sites/primary',
                 '/project/data'] + to_move,
        ro={MIGRATE: '/scripts/migrate.sh'},
        rw={datadir: '/project/data'}
    )

    pgdata_name = 'datacats_pgdata_{}_primary'.format(env_name)
    if is_boot2docker() and inspect_container(pgdata_name):
        rename_container(pgdata_name, 'datacats_pgdata_{}'.format(env_name))

    print 'Doing cleanup...'
    with open(path_join(datadir, 'project-dir')) as pd:
        datacats_env_location = path_join(pd.read(), '.datacats-environment')

    cp = SafeConfigParser()
    cp.read(datacats_env_location)

    # We need to move the port OUT of site_primary section and INTO datacats
    cp.set('datacats', 'port', cp.get('site_primary', 'port'))
    cp.remove_section('site_primary')

    with open(datacats_env_location, 'w') as config:
        cp.write(config)

    cp = SafeConfigParser()
    cp.read(path_join(datadir, 'passwords.ini'))

    # This isn't needed in this version
    cp.remove_option('passwords', 'beaker_session_secret')

    with open(path_join(datadir, 'passwords.ini'), 'w') as config:
        cp.write(config)


migrations = {
    (1, 2): _one_to_two,
    (2, 1): _two_to_one
    }


def convert_environment(datadir, version, always_yes):
    """
    Converts an environment TO the version specified by `version`.
    :param datadir: The datadir to convert.
    :param version: The version to convert TO.
    :param always_yes: True if the user shouldn't be prompted about the migration.
    """
    # Since we don't call either load() or new() we have to call require_images ourselves.
    require_images()

    inp = None
    old_version = _get_current_format(datadir)
    migration_func = migrations[(old_version, version)]

    if version > CURRENT_FORMAT_VERSION:
        raise DatacatsError('Cannot migrate to a version higher than the '
                            'current one.')
    if version < 1:
        raise DatacatsError('Datadir versioning starts at 1.')

    if not always_yes:
        while inp != 'y' and inp != 'n':
            inp = raw_input(migration_func.__doc__.format(version))

        if inp == 'n':
            sys.exit(1)

    lockfile = LockFile(path_join(datadir, '.migration_lock'))
    lockfile.acquire()

    try:
        # FIXME: If we wanted to, we could find a set of conversions which
        # would bring us up to the one we want if there's no direct path.
        # This isn't necessary with just two formats, but it may be useful
        # at 3.
        # Call the appropriate conversion function
        migration_func(datadir)
    finally:
        lockfile.release()


def is_locked(datadir):
    """
    Return True if this datadir is locked for migrations
    """
    lockfile = LockFile(datadir + '/.migration_lock')
    return lockfile.is_locked()
