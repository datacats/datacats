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
    'datacats/ckan:2.3',
    'datacats/postgres',
    'datacats/solr'
    ]

EXTRA_IMAGES = [
    'datacats/lessc',
    'datacats/ckan:latest',
    'datacats/ckan:2.4'
    ]


def write(line):
    sys.stdout.write(line)
    sys.stdout.flush()


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
    for i in IMAGES + (EXTRA_IMAGES if opts['--all'] else []):
        retrying_pull_image(i)


def retrying_pull_image(image_name):
    _retry_func(pull_image, image_name, 5,
                lambda img, num: write("Pulling image {} failed. Retrying.".format(image_name)),
                "Failed to pull image {}.".format(image_name))


def _retry_func(func, param, num, retry_notif, error_msg):
    """
    A function which retries a given function num times and calls retry_notif each
    time the function is retried.
    :param func: The function to retry num times.
    :param num: The number of times to try before giving up.
    :param retry_notif: Will be called with the same parameter as func if we have to retry the
                        function. Will also receive the number of retries so far as a second
                        parameter.
    :param: error_msg: The message

    Throws DatacatsError if we run out of retries. Returns otherwise.
    """
    for retry_num in range(num):
        if retry_num:
            retry_notif(param, retry_num)
        try:
            func(param)
            return
        except DatacatsError:
            pass

    raise DatacatsError(error_msg)


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
