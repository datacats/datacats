import sys

from datacats.docker import image_exists, pull_stream
from datacats.error import DatacatsError


LESSC_IMAGE = 'datacats/lessc'


def less(environment, opts):
    """Recompiles less files in an environment.

Usage:
  datacats less [ENVIRONMENT]

ENVIRONMENT may be an environment name or a path to an environment directory.
Default: '.'
"""
    if not image_exists(LESSC_IMAGE):
        sys.stdout.write('Pulling image {}'.format(LESSC_IMAGE))
        for status in pull_stream(LESSC_IMAGE):
            if 'status' not in status:
                raise DatacatsError('Docker error: ' +
                        (status['error'] if 'error' in status else 'Unknown error.'))
            else:
                sys.stdout.write('.')
                sys.stdout.flush()
        sys.stdout.write('\n')
        sys.stdout.flush()

    print 'Converting .less files to .css...'
    environment.compile_less()
