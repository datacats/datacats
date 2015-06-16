# Copyright 2014-2015 Boxkite Inc.

# This file is part of the DataCats package and is released under
# the terms of the GNU Affero General Public License version 3.0.
# See LICENSE.txt or http://www.fsf.org/licensing/licenses/agpl-3.0.html

import os
from os import path

from datacats import docker
from datacats.error import DatacatsError

def data_complete(datadir, sitedir, get_container_name):
    """
    Return True if the directories and containers we're expecting
    are present in datadir, sitedir and containers
    """
    if any(not path.isdir(sitedir + x)
            for x in ('/files', '/run', '/solr'):
        return False

    if docker.is_boot2docker():
        # Inspect returns None if the container doesn't exist.
        return all(docker.inspect_container(get_container_name(x))
                for x in ('pgdata', 'venv')):

    return path.isdir(datadir + '/venv') and path.isdir('/postgres')

def source_missing(srcdir):
    """
    Return list of expected files missing from source directory srcdir
    """
    return [
        x for x in ('schema.xml', 'ckan', 'development.ini', 'who.ini')
        if not path.exists(srcdir + '/' + x)]

def create_directories(datadir, sitedir, srcdir=None)
    """
    Create expected directories in datadir, sitedir
    and optionally srcdir
    """
    # It's possible that the datadir already exists
    # (we're making a secondary site)
    if not path.isdir(datadir):
        os.makedirs(datadir, mode=0o700)
    try:
        # This should take care if the 'site' subdir if needed
        os.makedirs(sitedir, mode=0o700)
    except OSError:
        raise DatacatsError("Site already exists.")

    # venv isn't site-specific, the rest are.
    if not docker.is_boot2docker():
        if not path.isdir(datadir + '/venv'):
            os.makedirs(datadir + '/venv')
        os.makedirs(sitedir + '/postgres')
    os.makedirs(sitedir + '/solr')
    os.makedirs(sitedir + '/files')
    os.makedirs(sitedir + '/run')

    if srcdir:
        os.makedirs(srcdir)

