# Copyright 2014-2015 Boxkite Inc.

# This file is part of the DataCats package and is released under
# the terms of the GNU Affero General Public License version 3.0.
# See LICENSE.txt or http://www.fsf.org/licensing/licenses/agpl-3.0.html

from datacats.project import Project

def shell(project, opts):
    """Run a command or interactive shell within this project

Usage:
  datacats shell [PROJECT [COMMAND...]]

PROJECT may be a project name or a path to a project directory. Default: '.'
"""
    project.start_postgres_and_solr()
    return project.interactive_shell(opts['COMMAND'])

