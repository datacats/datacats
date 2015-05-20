# Copyright 2014-2015 Boxkite Inc.

# This file is part of the DataCats package and is released under
# the terms of the GNU Affero General Public License version 3.0.
# See LICENSE.txt or http://www.fsf.org/licensing/licenses/agpl-3.0.html

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
