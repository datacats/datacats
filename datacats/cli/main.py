# Copyright 2014-2015 Boxkite Inc.

# This file is part of the DataCats package and is released under
# the terms of the GNU Affero General Public License version 3.0.
# See LICENSE.txt or http://www.fsf.org/licensing/licenses/agpl-3.0.html

"""datacats command line interface

Usage:
  datacats pull
  datacats create PROJECT [PORT] [-bin] [--ckan=CKAN_VERSION]
  datacats stop [PROJECT] [-r]
  datacats start [PROJECT [PORT] [-p] | -p | [PROJECT] -r]
  datacats reload [PROJECT [PORT] [-p] | -p | [PROJECT] -r]
  datacats deploy [PROJECT]
  datacats logs [PROJECT] [-f | [-t] [--tail=LINES]] [-d | -s]
  datacats info [PROJECT] [-qr]
  datacats list
  datacats open [PROJECT]
  datacats shell [PROJECT [COMMAND...]]
  datacats install [PROJECT] [-c]
  datacats purge [PROJECT [--delete-project]]
  datacats init [PROJECT [PORT]] [-i]

Options:
  -b --bare                   Bare CKAN site with no example extension
  -c --clean                  Reinstall into a clean virtual environment
  --ckan=CKAN_VERSION         Use CKAN version CKAN_VERSION, defaults to
                              latest development release
  -d --data-logs              Show database logs instead of web logs
  --delete-project            Delete project folder as well as its data
  -f --follow                 Follow logs instead of exiting immediately
  -i --image-only             Only create the project, don't start containers
  -r --remote                 Operate on cloud-deployed production datacats
                              instance
  -s --search-logs            Show search logs instead of web logs
  -t --timestamps             Include timestamps in logs
  --tail=LINES                Number of lines to show [default: all]
  -n --no-sysadmin            Don't create an initial sysadmin user account
  -p --production             Run in production mode instead of debug mode
  -q --quiet                  Simple text response suitable for scripting

PROJECT must be a path for the create and init commands. Other PROJECT
values may be a project name or a path to the project directory.
PROJECT defaults to '.' if not given.
"""

import json
import sys
from docopt import docopt

from datacats.cli import create, manage, install, pull, purge, shell
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
    args = sys.argv[1:]
    # separate shell commands from args pre-docopt to allow
    # passing options as part of command
    command = []
    for i, a in enumerate(args):
        if a.startswith('-'):
            continue
        if a == 'shell':
            command = args[i + 2:]
            args = args[:i + 2]
        break

    opts = docopt(__doc__, args)
    option_not_yet_implemented(opts, '--ckan')
    option_not_yet_implemented(opts, '--remote')
    option_not_yet_implemented(opts, '--clean')
    command_not_yet_implemented(opts, 'deploy')

    if opts['pull']:
        return pull.pull(opts)
    if opts['create']:
        return create.create(opts['PROJECT'], opts['PORT'],
            opts['--bare'], opts['--image-only'], opts['--no-sysadmin'],
            opts['--ckan'])
    if opts['init']:
        return create.init(opts['PROJECT'], opts['PORT'], opts['--image-only'])
    if opts['purge']:
        return purge.purge(opts)
    if opts['list']:
        return manage.list()

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
        return manage.reload_(project, opts)
    if opts['debug']:
        return manage.debug(project)
    if opts['shell']:
        return shell.shell(project, command)
    if opts['info']:
        return manage.info(project, opts)
    if opts['logs']:
        return manage.logs(project, opts)
    if opts['install']:
        return install.install(project, opts['--clean'])
    if opts['open']:
        return manage.open(project)

    print json.dumps(docopt(__doc__), indent=4)
