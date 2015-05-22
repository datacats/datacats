# Copyright 2014-2015 Boxkite Inc.

# This file is part of the DataCats package and is released under
# the terms of the GNU Affero General Public License version 3.0.
# See LICENSE.txt or http://www.fsf.org/licensing/licenses/agpl-3.0.html

from shutil import rmtree

from datacats.environment import Environment, DatacatsError


def purge(opts):
    """Purge environment database and uploaded files

Usage:
  datacats purge [-c NAME | --delete-environment] [-y] [ENVIRONMENT]

Options:
  --delete-environment   Delete environment directory as well as its data, as
                         well as the data for **all** sites.
  -s --site=NAME         Specify a site to be purge [default: primary]
  -y --yes               Respond yes to all prompts (i.e. force)

ENVIRONMENT may be an environment name or a path to an environment directory.
Default: '.'
"""
    try:
        environment = Environment.load(opts['ENVIRONMENT'], opts['--site'])
    except DatacatsError:
        environment = Environment.load(opts['ENVIRONMENT'], opts['--site'], data_only=True)

    # We need a valid site if they don't want to blow away everything.
    if not opts['--delete-environment']:
        environment.require_valid_site()

    sites = [opts['--site']] if not opts['--delete-environment'] else environment.sites

    if not opts['--yes']:
        inp = None
        # Nothing (default, n), y and n are our valid inputs
        while inp is None or inp.lower()[:1] not in ['y', 'n', '']:
            inp = raw_input('datacats purge will delete all stored data. Are you sure? [n] (y/n): ')

        if inp.lower()[:1] == 'n' or not inp:
            raise DatacatsError('Aborting purge by user request.')

    environment.stop_web()
    environment.stop_postgres_and_solr()

    environment.purge_data(sites)

    if opts['--delete-environment']:
        if not environment.target:
            print 'Failed to load environment.',
            print 'Not deleting environment directory.'
        else:
            environment.fix_project_permissions()
            rmtree(environment.target)
