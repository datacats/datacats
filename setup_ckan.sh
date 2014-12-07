#! /bin/bash

virtualenv $CKAN_HOME #change to use site packages
mkdir -p $CKAN_HOME $CKAN_CONFIG /var/www/storage
chown -R www-data:www-data /var/www/
git clone --depth 1 https://github.com/ckan/ckan.git $CKAN_HOME/src/ckan
$CKAN_HOME/bin/pip install -r $CKAN_HOME/src/ckan/requirements.txt
$CKAN_HOME/bin/pip install -e $CKAN_HOME/src/ckan/
cp $CKAN_HOME/src/ckan/ckan/config/who.ini $CKAN_CONFIG/who.ini
