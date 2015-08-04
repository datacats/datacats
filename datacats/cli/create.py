# Copyright 2014-2015 Boxkite Inc.

# This file is part of the DataCats package and is released under
# the terms of the GNU Affero General Public License version 3.0.
# See LICENSE.txt or http://www.fsf.org/licensing/licenses/agpl-3.0.html

import sys
from os.path import abspath

from datacats.environment import Environment
from datacats.cli.install import install_all
from datacats.error import DatacatsError

from datacats.cli.util import y_or_n_prompt, confirm_password


def write(s):
    sys.stdout.write(s)
    sys.stdout.flush()


def create(opts):
    """Create a new environment

Usage:
  datacats create [-bin] [--interactive] [-s NAME] [--address=IP] [--syslog] [--ckan=CKAN_VERSION]
                  [--no-datapusher] [--site-url SITE_URL] ENVIRONMENT_DIR [PORT]

Options:
  --address=IP            Address to listen on (Linux-only) [default: 127.0.0.1]
  --ckan=CKAN_VERSION     Use CKAN version CKAN_VERSION [default: 2.3]
  -b --bare               Bare CKAN site with no example extension
  -i --image-only         Create the environment but don't start containers
  --interactive           Doesn't detach from the web container
  -n --no-sysadmin        Don't prompt for an initial sysadmin user account
  -s --site=NAME          Pick a site to create [default: primary]
  --no-datapusher         Don't install/enable ckanext-datapusher
  --site-url SITE_URL     The site_url to use in API responses (e.g. http://example.org:{port}/)
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
        site_name=opts['--site'],
        ckan_version=opts['--ckan'],
        address=opts['--address'],
        log_syslog=opts['--syslog'],
        datapusher=not opts['--no-datapusher'],
        site_url=opts['--site-url'],
        interactive=opts['--interactive'],
        )


def create_environment(environment_dir, port, ckan_version, create_skin,
        site_name, start_web, create_sysadmin, address, log_syslog=False,
        datapusher=True, quiet=False, site_url=None, interactive=False):
    environment = Environment.new(environment_dir, ckan_version, site_name,
                                  address=address, port=port)

    try:
        # There are a lot of steps we can/must skip if we're making a sub-site only
        making_full_environment = not environment.data_exists()

        if not quiet:
            write('Creating environment "{0}/{1}"'.format(environment.name, environment.site_name))
        steps = [
            lambda: environment.create_directories(making_full_environment),
            environment.create_bash_profile
            ] + \
            ([
                environment.create_virtualenv,
                environment.save,
                lambda: environment.create_source(datapusher),
                environment.create_ckan_ini] if making_full_environment else []
            ) + \
            [
                environment.save_site,
                environment.start_supporting_containers,
                environment.fix_storage_permissions,
                lambda: environment.update_ckan_ini(skin=create_skin),
            ]

        if create_skin and making_full_environment:
            steps.append(environment.create_install_template_skin)

        for fn in steps:
            fn()
            if not quiet:
                write('.')
        if not quiet:
            write('\n')

        return finish_init(environment, start_web, create_sysadmin, address,
                           log_syslog=log_syslog, site_url=site_url,
                           interactive=interactive)
    except:
        # Make sure that it doesn't get printed right after the dots
        # by printing a newline
        # i.e. Creating environment 'hello'.....ERROR MESSAGE
        if not quiet:
            print
        raise


def reset(environment, opts):
    """Resets a site to the default state. This will re-initialize the
database and recreate the administrator account.

Usage:
  datacats reset [-iyn] [-s NAME] [ENVIRONMENT]

Options:
  -i --interactive        Don't detach from the web container
  -s --site=NAME          The site to reset [default: primary]
  -y --yes                Respond yes to all questions
  -n --no-sysadmin        Don't prompt for a sysadmin password"""
    # pylint: disable=unused-argument
    if not opts['--yes']:
        y_or_n_prompt('Reset will remove all data related to the '
                      'site {} and recreate the database'.format(opts['--site']))

    print 'Resetting...'
    environment.stop_supporting_containers()
    environment.stop_ckan()
    environment.purge_data([opts['--site']], never_delete=True)
    init({
        'ENVIRONMENT_DIR': opts['ENVIRONMENT'],
        '--site': opts['--site'],
        'PORT': None,
        '--syslog': None,
        '--address': '127.0.0.1',
        '--image-only': False,
        '--interactive': opts['--interactive'],
        '--no-sysadmin': opts['--no-sysadmin'],
        '--site-url': None
        }, no_install=True)


