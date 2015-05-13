from os.path import expanduser, split
from os import getcwd
from datacats.migrate import convert_environment, needs_format_conversion


def migrate(opts):
    """Stop serving environment and remove all its containers

Usage:
  datacats migrate [ENVIRONMENT_DIR]

Migrates an environment to the newer datadir format if necessary.
Defaults to '.' if ENVIRONMENT_DIR isn't specified.
"""
    if 'ENVIRONMENT_DIR' not in opts or not opts['ENVIRONMENT_DIR']:
        cwd = getcwd()
        # Get the dirname
        opts['ENVIRONMENT_DIR'] = split(cwd if cwd[-1] != '/' else cwd[:-1])[1]

    datadir = expanduser('~/.datacats/' + opts['ENVIRONMENT_DIR'])
    if needs_format_conversion(datadir):
        convert_environment(datadir)
