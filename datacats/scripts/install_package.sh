#!/bin/bash

# Copyright 2014-2015 Boxkite Inc.

# This file is part of the DataCats package and is released under
# the terms of the GNU Affero General Public License version 3.0.
# See LICENSE.txt or http://www.fsf.org/licensing/licenses/agpl-3.0.html

set -e

if [ -e /etc/environment ]; then
    source /etc/environment
    export http_proxy HTTP_PROXY https_proxy HTTPS_PROXY no_proxy NO_PROXY
fi

/usr/lib/ckan/bin/pip install -e "$1"
