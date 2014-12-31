#! /bin/bash

# Copyright 2014-2015 Boxkite Inc.

# This file is part of the DataCats package and is released under
# the terms of the GNU Affero General Public License version 3.0.
# See LICENSE.txt or http://www.fsf.org/licensing/licenses/agpl-3.0.html

echo $BRANCH

CKAN_HOME=/usr/lib/ckan
CKAN_CONFIG=/etc/ckan/default
CKAN_SRC=/project/src

virtualenv $CKAN_HOME
mkdir -p $CKAN_HOME $CKAN_CONFIG /var/www/storage
chown -R www-data:www-data /var/www/
git clone --depth 1 --branch $BRANCH \
    https://github.com/ckan/ckan.git $CKAN_SRC/ckan
$CKAN_HOME/bin/pip install -r $CKAN_SRC/ckan/requirements.txt
$CKAN_HOME/bin/pip install -e $CKAN_SRC/ckan/

exit
