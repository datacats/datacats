# Copyright 2014-2015 Boxkite Inc.
# This file is part of the DataCats package and is released under
# the terms of the GNU Affero General Public License version 3.0.
# See LICENSE.txt or http://www.fsf.org/licensing/licenses/agpl-3.0.html

from os import makedirs
from os.path import isdir, exists, join as path_join, split as path_split
from datacats.docker import is_boot2docker, remove_container
from ConfigParser import SafeConfigParser
import shutil


def needs_format_conversion(datadir):
    """
    Returns True if `datadir` requires conversion to the child env format.
    """
    return (isdir(datadir) and isdir(path_join(datadir, 'run')) and
            exists(path_join(datadir, 'passwords.ini')) and
            exists(path_join(datadir, 'search')) and
            exists(path_join(datadir, 'solr')) and
            exists(path_join(datadir, 'project-dir')))


def convert_environment(datadir):
    new_child_name = 'primary'
    inp = None

    while inp != 'y' and inp != 'n':
        inp = raw_input('You are using a file in the old DataCats format. '
                        'Would you like to convert it (y/n) [n]: ')

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

    backup_loc = path_join(path_split(datadir)[0], split[1] + '.bak')

    print 'Making a backup at {}...'.format(backup_loc)

    if exists(backup_loc):
        # Remove any old backups
        shutil.rmtree(backup_loc)
    # Make a backup of the current version
    shutil.copytree(datadir, backup_loc)

    # Begin the actual conversion
    to_move = ['files', 'passwords.ini', 'run', 'search', 'solr'] + [
                'postgres', 'venv'] if not is_boot2docker() else []
    # Make a primary child
    child_path = path_join(datadir, 'primary')
    makedirs(child_path)

    print 'Doing conversion...'
    for directory in to_move:
        shutil.move(path_join(datadir, directory), path_join(child_path,
                                                             directory))

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

    cp.set('passwords', 'beaker_session_secret', generate_password())

    with open(config_loc, 'w') as config:
        cp.write(config)
