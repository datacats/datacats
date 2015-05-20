# Copyright 2014-2015 Boxkite Inc.
# This file is part of the DataCats package and is released under
# the terms of the GNU Affero General Public License version 3.0.
# See LICENSE.txt or http://www.fsf.org/licensing/licenses/agpl-3.0.html

from os import makedirs
from os.path import isdir, exists, join as path_join, split as path_split
from ConfigParser import SafeConfigParser
import sys

from lockfile import LockFile

from datacats.docker import (is_boot2docker, remove_container,
                             rename_container, web_command)
from datacats.scripts import MIGRATE
from datacats.password import generate_password


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

def _one_to_two(datadir):
    new_child_name = 'primary'
    # Get around a quirk in path_split where a / at the end will make the
    # dirname (split[0]) the entire path
    datadir = datadir[:-1] if datadir[-1] == '/' else datadir
    split = path_split(datadir)

    print 'Making sure that containers are stopped...'
    env_name = split[1]
    # Old-style names on purpose! We need to stop old containers!
    remove_container('datacats_web_' + env_name)
    remove_container('datacats_solr_' + env_name)
    remove_container('datacats_postgres_' + env_name)

    print 'Doing conversion...'
    # Begin the actual conversion
    to_move = (['files', 'passwords.ini', 'run', 'solr', 'search'] +
               (['postgres', 'data'] if not is_boot2docker() else []))
    # Make a primary child
    child_path = path_join(datadir, 'children', new_child_name)
    makedirs(child_path)

    web_command(
        command=['/scripts/migrate.sh',
                 '/project/data',
                 '/project/data/children/' + new_child_name] +
        to_move,
        ro={MIGRATE: '/scripts/migrate.sh'},
        rw={datadir: '/project/data'},
        clean_up=True
        )

    if is_boot2docker():
        rename_container('datacats_pgdata_' + env_name,
                         'datacats_pgdata_' + env_name + '_' + new_child_name)

    with open(path_join(datadir, '.version'), 'w') as f:
        # Version 2
        f.write('2')

    # Lastly, grab the project directory and update the ini file
    with open(path_join(datadir, 'project-dir')) as pd:
        project = pd.read()

    cp = SafeConfigParser()
    config_loc = path_join(project, '.datacats-environment')
    cp.read([config_loc])

    new_section = 'child_' + new_child_name
    cp.add_section('child_' + new_child_name)

    # Ports need to be moved into the new section
    port = cp.get('datacats', 'port')
    cp.remove_option('datacats', 'port')

    cp.set(new_section, 'port', port)

    with open(config_loc, 'w') as config:
        cp.write(config)

    # Make a session secret for it (make it per-child)
    cp = SafeConfigParser()
    config_loc = path_join(child_path, 'passwords.ini')
    cp.read([config_loc])

    # Grab the secret from config
    # Find the project-dir
    with open(datadir + '/project-dir') as pd:
        dev_ini_loc = path_join(pd.read(), 'development.ini')
    dev_ini_cp = SafeConfigParser()
    dev_ini_cp.read(dev_ini_loc)

    cp.set('passwords', 'beaker_session_secret', generate_password())

    with open(config_loc, 'w') as config:
        cp.write(config)

migrations = {
    (1,2): _one_to_two
    }

def convert_environment(datadir, version, always_yes):
    """
    Converts an environment TO the version specified by `version`.
    :param datadir: The datadir to convert.
    :param version: The version to convert TO.
    :param always_yes: True if the user shouldn't be prompted about the migration.
    """
    inp = None

    if not always_yes:
        while inp != 'y' and inp != 'n':
            inp = raw_input('This migration will change the format of your datadir.'
                            ' Are you sure? (y/n) [n]: ')

        if inp == 'n':
            sys.exit(1)

    lockfile = LockFile(path_join(datadir, '.migration_lock'))
    lockfile.acquire()

    try:
        # Call the appropriate conversion function
        migrations[(_get_current_format(datadir), version)](datadir)
    finally:
        lockfile.release()
