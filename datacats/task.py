# Copyright 2014-2015 Boxkite Inc.

# This file is part of the DataCats package and is released under
# the terms of the GNU Affero General Public License version 3.0.
# See LICENSE.txt or http://www.fsf.org/licensing/licenses/agpl-3.0.html

from datacats import docker
from os import path

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
