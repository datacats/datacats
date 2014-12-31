# Copyright 2014-2015 Boxkite Inc.

# This file is part of the DataCats package and is released under
# the terms of the GNU Affero General Public License version 3.0.
# See LICENSE.txt or http://www.fsf.org/licensing/licenses/agpl-3.0.html

import sys
import json

from datacats.docker import pull_stream

IMAGES = [
    'datacats/web',
    'datacats/web:preload_master',
    'datacats/data',
    'datacats/search',
    'scratch',
    ]

def pull(opts):
    """
    Pull down all docker images used by DataCats
    """

    sameline = False
    for i in IMAGES:
        sys.stdout.write('Pulling image '+ i)
        sys.stdout.flush()
        for s in pull_stream(i):
            if 'status' not in s:
                print json.dumps(s, indent=2)
                continue
            if s['status'] == 'Download complete':
                sys.stdout.write('.')
                sys.stdout.flush()
                continue
        sys.stdout.write('\n')
