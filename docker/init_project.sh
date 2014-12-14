#! /bin/bash

CKAN_HOME=/usr/lib/ckan
CKAN_CONFIG=/etc/ckan/default
CKAN_SRC=/project/src

cp -a /usr/lib/ckan_preload/. $CKAN_HOME/.
cp -a /project/src_preload/. $CKAN_SRC/.
chown -R --reference=$CKAN_CONFIG $CKAN_SRC

cp $CKAN_SRC/ckan/ckan/config/who.ini $CKAN_CONFIG/who.ini
chown -R --reference=$CKAN_CONFIG $CKAN_CONFIG

chown -R www-data: /var/www
