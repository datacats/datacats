# Copyright 2014-2015 Boxkite Inc.

# This file is part of the DataCats package and is released under
# the terms of the GNU Affero General Public License version 3.0.
# See LICENSE.txt or http://www.fsf.org/licensing/licenses/agpl-3.0.html

from os.path import isdir
from shutil import rmtree

from datacats.environment import Environment, DatacatsError

def purge(opts):
    """Purge environment database and uploaded files

Usage:
  datacats purge [-c NAME | --delete-environment] [ENVIRONMENT]

Options:
  --delete-environment   Delete environment directory as well as its data, as
                         well as the data for **all** children.
  -c --child=NAME      Specify a child to be purge [default: primary]

ENVIRONMENT may be an environment name or a path to an environment directory.
Default: '.'
"""
    try:
        environment = Environment.load(opts['ENVIRONMENT'], opts['--child'])
    except DatacatsError as e:
        environment = Environment.load(opts['ENVIRONMENT'], opts['--child'], data_only=True)

    # We need a valid child if they don't want to blow away everything.
    if not opts['--delete-environment']:
        environment.require_valid_child()

    children = [opts['--child']] if not opts['--delete-environment'] else environment.children

    environment.stop_web()
    environment.stop_postgres_and_solr()

    if opts['--delete-environment']:
        if not environment.target:
            print 'Failed to load environment.',
            print 'Not deleting environment directory.'
        else:
            environment.fix_project_permissions()
            rmtree(environment.target)
    environment.purge_data(children)
