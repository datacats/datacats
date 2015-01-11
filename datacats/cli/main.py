# Copyright 2014-2015 Boxkite Inc.

# This file is part of the DataCats package and is released under
# the terms of the GNU Affero General Public License version 3.0.
# See LICENSE.txt or http://www.fsf.org/licensing/licenses/agpl-3.0.html

"""datacats command line interface

Usage:
  datacats COMMAND [OPTIONS...] [ARGUMENTS...]
  datacats [COMMAND] --help
  datacats --version

The datacats commands available are:
  create      Create a new project
  deploy      Deploy project to production DataCats.com cloud service
  info        Display information about project and running containers
  init        Initialize a purged project or copied project directory
  install     Install or reinstall Python packages within this project
  list        List all projects for this user
  logs        Display or follow container logs
  open        Open web browser window to this project
  pull        Download or update required datacats docker images
  purge       Purge project database and uploaded files
  reload      Reload project source and configuration
  shell       Run commands or interactive shell within this project
  start       Create containers to start serving project
  stop        Stop serving project and remove all its containers

See 'datacats COMMAND --help' for information about options and
arguments available to each command.
"""

"""
Usage:
  datacats pull
  datacats create PROJECT [PORT] [-bin] [--ckan=CKAN_VERSION]
  datacats stop [PROJECT] [-r]
  datacats start [PROJECT [PORT] [-p] | -p | [PROJECT] -r]
  datacats reload [PROJECT [PORT] [-p] | -p | [PROJECT] -r]
  datacats deploy [PROJECT]
  datacats logs [PROJECT] [-f | [-t] [--tail=LINES]] [-d | -s] [-r]
  datacats info [PROJECT] [-qr]
  datacats list
  datacats open [PROJECT] [-r]
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

COMMANDS = {
    'create': create.create,
    'deploy': 'tbd',
    'info': manage.info,
    'init': create.init,
    'install': install.install,
    'list': manage.list_,
    'logs': manage.logs,
    'open': manage.open_,
    'pull': pull.pull,
    'purge': purge.purge,
    'reload': manage.reload_,
    'shell': shell.shell,
    'start': manage.start,
    'stop': manage.stop,
}

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
    # Find subcommand without docopt so that subcommand options may appear
    # anywhere
    for i, a in enumerate(args):
        if a.startswith('-') or a == 'help':
            continue
        command_fn = COMMANDS.get(a)

        break
    else:
        return docopt(__doc__, args)
    if not command_fn:
        return docopt(__doc__, ['--help'])

    try:
        # shell is special: options might belong to the command being executed
        if command_fn == shell.shell:
            return command_fn(args[i + 2:], args[:i + 2])

        opts = docopt(command_fn.__doc__, args)

        option_not_yet_implemented(opts, '--ckan')
        option_not_yet_implemented(opts, '--remote')
        option_not_yet_implemented(opts, '--clean')
        command_not_yet_implemented(opts, 'deploy')

        if opts.get('PROJECT'):
            project = Project.load(opts['PROJECT'])
            return command_fn(project, opts)
        return command_fn(opts)
    except ProjectError as e:
        print e
        return 1
