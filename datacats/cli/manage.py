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
    """Stop serving project and remove all its containers

Usage:
  datacats stop [PROJECT] [-r]

Options:
  -r --remote        Stop DataCats.com cloud instance

PROJECT may be a project name or a path to a project directory. Default: '.'
"""
    project.stop_web()
    project.stop_data_and_search()

def start(project, opts):
    """Create containers to start serving project

Usage:
  datacats start [PROJECT [PORT]] [-p]
  datacats start [PROJECT] -r

Options:
  -p --production    Start with apache and debug=false
  -r --remote        Start DataCats.com cloud instance

PROJECT may be a project name or a path to a project directory. Default: '.'
"""
    address = project.web_address()
    if address is not None:
        print 'Already running at {0}'.format(address)
        return
    reload_(project, opts)

def reload_(project, opts):
    """Reload project source and configuration

Usage:
  datacats reload [PROJECT [PORT]] [-p] | -p | [PROJECT] -r]

Options:
  -p --production    Reload with apache and debug=false
  -r --remote        Reload DataCats.com cloud instance

PROJECT may be a project name or a path to a project directory. Default: '.'
"""
    project.stop_web()
    if opts['PORT']:
        project.port = int(opts['PORT'])
        project.save()
    if 'data' not in project.containers_running():
        project.start_data_and_search()
    try:
        project.start_web(opts['--production'])
        print 'Now available at {0}'.format(project.web_address())
    except ProjectError as e:
        print e
        return 1

def info(project, opts):
    """Display information about project and running containers

Usage:
  datacats info [PROJECT] [-qr]

Options:
  -q --quiet         Echo only the web URL or nothing if not running
  -r --remote        Information about DataCats.com cloud instance

PROJECT may be a project name or a path to a project directory. Default: '.'
"""
    addr = project.web_address()
    if opts['--quiet']:
        if addr:
            print addr
        return

    print '    Project name: ' + project.name
    print '    CKAN version: ' + project.ckan_version
    print '    Default port: ' + str(project.port)
    print '     Project dir: ' + project.target
    print '        Data dir: ' + project.datadir
    print '      Containers: ' + ' '.join(project.containers_running())
    if not addr:
        return
    print '    Available at: ' + addr

def list_(opts):
    """List all projects for this user

Usage:
  datacats list
"""
    for p in sorted(listdir(expanduser('~/.datacats'))):
        print p

def logs(project, opts):
    """Display or follow container logs

Usage:
  datacats logs [PROJECT] [-f | [-t] [--tail=LINES]] [-d | -s] [-r]

Options:
  -d --data-logs     Show postgres database logs instead of web logs
  -f --follow        Follow logs instead of exiting immediately
  -r --remote        Retrieve logs from DataCats.com cloud instance
  -s --search-logs   Show solr search logs instead of web logs
  -t --timestamps    Add timestamps to log lines
  --tail=LINES       Number of lines to show [default: all]

PROJECT may be a project name or a path to a project directory. Default: '.'
"""
    container = 'web'
    if opts['--search-logs']:
        container = 'search'
    if opts['--data-logs']:
        container = 'data'
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
    """Open web browser window to this project

Usage:
  datacats open [PROJECT] [-r]

Options:
  -r --remote        Open DataCats.com cloud instance address

PROJECT may be a project name or a path to a project directory. Default: '.'
"""
    addr = project.web_address()
    if not addr:
        print "Site not currently running"
    else:
        webbrowser.open(addr)
