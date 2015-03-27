# Copyright 2014-2015 Boxkite Inc.

# This file is part of the DataCats package and is released under
# the terms of the GNU Affero General Public License version 3.0.
# See LICENSE.txt or http://www.fsf.org/licensing/licenses/agpl-3.0.html

from ConfigParser import SafeConfigParser
from os import listdir
from os.path import expanduser
import webbrowser
import sys

from datacats.project import Project, ProjectError

def write(s):
    sys.stdout.write(s)
    sys.stdout.flush()

def stop(project, opts):
    """Stop serving environment and remove all its containers

Usage:
  datacats stop [-r] [ENVIRONMENT]

Options:
  -r --remote        Stop DataCats.com cloud instance

ENVIRONMENT may be an environment name or a path to an environment directory.
Default: '.'
"""
    project.stop_web()
    project.stop_postgres_and_solr()

def start(project, opts):
    """Create containers and start serving environment

Usage:
  datacats start [-bp] [ENVIRONMENT [PORT]]
  datacats start -r [-b] [ENVIRONMENT]

Options:
  -b --background    Don't wait for response from web server
  -p --production    Start with apache and debug=false
  -r --remote        Start DataCats.com cloud instance

ENVIRONMENT may be an environment name or a path to an environment directory.
Default: '.'
"""
    project.require_data()
    address = project.web_address()
    if address is not None:
        print 'Already running at {0}'.format(address)
        return
    reload_(project, opts)

def reload_(project, opts):
    """Reload environment source and configuration

Usage:
  datacats reload [-bp] [ENVIRONMENT [PORT]]
  datacats reload -r [-b] [ENVIRONMENT]

Options:
  -b --background    Don't wait for response from web server
  -p --production    Reload with apache and debug=false
  -r --remote        Reload DataCats.com cloud instance

ENVIRONMENT may be an environment name or a path to an environment directory.
Default: '.'
"""
    project.require_data()
    project.stop_web()
    if opts['PORT']:
        project.port = int(opts['PORT'])
        project.save()
    if 'postgres' not in project.containers_running():
        project.stop_postgres_and_solr()
        project.start_postgres_and_solr()

    project.start_web(opts['--production'])
    write('Starting web server at {0} ...'.format(project.web_address()))
    if opts['--background']:
        write('\n')
        return
    try:
        project.wait_for_web_available()
    finally:
        write('\n')

def info(project, opts):
    """Display information about environment and running containers

Usage:
  datacats info [-qr] [ENVIRONMENT]

Options:
  -q --quiet         Echo only the web URL or nothing if not running
  -r --remote        Information about DataCats.com cloud instance

ENVIRONMENT may be an environment name or a path to an environment directory.
Default: '.'
"""
    addr = project.web_address()
    if opts['--quiet']:
        if addr:
            print addr
        return

    datadir = project.datadir
    if not project.data_exists():
        datadir = ''
    elif not project.data_complete():
        datadir += ' (damaged)'

    print 'Environment name: ' + project.name
    print '    Default port: ' + str(project.port)
    print ' Environment dir: ' + project.target
    print '        Data dir: ' + datadir
    print '      Containers: ' + ' '.join(project.containers_running())
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

def logs(project, opts):
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
    l = project.logs(container, tail, opts['--follow'], opts['--timestamps'])
    if not opts['--follow']:
        print l
        return
    try:
        for message in l:
            write(message)
    except KeyboardInterrupt:
        print

def open_(project, opts):
    """Open web browser window to this environment

Usage:
  datacats open [-r] [ENVIRONMENT]

Options:
  -r --remote        Open DataCats.com cloud instance address

ENVIRONMENT may be an environment name or a path to an environment directory.
Default: '.'
"""
    project.require_data()
    addr = project.web_address()
    if not addr:
        print "Site not currently running"
    else:
        webbrowser.open(addr)
