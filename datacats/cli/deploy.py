# Copyright 2014-2015 Boxkite Inc.

# This file is part of the DataCats package and is released under
# the terms of the GNU Affero General Public License version 3.0.
# See LICENSE.txt or http://www.fsf.org/licensing/licenses/agpl-3.0.html

from datacats.cli.profile import get_working_profile

def deploy(project, opts):
    """Deploy environment to production DataCats.com cloud service

Usage:
  datacats deploy [ENVIRONMENT [TARGET_NAME]]

ENVIRONMENT may be an environment name or a path to a environment directory.
Default: '.'
"""
    profile = get_working_profile(project)
    if not profile:
        return

    target_name = opts['TARGET_NAME']
    if target_name is None:
        target_name = project.name
    profile.deploy(project, target_name)
