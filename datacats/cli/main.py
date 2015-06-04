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
  less        Recompile less files in an environment

See 'datacats help COMMAND' for information about options and
arguments available to each command.
"""

import sys
from docopt import docopt

from datacats.cli import create, manage, install, pull, purge, shell, deploy, less
from datacats.environment import Environment, DatacatsError
from datacats.userprofile import UserProfile
from datacats.version import __version__

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
    'less': less.less
}


COMMANDS_THAT_USE_SSH = [
    deploy.deploy
]


def main():
    """
    The main entry point for datacats cli tool

    (as defined in setup.py's entry_points)
    It parses the cli arguments for corresponding options
    and runs the corresponding command
    """
    try:
        command_fn, opts = _parse_arguments(sys.argv[1:])
        # purge handles loading differently
        if command_fn == purge.purge or 'ENVIRONMENT' not in opts:
            return command_fn(opts)

        environment = Environment.load(
            opts['ENVIRONMENT'] or '.')

        if command_fn not in COMMANDS_THAT_USE_SSH:
            return command_fn(environment, opts)

        # for commands that communicate with a remote server
        # we load UserProfile and test our communication
        user_profile = UserProfile()
        user_profile.test_ssh_key(environment)

        return command_fn(environment, opts, user_profile)

    except DatacatsError as e:
        if sys.stdout.isatty():
            # error message to have colors if stdout goes to shell
            e.pretty_print()
        else:
            print e
        sys.exit(1)


def _parse_arguments(args):
    help_ = False  # flag for only showing the help message

    # Find subcommand without docopt so that subcommand options may appear
    # anywhere
    for i, a in enumerate(args):
        if a.startswith('-'):
            continue
        if a == 'help':
            help_ = True
            continue
        if a not in COMMANDS:
            raise DatacatsError("\'{0}\' command is not recognized. \n"
              "See \'datacats help\' for the list of available commands".format(a))
        command_fn = COMMANDS[a]
        break
    else:
        opts = docopt(__doc__, args, version=__version__)
        return _intro_message, {}

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

    opts = docopt(command_fn.__doc__, args, version=__version__)

    _option_not_yet_implemented(opts, '--ckan')
    _option_not_yet_implemented(opts, '--remote')
    return command_fn, opts


def _option_not_yet_implemented(opts, name):
    if name not in opts or not opts[name]:
        return
    raise DatacatsError(
        "\'{0}\' option is not implemented yet. \n".format(name))


def _intro_message(opts):
    return docopt(__doc__, ['--help'])
