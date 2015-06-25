# Copyright 2014-2015 Boxkite Inc.

# This file is part of the DataCats package and is released under
# the terms of the GNU Affero General Public License version 3.0.
# See LICENSE.txt or http://www.fsf.org/licensing/licenses/agpl-3.0.html

from os import listdir
from os.path import expanduser
import webbrowser
import sys

from datacats.error import DatacatsError


def write(s):
    sys.stdout.write(s)
    sys.stdout.flush()


def stop(environment, opts):
    # pylint: disable=unused-argument
    """Stop serving environment and remove all its containers

Usage:
  datacats stop [-r] [-s NAME] [ENVIRONMENT]

Options:
  -r --remote        Stop DataCats.com cloud instance
  -s --site=NAME    Specify a site to stop. [default: primary]

ENVIRONMENT may be an environment name or a path to an environment directory.
Default: '.'
"""
    environment.stop_ckan()
    environment.stop_supporting_containers()


def start(environment, opts):
    """Create containers and start serving environment

Usage:
  datacats start [-b] [-p|--no-watch] [-s NAME] [--syslog] [--address=IP] [ENVIRONMENT [PORT]]
  datacats start -r [-b] [-s NAME] [--syslog] [--address=IP] [ENVIRONMENT]

Options:
  --address=IP       Address to listen on (Linux-only) [default: 127.0.0.1]
  -b --background    Don't wait for response from web server
  --no-watch         Do not automatically reload templates and .py files on change
  -p --production    Start with apache and debug=false
  -r --remote        Start DataCats.com cloud instance
  -s --site=NAME     Specify a site to start [default: primary]
  --syslog           Log to the syslog

ENVIRONMENT may be an environment name or a path to an environment directory.
Default: '.'
"""
    environment.require_data()

    if environment.fully_running():
        print 'Already running at {0}'.format(environment.web_address())
        return

    reload_(environment, opts)


def reload_(environment, opts):
    """Reload environment source and configuration

Usage:
  datacats reload [-b] [-p|--no-watch] [--syslog] [-s NAME] [--address=IP] [ENVIRONMENT [PORT]]
  datacats reload -r [-b] [--syslog] [-s NAME] [--address=IP] [ENVIRONMENT]

Options:
  --address=IP       Address to listen on (Linux-only) [default: 127.0.0.1]
  -b --background    Don't wait for response from web server
  --no-watch         Do not automatically reload templates and .py files on change
  -p --production    Reload with apache and debug=false
  -r --remote        Reload DataCats.com cloud instance
  -s --site=NAME     Specify a site to reload [default: primary]
  --syslog           Log to the syslog

ENVIRONMENT may be an environment name or a path to an environment directory.
Default: '.'
"""
    environment.require_data()
    environment.stop_ckan()
    if opts['PORT'] or opts['--address'] != '127.0.0.1':
        if opts['PORT']:
            environment.port = int(opts['PORT'])
        if opts['--address'] != '127.0.0.1':
            environment.address = opts['--address']
        environment.save()
    if 'postgres' not in environment.containers_running():
        environment.stop_supporting_containers()
        environment.start_supporting_containers()

    environment.start_ckan(
        production=opts['--production'],
        address=opts['--address'],
        paster_reload=not opts['--no-watch'],
        log_syslog=opts['--syslog'])
    write('Starting web server at {0} ...'.format(environment.web_address()))
    if opts['--background']:
        write('\n')
        return

    try:
        environment.wait_for_web_available()
    finally:
        write('\n')


def info(environment, opts):
    """Display information about environment and running containers

Usage:
  datacats info [-qr] [ENVIRONMENT]

Options:
  -q --quiet         Echo only the web URL or nothing if not running
  -r --remote        Information about DataCats.com cloud instance

ENVIRONMENT may be an environment name or a path to an environment directory.
Default: '.'
"""
    damaged = False
    sites = environment.sites
    if not environment.sites:
        sites = []
        damaged = True

    if opts['--quiet']:
        if damaged:
            raise DatacatsError('Damaged datadir: cannot get address.')
        for site in sites:
            environment.site_name = site
            print '{}: {}'.format(site, environment.web_address())
        return

    datadir = environment.datadir
    if not environment.data_exists():
        datadir = ''
    elif damaged:
        datadir += ' (damaged)'

    print 'Environment name: ' + environment.name
    print ' Environment dir: ' + environment.target
    print '        Data dir: ' + datadir
    print '           Sites: ' + ' '.join(environment.sites)

    for site in environment.sites:
        print
        environment.site_name = site
        print '            Site: ' + site
        print '      Containers: ' + ' '.join(environment.containers_running())

        sitedir = environment.sitedir + (' (damaged)' if not environment.data_complete() else '')
        print '        Site dir: ' + sitedir
        addr = environment.web_address()
        if addr:
            print '    Available at: ' + addr


def list_(opts):
    # pylint: disable=unused-argument
    """List all environments for this user

Usage:
  datacats list
"""
    for p in sorted(listdir(expanduser('~/.datacats'))):
        if p == 'user-profile':
            continue
        print p


def logs(environment, opts):
    """Display or follow container logs

Usage:
  datacats logs [--postgres | --solr | --datapusher] [-s NAME] [-tr] [--tail=LINES] [ENVIRONMENT]
  datacats logs -f [--postgres | --solr | --datapusher] [-s NAME] [-r] [ENVIRONMENT]

Options:
  --datapusher       Show logs for datapusher instead of web logs
  --postgres         Show postgres database logs instead of web logs
  -f --follow        Follow logs instead of exiting immediately
  -r --remote        Retrieve logs from DataCats.com cloud instance
  --solr             Show solr search logs instead of web logs
  -t --timestamps    Add timestamps to log lines
  -s --site=NAME     Specify a site for logs if needed [default: primary]
  --tail=LINES       Number of lines to show [default: all]

ENVIRONMENT may be an environment name or a path to an environment directory.
Default: '.'
"""
    container = 'web'
    if opts['--solr']:
        container = 'solr'
    if opts['--postgres']:
        container = 'postgres'
    if opts['--datapusher']:
        container = 'datapusher'
    tail = opts['--tail']
    if tail != 'all':
        tail = int(tail)
    l = environment.logs(container, tail, opts['--follow'],
        opts['--timestamps'])
    if not opts['--follow']:
        print l
        return
    try:
        for message in l:
            write(message)
    except KeyboardInterrupt:
        print


def open_(environment, opts):
    # pylint: disable=unused-argument
    """Open web browser window to this environment

Usage:
  datacats open [-r] [-s NAME] [ENVIRONMENT]

Options:
  -r --remote        Open DataCats.com cloud instance address
  -s --site=NAME     Choose a site to open [default: primary]

ENVIRONMENT may be an environment name or a path to an environment directory.
Default: '.'
"""

    environment.require_data()
    addr = environment.web_address()
    if not addr:
        print "Site not currently running"
    else:
        webbrowser.open(addr)


def tweak(environment, opts):
    """Commands operating on environment data

Usage:
  datacats tweak [-s NAME] --install-postgis [ENVIRONMENT]

Options:
  --install-postgis    Install postgis in ckan database
  -s --site=NAME       Choose a site to tweak [default: primary]

ENVIRONMENT may be an environment name or a path to an environment directory.
Default: '.'
"""

    environment.require_data()
    if opts['--install-postgis']:
        print "Installing postgis"
        environment.install_postgis_sql()
