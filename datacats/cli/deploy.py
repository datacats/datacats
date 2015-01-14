# Copyright 2014-2015 Boxkite Inc.

# This file is part of the DataCats package and is released under
# the terms of the GNU Affero General Public License version 3.0.
# See LICENSE.txt or http://www.fsf.org/licensing/licenses/agpl-3.0.html

def deploy(project, opts):
    """Deploy project to Deploy project to production DataCats.com cloud service

Usage:
  datacats deploy [PROJECT]

PROJECT may be a project name or a path to a project directory. Default: '.'
"""
    # 1. open or create user profile
    #    a. create ~/.datacats/user-profile/config
    #    b. generate ssh key
    #    c. request email address
    # 2. connect to DataCats.com
    #    a. create account or log in to DataCats.com account
    #    b. associate ssh key with DataCats.com account
    # 3. reserve DataCats.com project name, save in project conf
    # 4. rsync project directory (triggers install and reload)
