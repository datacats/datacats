# Copyright 2014-2015 Boxkite Inc.

# This file is part of the DataCats package and is released under
# the terms of the GNU Affero General Public License version 3.0.
# See LICENSE.txt or http://www.fsf.org/licensing/licenses/agpl-3.0.html

from datacats.cli.util import require_extra_image


LESSC_IMAGE = 'datacats/lessc'


def less(environment, opts):
    # pylint: disable=unused-argument
    """Recompiles less files in an environment.

Usage:
  datacats less [ENVIRONMENT]

ENVIRONMENT may be an environment name or a path to an environment directory.
Default: '.'
"""
    require_extra_image(LESSC_IMAGE)

    print 'Converting .less files to .css...'
    for log in environment.compile_less():
        print log
