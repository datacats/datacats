# Copyright 2014-2015 Boxkite Inc.

# This file is part of the DataCats package and is released under
# the terms of the GNU Affero General Public License version 3.0.
# See LICENSE.txt or http://www.fsf.org/licensing/licenses/agpl-3.0.html

"""datacats command line interface

Usage:
  datacats COMMAND [ARGUMENTS...]
  datacats --help [COMMAND]
  datacats --version

The datacats commands available are:
  create      Create a new environment
  deploy      Deploy environment to production DataCats.com cloud service
  info        Display information about environment and running containers
  init        Initialize a purged environment or copied environment directory
  install     Install or reinstall Python packages within this environment
  list        List all environments for this user
  logs        Display or follow container logs
  open        Open web browser window to this environment
  paster      Run a paster command from the current directory
  pull        Download or update required datacats docker images
  purge       Purge environment database and uploaded files
  reload      Reload environment source and configuration
  shell       Run a command or interactive shell within this environment
  start       Create containers and start serving environment
  stop        Stop serving environment and remove all its containers

See 'datacats help COMMAND' for information about options and
arguments available to each command.
"""

import json
import sys
from docopt import docopt
import pkg_resources

from datacats.cli import create, manage, install, pull, purge, shell, deploy
from datacats.environment import Environment, DatacatsError

COMMANDS = {
    'create': create.create,
    'deploy': deploy.deploy,
    'info': manage.info,
    'init': create.init,
    'install': install.install,
    'list': manage.list_,
    'logs': manage.logs,
    'open': manage.open_,
    'paster': shell.paster,
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
        if help_:
            args = ['--help']
        return docopt(__doc__, args,
            version=pkg_resources.require("datacats")[0].version)
    if not command_fn:
        return docopt(__doc__, ['--help'])

    # shell, paster are special: options might belong to the command being
    # executed
    if command_fn == shell.shell:
        # assume commands don't start with '-' and that those options
        # are intended for datacats
        for j, a in enumerate(args[i + 2:], i + 2):
            if not a.startswith('-'):
                # -- makes docopt parse the rest as positional args
                args = args[:j] + ['--'] + args[j:]
                break

    if command_fn == shell.paster:
        args = args[:i + 1] + ['--'] + args[i + 1:]

    if help_:
        args.insert(1, '--help')

    try:
        opts = docopt(command_fn.__doc__, args)

        option_not_yet_implemented(opts, '--ckan')
        option_not_yet_implemented(opts, '--remote')

        # purge handles loading differently
        if command_fn != purge.purge and 'ENVIRONMENT' in opts:
            environment = Environment.load(opts['ENVIRONMENT'] or '.')
            return command_fn(environment, opts)
        return command_fn(opts)
    except DatacatsError as e:
        print e
        return 1
