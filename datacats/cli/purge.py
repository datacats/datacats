# Copyright 2014-2015 Boxkite Inc.

# This file is part of the DataCats package and is released under
# the terms of the GNU Affero General Public License version 3.0.
# See LICENSE.txt or http://www.fsf.org/licensing/licenses/agpl-3.0.html

from shutil import rmtree

from datacats.environment import Environment, DatacatsError


def purge(opts):
    """Purge environment database and uploaded files

Usage:
  datacats purge [-y] [--delete-environment] [ENVIRONMENT]

Options:
  --delete-environment   Delete environment directory as well as its data
  -y --yes               Respond yes to all prompts (i.e. force)

ENVIRONMENT may be an environment name or a path to an environment directory.
Default: '.'
"""
    try:
        environment = Environment.load(opts['ENVIRONMENT'])
    except DatacatsError:
        environment = Environment.load(opts['ENVIRONMENT'], data_only=True)

    if not opts['--yes']:
        inp = None
        # Nothing (default, n), y and n are our valid inputs
        while inp is None or inp.lower()[:1] not in ['y', 'n', '']:
            inp = raw_input('datacats purge will delete all stored data. Are you sure? [n] (y/n): ')

        if inp.lower()[:1] == 'n' or not inp:
            raise DatacatsError('Aborting purge by user request.')

    environment.stop_web()
    environment.stop_postgres_and_solr()

    if opts['--delete-environment']:
        if not environment.target:
            print 'Failed to load environment.',
            print 'Not deleting environment directory.'
        else:
            environment.fix_project_permissions()
            rmtree(environment.target)

    environment.purge_data()
