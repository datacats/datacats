# Copyright 2014-2015 Boxkite Inc.

# This file is part of the DataCats package and is released under
# the terms of the GNU Affero General Public License version 3.0.
# See LICENSE.txt or http://www.fsf.org/licensing/licenses/agpl-3.0.html

from datacats.cli.profile import get_working_profile

def deploy(project, opts):
    """Deploy environment to production DataCats.com cloud service

Usage:
  datacats deploy [ENVIRONMENT]

ENVIRONMENT may be an environment name or a path to a environment directory.
Default: '.'
"""
    profile = get_working_profile()
    # 1. open or create user profile
    #    a. create ~/.datacats/user-profile/config
    #    b. generate ssh key
    # 2. connect to DataCats.com
    #    b. associate ssh key with DataCats.com account
    # 3. reserve DataCats.com project name, save in project conf
    # 4. rsync project directory (triggers install and reload)
