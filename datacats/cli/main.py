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
    if name not in opts or not opts[name]:
        return
    print "Option {0} is not yet implemented.".format(name)
    sys.exit(1)

def command_not_yet_implemented(opts, name):
    if name not in opts or not opts[name]:
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

        # purge handles loading differently
        if command_fn != purge.purge and opts.get('PROJECT'):
            project = Project.load(opts['PROJECT'])
            return command_fn(project, opts)
        return command_fn(opts)
    except ProjectError as e:
        print e
        return 1
