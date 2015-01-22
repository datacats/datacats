# Copyright 2014-2015 Boxkite Inc.

# This file is part of the DataCats package and is released under
# the terms of the GNU Affero General Public License version 3.0.
# See LICENSE.txt or http://www.fsf.org/licensing/licenses/agpl-3.0.html

from os.path import isdir
from shutil import rmtree

from datacats.project import Project, ProjectError

def purge(opts):
    """Purge environment database and uploaded files

Usage:
  datacats purge [--delete-environment] [ENVIRONMENT]

Options:
  --delete-environment   Delete environment directory as well as its data

ENVIRONMENT may be an environment name or a path to an environment directory.
Default: '.'
"""
    try:
        project = Project.load(opts['ENVIRONMENT'])
    except ProjectError as e:
        project = Project.load(opts['ENVIRONMENT'], data_only=True)

    project.stop_web()
    project.stop_postgres_and_solr()

    if opts['--delete-environment']:
        if not project.target:
            print 'Failed to load environment.',
            print 'Not deleting environment directory.'
        else:
            project.fix_project_permissions()
            rmtree(project.target)

    project.purge_data()
