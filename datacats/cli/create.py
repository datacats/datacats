# Copyright 2014-2015 Boxkite Inc.

# This file is part of the DataCats package and is released under
# the terms of the GNU Affero General Public License version 3.0.
# See LICENSE.txt or http://www.fsf.org/licensing/licenses/agpl-3.0.html

import sys
from os.path import exists, abspath
from getpass import getpass

from datacats.project import Project, ProjectError
from datacats.cli.install import install

def write(s):
    sys.stdout.write(s)
    sys.stdout.flush()

def create(opts):
    """Create a new environment

Usage:
  datacats create [-bin] [--ckan=CKAN_VERSION] ENVIRONMENT_DIR [PORT]

Options:
  --ckan=CKAN_VERSION     Use CKAN version CKAN_VERSION, defaults to
                          latest development release
  -b --bare               Bare CKAN site with no example extension
  -i --image-only         Create the environment but don't start containers
  -n --no-sysadmin        Don't prompt for an initial sysadmin user account

ENVIRONMENT_DIR is a path for the new environment directory. The last
part of this path will be used as the environment name.
"""
    return create_environment(
        environment_dir=opts['ENVIRONMENT_DIR'],
        port=opts['PORT'],
        create_skin=not opts['--bare'],
        start_web=not opts['--image-only'],
        create_sysadmin=not opts['--no-sysadmin'],
        ckan_version=opts['--ckan'],
        )

def create_environment(environment_dir, port, ckan_version, create_skin,
        start_web, create_sysadmin):
    try:
        # FIXME: only 2.3 preload supported at the moment
        project = Project.new(environment_dir, '2.3', port)
    except ProjectError as e:
        print e
        return 1

    write('Creating environment "{0}"'.format(project.name))
    steps = [
        project.create_directories,
        project.create_bash_profile,
        project.save,
        project.create_virtualenv,
        project.create_source,
        project.start_postgres_and_solr,
        project.fix_storage_permissions,
        project.create_ckan_ini,
        lambda: project.update_ckan_ini(skin=create_skin),
        project.fix_project_permissions,
        ]

    if create_skin:
        steps.append(project.create_install_template_skin)

    steps.append(project.ckan_db_init)

    for fn in steps:
        fn()
        write('.')
    write('\n')

    return finish_init(project, start_web, create_sysadmin)


def init(opts):
    """Initialize a purged environment or copied environment directory

Usage:
  datacats init [-in] [ENVIRONMENT_DIR [PORT]]

Options:
  -i --image-only         Create the environment but don't start containers
  -n --no-sysadmin        Don't prompt for an initial sysadmin user account

ENVIRONMENT_DIR is an existing datacats environment directory. Defaults to '.'
"""
    project_dir = opts['ENVIRONMENT_DIR']
    port = opts['PORT']
    start_web = not opts['--image-only']
    create_sysadmin = not opts['--no-sysadmin']

    project_dir = abspath(project_dir or '.')
    try:
        project = Project.load(project_dir)
        if port:
            project.port = int(port)
    except ProjectError as e:
        print e
        return 1

    write('Creating from existing environment directory "{0}"'.format(
        project.name))
    steps = [
        lambda: project.create_directories(create_project_dir=False),
        project.save,
        project.create_virtualenv,
        project.start_postgres_and_solr,
        project.fix_storage_permissions,
        project.fix_project_permissions,
        ]

    for fn in steps:
        fn()
        write('.')
    write('\n')

    return finish_init(project, start_web, create_sysadmin)


def finish_init(project, start_web, create_sysadmin):
    """
    Common parts of create and init: Install, init db, start site, sysadmin
    """
    install(project, {'--clean': False, 'PORT': None})

    write('Initializing database')
    project.ckan_db_init()
    write('\n')

    if start_web:
        project.start_web()
        write('Starting web server at {0} ...\n'.format(project.web_address()))

    if create_sysadmin:
        try:
            adminpw = confirm_password()
            project.create_admin_set_password(adminpw)
        except KeyboardInterrupt:
            print

    if not start_web:
        project.stop_postgres_and_solr()


def confirm_password():
    while True:
        p1 = getpass('admin user password:')
        if len(p1) < 4:
            print 'At least 4 characters are required'
            continue
        p2 = getpass('confirm password:')
        if p1 == p2:
            return p1
        print 'Passwords do not match'
