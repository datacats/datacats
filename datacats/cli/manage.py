# Copyright 2014-2015 Boxkite Inc.

# This file is part of the DataCats package and is released under
# the terms of the GNU Affero General Public License version 3.0.
# See LICENSE.txt or http://www.fsf.org/licensing/licenses/agpl-3.0.html

from ConfigParser import SafeConfigParser
from os import listdir
from os.path import expanduser
import webbrowser

from datacats.project import Project, ProjectError

def stop(project):
    project.stop_web()
    project.stop_data_and_search()

def start(project, opts):
    address = project.web_address()
    if address is not None:
        print 'Already running at {0}'.format(address)
        return
    if opts['PORT']:
        project.port = int(opts['PORT'])
        project.save()
    project.start_data_and_search()
    project.start_web(opts['--production'])
    print 'Now available at {0}'.format(project.web_address())

def reload(project, opts):
    project.stop_web()
    project.start_web(opts['--production'])
    print 'Now available at {0}'.format(project.web_address())

def info(project, opts):
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

def list():
    for p in sorted(listdir(expanduser('~/.datacats'))):
        print p

def logs(project, opts):
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
            print message
    except KeyboardInterrupt:
        print

def open(project):
    addr = project.web_address()
    if not addr:
        print "Site not currently running"
    else:
        webbrowser.open(addr)
