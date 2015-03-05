# Copyright 2014-2015 Boxkite Inc.

# This file is part of the DataCats package and is released under
# the terms of the GNU Affero General Public License version 3.0.
# See LICENSE.txt or http://www.fsf.org/licensing/licenses/agpl-3.0.html

from datacats.project import Project

def paster(opts):
    """Run a paster command within this environment

Usage:
  datacats paster [COMMAND...]

You must be inside a datacats environment to run this. The paster command will
run within your current directory inside the environment. You don't need to
specify the --plugin option. The --config option also need not be specified.
"""
    project = Project.load('.')
    project.start_postgres_and_solr()

    opts['COMMAND'] = ['--', project.extension_dir, 'paster'] + opts['COMMAND']

    return project.interactive_shell(opts['COMMAND'], paster=True)
