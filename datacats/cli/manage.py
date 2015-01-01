# Copyright 2014-2015 Boxkite Inc.

# This file is part of the DataCats package and is released under
# the terms of the GNU Affero General Public License version 3.0.
# See LICENSE.txt or http://www.fsf.org/licensing/licenses/agpl-3.0.html

from ConfigParser import SafeConfigParser

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
    project.start_web()
    print 'Now available at {0}'.format(project.web_address())

def reload(project):
    project.stop_web()
    project.start_web()
    print 'Now available at {0}'.format(project.web_address())

def shell(project):
    project.start_data_and_search()
    project.interactive_shell()
