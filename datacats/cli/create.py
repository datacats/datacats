# Copyright 2014-2015 Boxkite Inc.

# This file is part of the DataCats package and is released under
# the terms of the GNU Affero General Public License version 3.0.
# See LICENSE.txt or http://www.fsf.org/licensing/licenses/agpl-3.0.html

import sys
from os.path import abspath
from getpass import getpass

from datacats.environment import Environment
from datacats.cli.install import install_all
from datacats.validate import valid_deploy_name


def write(s):
    sys.stdout.write(s)
    sys.stdout.flush()


def create(opts):
    """Create a new environment

Usage:
  datacats create [-bni] [--address=IP] [--syslog] [--ckan=CKAN_VERSION] ENVIRONMENT_DIR [PORT]

Options:
  --address=IP            Address to listen on (Linux-only) [default: 127.0.0.1]
  --ckan=CKAN_VERSION     Use CKAN version CKAN_VERSION, defaults to
                          latest development release
  -b --bare               Bare CKAN site with no example extension
  -i --image-only         Create the environment but don't start containers
  -n --no-sysadmin        Don't prompt for an initial sysadmin user account
  --syslog                Log to the syslog

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
        address=opts['--address'],
        log_syslog=opts['--syslog']
        )


def create_environment(environment_dir, port, ckan_version, create_skin,
        start_web, create_sysadmin, address, log_syslog=False):

    # FIXME: only 2.3 preload supported at the moment
    environment = Environment.new(environment_dir, '2.3', port=port)

    try:
        if not valid_deploy_name(environment.name):
            print "WARNING: When deploying you will need to choose a"
            print "target name that is at least 5 characters long"
            print

        write('Creating environment "{0}"'.format(environment.name))
        steps = [
            environment.create_directories,
            environment.create_bash_profile,
            environment.save,
            environment.create_virtualenv,
            environment.create_source,
            environment.start_postgres_and_solr,
            environment.fix_storage_permissions,
            environment.create_ckan_ini,
            lambda: environment.update_ckan_ini(skin=create_skin),
            environment.fix_project_permissions,
            ]

        if create_skin:
            steps.append(environment.create_install_template_skin)

        steps.append(environment.ckan_db_init)

        for fn in steps:
            fn()
            write('.')
        write('\n')

        return finish_init(environment, start_web, create_sysadmin, address, log_syslog=log_syslog)
    except:
        # Make sure that it doesn't get printed right after the dots
        # by printing a newline
        # i.e. Creating environment 'hello'.....ERROR MESSAGE
        print
        raise


def init(opts):
    """Initialize a purged environment or copied environment directory

Usage:
  datacats init [-ni] [--syslog] [--address=IP] [ENVIRONMENT_DIR [PORT]]

Options:
  --address=IP            Address to listen on (Linux-only) [default: 127.0.0.1]
  -i --image-only         Create the environment but don't start containers
  -n --no-sysadmin        Don't prompt for an initial sysadmin user account
  --syslog                Log to the syslog

ENVIRONMENT_DIR is an existing datacats environment directory. Defaults to '.'
"""
    environment_dir = opts['ENVIRONMENT_DIR']
    port = opts['PORT']
    address = opts['--address']
    start_web = not opts['--image-only']
    create_sysadmin = not opts['--no-sysadmin']
    environment_dir = abspath(environment_dir or '.')
    log_syslog = opts['--syslog']

    environment = Environment.load(environment_dir)
    environment.address = address
    if port:
        environment.port = int(port)

    try:
        write('Creating from existing environment directory "{0}"'.format(
            environment.name))
        steps = [
            lambda: environment.create_directories(create_project_dir=False),
            environment.save,
            environment.create_virtualenv,
            environment.start_postgres_and_solr,
            environment.fix_storage_permissions,
            environment.fix_project_permissions,
            ]

        for fn in steps:
            fn()
            write('.')
        write('\n')
    except:
        print
        raise

    return finish_init(environment, start_web, create_sysadmin, address, log_syslog=log_syslog)


def finish_init(environment, start_web, create_sysadmin, address, log_syslog=False):
    """
    Common parts of create and init: Install, init db, start site, sysadmin
    """
    install_all(environment, False, verbose=False)

    write('Initializing database')
    environment.ckan_db_init()
    write('\n')

    if start_web:
        environment.start_web(address=address, log_syslog=log_syslog)
        write('Starting web server at {0} ...\n'.format(
            environment.web_address()))

    if create_sysadmin:
        try:
            adminpw = confirm_password()
            environment.create_admin_set_password(adminpw)
        except KeyboardInterrupt:
            print

    if not start_web:
        environment.stop_postgres_and_solr()


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
