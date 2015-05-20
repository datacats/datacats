from os.path import expanduser, split
from os import getcwd
from datacats.migrate import convert_environment, needs_format_conversion


def migrate(opts):
    """Stop serving environment and remove all its containers

Usage:
  datacats migrate [-y] [-r VERSION] [ENVIRONMENT_DIR]

Options:
  -r --revision=VERSION  The version of the datadir format you want
                         to convert to [default: 2]
  -y --yes               Answer yes to all questions.

Migrates an environment to the newer datadir format if necessary.
Defaults to '.' if ENVIRONMENT_DIR isn't specified.
"""
    try:
        version = int(opts['--revision'])
    except:
        raise DatacatsError('--revision parameter must be an integer.')

    always_yes = opts['--yes']

    if 'ENVIRONMENT_DIR' not in opts or not opts['ENVIRONMENT_DIR']:
        cwd = getcwd()
        # Get the dirname
        opts['ENVIRONMENT_DIR'] = split(cwd if cwd[-1] != '/' else cwd[:-1])[1]

    datadir = expanduser('~/.datacats/' + opts['ENVIRONMENT_DIR'])
    if needs_format_conversion(datadir, version):
        convert_environment(datadir, version, always_yes)
        print 'Successfully converted datadir {} to format version {}'.format(datadir, version)
    else:
        print 'datadir {} is already at version {}.'.format(datadir, version)
