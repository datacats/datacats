from datacats.docker import image_exists

from datacats.cli.pull import pull_image


LESSC_IMAGE = 'datacats/lessc'


def less(environment, opts):
    """Recompiles less files in an environment.

Usage:
  datacats less [ENVIRONMENT]

ENVIRONMENT may be an environment name or a path to an environment directory.
Default: '.'
"""
    if not image_exists(LESSC_IMAGE):
        pull_image(LESSC_IMAGE)

    print 'Converting .less files to .css...'
    environment.compile_less()
