# Copyright 2014-2015 Boxkite Inc.

# This file is part of the DataCats package and is released under
# the terms of the GNU Affero General Public License version 3.0.
# See LICENSE.txt or http://www.fsf.org/licensing/licenses/agpl-3.0.html

import re

NAME_RE = r'[a-z][a-z0-9]*$'
DATACATS_NAME_RE = r'[a-z][a-z0-9]{4,}$'


def valid_name(n):
    """
    Return True for environment names that may be used locally
    """
    return bool(re.match(NAME_RE, n))


def valid_deploy_name(n):
    """
    Return True for environment names that may be deployed to DataCats.com
    """
    return bool(re.match(DATACATS_NAME_RE, n))
