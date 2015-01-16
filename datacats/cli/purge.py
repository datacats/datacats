# Copyright 2014-2015 Boxkite Inc.

# This file is part of the DataCats package and is released under
# the terms of the GNU Affero General Public License version 3.0.
# See LICENSE.txt or http://www.fsf.org/licensing/licenses/agpl-3.0.html

from os.path import isdir
from shutil import rmtree

from datacats.project import Project, ProjectError

def purge(opts):
    """Purge project database and uploaded files

Usage:
  datacats purge [--delete-project] [PROJECT]

Options:
  --delete-project   Delete project folder as well as its data

PROJECT may be a project name or a path to a project directory. Default: '.'
"""
    try:
        project = Project.load(opts['PROJECT'])
    except ProjectError as e:
        project = Project.load(opts['PROJECT'], data_only=True)

    project.stop_web()
    project.stop_postgres_and_solr()

    if opts['--delete-project']:
        if not project.target:
            print 'Failed to load project. Not deleting project directory.'
        else:
            project.fix_project_permissions()
            rmtree(project.target)

    project.purge_data()
