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
    ]

DEVEL_IMAGES = [
    'datacats/lessc',
    ]


def pull(opts):
    """Download or update required datacats docker images

Usage:
  datacats pull [-a]

Options:
  -a --all           Pull optional images as well as required
                     images. Optional images will be pulled
                     when needed, but you can use this to make
                     sure you have all the images you need if
                     you are going offline.
"""
    for i in IMAGES + (DEVEL_IMAGES if opts['--all'] else []):
        pull_image(i)


def pull_image(image_name):
    sys.stdout.write('Pulling image ' + image_name)
    sys.stdout.flush()
    for s in pull_stream(image_name):
        if 'status' not in s:
            if 'error' in s:
                # Line to make the error appear after the ...
                print
                raise DatacatsError(s['error'])
            else:
                print json.dumps(s)
        sys.stdout.write('.')
        sys.stdout.flush()
    sys.stdout.write('\n')