def init(opts, no_install=False, quiet=False):
    """Initialize a purged environment or copied environment directory

Usage:
  datacats init [-in] [--syslog] [-s NAME] [--address=IP] [--interactive]
                [--site-url SITE_URL] [ENVIRONMENT_DIR [PORT]]

Options:
  --address=IP            Address to listen on (Linux-only) [default: 127.0.0.1]
  --interactive           Don't detach from the web container
  -i --image-only         Create the environment but don't start containers
  -n --no-sysadmin        Don't prompt for an initial sysadmin user account
  -s --site=NAME          Pick a site to initialize [default: primary]
  --site-url SITE_URL     The site_url to use in API responses (e.g. http://example.org:{port}/)
  --syslog                Log to the syslog

ENVIRONMENT_DIR is an existing datacats environment directory. Defaults to '.'
"""
    environment_dir = opts['ENVIRONMENT_DIR']
    port = opts['PORT']
    address = opts['--address']
    start_web = not opts['--image-only']
    create_sysadmin = not opts['--no-sysadmin']
    site_name = opts['--site']
    site_url = opts['--site-url']
    interactive = opts['--interactive']

    environment_dir = abspath(environment_dir or '.')
    log_syslog = opts['--syslog']

    environment = Environment.load(environment_dir, site_name)
    environment.address = address
    if port:
        environment.port = int(port)
    if site_url:
        environment.site_url = site_url

    try:
        if environment.sites and site_name in environment.sites:
            raise DatacatsError('Site named {0} already exists.'
                                .format(site_name))
        # There are a couple of steps we can/must skip if we're making a sub-site only
        making_full_environment = not environment.data_exists()

        if not quiet:
            write('Creating environment {0}/{1} '
                  'from existing environment directory "{0}"'
                  .format(environment.name, environment.site_name))
        steps = [
            lambda: environment.create_directories(create_project_dir=False)] + ([
             environment.save,
             environment.create_virtualenv
             ] if making_full_environment else []) + [
                 environment.save_site,
                 environment.start_supporting_containers,
                 environment.fix_storage_permissions,
            ]

        for fn in steps:
            fn()
            if not quiet:
                write('.')
        if not quiet:
            write('\n')
    except:
        if not quiet:
            print
        raise

    return finish_init(environment, start_web, create_sysadmin, address,
                       log_syslog=log_syslog, do_install=not no_install,
                       quiet=quiet, site_url=site_url, interactive=interactive)


def finish_init(environment, start_web, create_sysadmin, address, log_syslog=False,
                do_install=True, quiet=False, site_url=None, interactive=False):
    """
    Common parts of create and init: Install, init db, start site, sysadmin
    """
    if do_install:
        install_all(environment, False, verbose=False, quiet=quiet)

    if not quiet:
        write('Initializing database')
    environment.install_postgis_sql()
    environment.ckan_db_init()
    if not quiet:
        write('\n')

    if site_url:
        try:
            site_url = site_url.format(address=environment.address, port=environment.port)
            environment.site_url = site_url
            environment.save_site(False)
        except (KeyError, IndexError, ValueError) as e:
            raise DatacatsError('Could not parse site_url: {}'.format(e))

    if start_web:
        environment.start_ckan(address=address, log_syslog=log_syslog, interactive=interactive)
        if not quiet and not interactive:
            write('Starting web server at {0} ...\n'.format(
                environment.web_address()))

    if create_sysadmin:
        try:
            adminpw = confirm_password()
            environment.create_admin_set_password(adminpw)
        except KeyboardInterrupt:
            print

    if not start_web:
        environment.stop_supporting_containers()
