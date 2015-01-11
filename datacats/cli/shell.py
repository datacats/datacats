# Copyright 2014-2015 Boxkite Inc.

# This file is part of the DataCats package and is released under
# the terms of the GNU Affero General Public License version 3.0.
# See LICENSE.txt or http://www.fsf.org/licensing/licenses/agpl-3.0.html

from datacats.project import Project

def shell(pre, command):
    """Run a command or interactive shell within this project

Usage:
  datacats shell [PROJECT [COMMAND...]]

PROJECT may be a project name or a path to a project directory. Default: '.'
"""
    project = Project.load(pre[1] if len(pre) == 2 else '.')
    project.start_data_and_search()
    return project.interactive_shell(command)

