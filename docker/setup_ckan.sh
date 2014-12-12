#! /bin/bash

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
cp $CKAN_SRC/ckan/ckan/config/who.ini $CKAN_CONFIG/who.ini
