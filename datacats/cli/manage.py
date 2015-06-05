# Copyright 2014-2015 Boxkite Inc.

# This file is part of the DataCats package and is released under
# the terms of the GNU Affero General Public License version 3.0.
# See LICENSE.txt or http://www.fsf.org/licensing/licenses/agpl-3.0.html

from os import listdir
from os.path import expanduser
import webbrowser
import sys


def write(s):
    sys.stdout.write(s)
    sys.stdout.flush()


def stop(environment, opts):
    """Stop serving environment and remove all its containers

Usage:
  datacats stop [-r] [ENVIRONMENT]

Options:
  -r --remote        Stop DataCats.com cloud instance

ENVIRONMENT may be an environment name or a path to an environment directory.
Default: '.'
"""
    environment.stop_web()
    environment.stop_postgres_and_solr()


def start(environment, opts):
    """Create containers and start serving environment

Usage:
  datacats start [-bp] [--address=IP] [--syslog] [ENVIRONMENT [PORT]]
  datacats start -r [-b] [--address=IP] [--syslog] [ENVIRONMENT]

Options:
  --address=IP       Address to listen on (Linux-only) [default: 127.0.0.1]
  -b --background    Don't wait for response from web server
  -p --production    Start with apache and debug=false
  -r --remote        Start DataCats.com cloud instance
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
  datacats reload [-bp] [--address=IP] [--syslog] [ENVIRONMENT [PORT]]
  datacats reload -r [-b] [--address=IP] [--syslog] [ENVIRONMENT]

Options:
  --address=IP       Address to listen on (Linux-only) [default: 127.0.0.1]
  -b --background    Don't wait for response from web server
  -p --production    Reload with apache and debug=false
  -r --remote        Reload DataCats.com cloud instance
  --syslog           Log to the syslog

ENVIRONMENT may be an environment name or a path to an environment directory.
Default: '.'
"""
    environment.require_data()
    environment.stop_web()
    if opts['PORT'] or opts['--address'] != '127.0.0.1':
        if opts['PORT']:
            environment.port = int(opts['PORT'])
        if opts['--address'] != '127.0.0.1':
            environment.address = opts['--address']
        environment.save()
    if 'postgres' not in environment.containers_running():
        environment.stop_postgres_and_solr()
        environment.start_postgres_and_solr()

    environment.start_web(
        production=opts['--production'],
        address=opts['--address'],
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
    addr = environment.web_address()
    if opts['--quiet']:
        if addr:
            print addr
        return

    datadir = environment.datadir
    if not environment.data_exists():
        datadir = ''
    elif not environment.data_complete():
        datadir += ' (damaged)'

    print 'Environment name: ' + environment.name
    print '    Default port: ' + str(environment.port)
    print ' Environment dir: ' + environment.target
    print '        Data dir: ' + datadir
    print '      Containers: ' + ' '.join(environment.containers_running())
    if not addr:
        return
    print '    Available at: ' + addr


def list_(opts):
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
  datacats logs [-d | -s] [-tr] [--tail=LINES] [ENVIRONMENT]
  datacats logs -f [-d | -s] [-r] [ENVIRONMENT]

Options:
  -d --postgres-logs Show postgres database logs instead of web logs
  -f --follow        Follow logs instead of exiting immediately
  -r --remote        Retrieve logs from DataCats.com cloud instance
  -s --solr-logs     Show solr search logs instead of web logs
  -t --timestamps    Add timestamps to log lines
  --tail=LINES       Number of lines to show [default: all]

ENVIRONMENT may be an environment name or a path to an environment directory.
Default: '.'
"""
    container = 'web'
    if opts['--solr-logs']:
        container = 'solr'
    if opts['--postgres-logs']:
        container = 'postgres'
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
    """Open web browser window to this environment

Usage:
  datacats open [-r] [ENVIRONMENT]

Options:
  -r --remote        Open DataCats.com cloud instance address

ENVIRONMENT may be an environment name or a path to an environment directory.
Default: '.'
"""
    environment.require_data()
    addr = environment.web_address()
    if not addr:
        print "Site not currently running"
    else:
        webbrowser.open(addr)
