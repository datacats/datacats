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
    """Create a new project

Usage:
  datacats create PROJECT_DIR [PORT] [-bin] [--ckan=CKAN_VERSION]

Options:
  --ckan=CKAN_VERSION     Use CKAN version CKAN_VERSION, defaults to
                          latest development release
  -b --bare               Bare CKAN site with no example extension
  -i --image-only         Create the project but don't start containers
  -n --no-sysadmin        Don't prompt for an initial sysadmin user account

PROJECT_DIR is a path for the new project directory.
"""
    project_dir = opts['PROJECT_DIR']
    port = opts['PORT']
    bare = opts['--bare']
    image_only = opts['--image-only']
    no_sysadmin = opts['--no-sysadmin']
    ckan = opts['--ckan']

    try:
        project = Project.new(project_dir, 'master', port)
    except ProjectError as e:
        print e
        return 1

    write('Creating project "{0}"'.format(project.name))
    steps = [
        project.create_directories,
        project.create_bash_profile,
        project.save,
        project.create_virtualenv,
        project.create_source,
        project.start_data_and_search,
        project.fix_storage_permissions,
        project.create_ckan_ini,
        lambda: project.update_ckan_ini(skin=not bare),
        project.fix_project_permissions,
        ]

    if not bare:
        steps.append(project.create_install_template_skin)

    steps.append(project.ckan_db_init)

    for fn in steps:
        fn()
        write('.')
    write('\n')

    return finish_init(project, image_only, no_sysadmin)


def init(opts):
    """Initialize a purged project or copied project directory

Usage:
  datacats init [PROJECT_DIR [PORT]] [-in]

Options:
  -i --image-only         Create the project but don't start containers
  -n --no-sysadmin        Don't prompt for an initial sysadmin user account

PROJECT_DIR is an existing project directory. Defaults to '.'
"""
    project_dir = opts['PROJECT_DIR']
    port = opts['PORT']
    image_only = opts['--image-only']
    no_sysadmin = opts['--no-sysadmin']

    project_dir = abspath(project_dir or '.')
    try:
        project = Project.load(project_dir)
        if port:
            project.port = int(port)
    except ProjectError as e:
        print e
        return 1

    write('Creating from existing project "{0}"'.format(project.name))
    steps = [
        lambda: project.create_directories(create_project_dir=False),
        project.save,
        project.create_virtualenv,
        project.start_data_and_search,
        project.fix_storage_permissions,
        project.fix_project_permissions,
        ]

    for fn in steps:
        fn()
        write('.')
    write('\n')

    return finish_init(project, image_only, no_sysadmin)


def finish_init(project, image_only, no_sysadmin):
    """
    Common parts of create and init: Install, init db, start site, sysadmin
    """
    install(project, {'--clean': False, 'PORT': None})

    write('Initializing database')
    project.ckan_db_init()
    write('\n')

    if not image_only:
        project.start_web()
        write('Site available at {0}\n'.format(project.web_address()))

    if not no_sysadmin:
        try:
            adminpw = confirm_password()
            project.create_admin_set_password(adminpw)
        except KeyboardInterrupt:
            print

    if image_only:
        project.stop_data_and_search()


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
