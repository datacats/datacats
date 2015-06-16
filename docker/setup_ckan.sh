# Copyright 2014-2015 Boxkite Inc.

# This file is part of the DataCats package and is released under
# the terms of the GNU Affero General Public License version 3.0.
# See LICENSE.txt or http://www.fsf.org/licensing/licenses/agpl-3.0.html

echo $BRANCH

CKAN_HOME=/usr/lib/ckan

virtualenv $CKAN_HOME
mkdir -p $CKAN_HOME /project /var/www/storage
chown -R www-data:www-data /var/www/
git clone --depth 1 --branch $BRANCH \
    https://github.com/ckan/ckan.git /project/ckan
git clone -b stable https://github.com/ckan/datapusher /project/datapusher
$CKAN_HOME/bin/pip install -r /project/ckan/requirements.txt
$CKAN_HOME/bin/pip install -e /project/ckan/
$CKAN_HOME/bin/pip install ckanapi
$CKAN_HOME/bin/pip install -r /project/datapusher/requirements.txt


exit
