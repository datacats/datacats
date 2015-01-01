# Copyright 2014-2015 Boxkite Inc.

# This file is part of the DataCats package and is released under
# the terms of the GNU Affero General Public License version 3.0.
# See LICENSE.txt or http://www.fsf.org/licensing/licenses/agpl-3.0.html

"""datacats command line interface

Usage:
  datacats pull
  datacats create PROJECT [PORT] [-bin] [--ckan=CKAN_VERSION]
  datacats start [PROJECT [PORT] | [PROJECT] -r]
  datacats stop [PROJECT] [-r]
  datacats reload [PROJECT] [-r]
  datacats deploy [PROJECT]
  datacats logs [PROJECT] [-f]
  datacats info [PROJECT] [-qr]
  datacats open [PROJECT]
  datacats paster PROJECT PASTER_COMMAND...
  datacats install [PROJECT] [-c]
  datacats purge [PROJECT [-d]]

Options:
  -b --bare                   Bare CKAN site with no example extension
  -c --clean                  Reinstall into a clean virtual environment
  -d --delete-project         Delete project folder as well as its data
  --ckan=CKAN_VERSION         Use CKAN version CKAN_VERSION, defaults to
                              latest development release
  -f --follow                 Follow logs
  -i --image-only             Only create the project, don't start containers
  -r --remote                 Operate on cloud-deployed datacats instance
  -n --no-sysadmin            Don't create an initial sysadmin user account
  -q --quiet                  Simple text response suitable for scripting

Create PROJECT must be a path. Other PROJECT values may be a project name
or a path to the project directory. Project defaults to '.' if not given.
"""

import json
import sys
from docopt import docopt

from datacats.cli import create, manage, install, pull, purge
from datacats.project import Project, ProjectError

def option_not_yet_implemented(opts, name):
    if not opts[name]:
        return
    print "Option {0} is not yet implemented.".format(name)
    sys.exit(1)

def command_not_yet_implemented(opts, name):
    if not opts[name]:
        return
    print "Command {0} is not yet implemented.".format(name)
    sys.exit(1)

def main():
    opts = docopt(__doc__)
    option_not_yet_implemented(opts, '--ckan')
    option_not_yet_implemented(opts, '--remote')
    command_not_yet_implemented(opts, 'deploy')
    command_not_yet_implemented(opts, 'logs')
    command_not_yet_implemented(opts, 'info')
    command_not_yet_implemented(opts, 'paster')

    if opts['pull']:
        return pull.pull(opts)
    if opts['create']:
        return create.create(opts)
    if opts['purge']:
        return purge.purge(opts)

    try:
        project = Project.load(opts['PROJECT'])
    except ProjectError as e:
        print e
        return

    if opts['stop']:
        return manage.stop(project)
    if opts['start']:
        return manage.start(project, opts)
    if opts['reload']:
        return manage.reload(project)
    if opts['install']:
        return install.install(project, opts)

    print json.dumps(docopt(__doc__), indent=4)
