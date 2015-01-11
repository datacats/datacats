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
  shell       Run a command or interactive shell within this project
  start       Create containers to start serving project
  stop        Stop serving project and remove all its containers

See 'datacats help COMMAND' for information about options and
arguments available to each command.
"""

import json
import sys
from docopt import docopt

from datacats.cli import create, manage, install, pull, purge, shell, deploy
from datacats.project import Project, ProjectError

COMMANDS = {
    'create': create.create,
    'deploy': deploy.deploy,
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
    help_ = False
    # Find subcommand without docopt so that subcommand options may appear
    # anywhere
    for i, a in enumerate(args):
        if a.startswith('-'):
            continue
        if a == 'help':
            help_ = True
            continue
        command_fn = COMMANDS.get(a)
        break
    else:
        return docopt(__doc__, args)
    if not command_fn:
        return docopt(__doc__, ['--help'])

    # shell is special: options might belong to the command being executed
    # split args into args and shell_command
    if command_fn == shell.shell:
        # assume commands don't start with '-' and that those options
        # are intended for datacats
        for j, a in enumerate(args[i + 2:], i + 2):
            if not a.startswith('-'):
                # -- makes docopt parse the rest as positional args
                args = args[:j] + ['--'] + args[j:]
                break

    if help_:
        args.insert(1, '--help')

    try:
        opts = docopt(command_fn.__doc__, args)

        option_not_yet_implemented(opts, '--ckan')
        option_not_yet_implemented(opts, '--remote')
        option_not_yet_implemented(opts, '--clean')
        command_not_yet_implemented(opts, 'deploy')

        # purge handles loading differently
        if command_fn != purge.purge and 'PROJECT' in opts:
            project = Project.load(opts['PROJECT'] or '.')
            return command_fn(project, opts)
        return command_fn(opts)
    except ProjectError as e:
        print e
        return 1
