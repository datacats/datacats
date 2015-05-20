# Copyright 2014-2015 Boxkite Inc.

# This file is part of the DataCats package and is released under
# the terms of the GNU Affero General Public License version 3.0.
# See LICENSE.txt or http://www.fsf.org/licensing/licenses/agpl-3.0.html

import sys
import json

from datacats.docker import pull_stream
from datacats.error import DatacatsError

IMAGES = [
    'datacats/web',
    'datacats/web:preload-2.3',
    'datacats/postgres',
    'datacats/solr',
    'datacats/lessc',
    ]


def pull(opts):
    """Download or update required datacats docker images

Usage:
  datacats pull
"""
    for i in IMAGES:
        sys.stdout.write('Pulling image ' + i)
        sys.stdout.flush()
        for s in pull_stream(i):
            if 'status' not in s:
                if 'error' in s:
                    # Line to make the error appear after the ...
                    print
                    raise DatacatsError(s['error'])
                else:
                    print json.dumps(s)
                continue
            sys.stdout.write('.')
            sys.stdout.flush()
        sys.stdout.write('\n')
