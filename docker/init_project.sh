#! /bin/bash

CKAN_HOME=/usr/lib/ckan
CKAN_CONFIG=/etc/ckan/default
CKAN_SRC=/project/src

cp -a $CKAN_HOME/. /usr/lib/ckan_target/.
cp -a $CKAN_SRC/. /project/src_target/.
chown -R --reference=$CKAN_CONFIG /project/src_target/.

cp $CKAN_SRC/ckan/ckan/config/who.ini $CKAN_CONFIG/.
cp $CKAN_SRC/ckan/ckan/config/solr/schema.xml $CKAN_CONFIG/.
chown -R --reference=$CKAN_CONFIG /usr/lib/ckan_target/.

chown -R www-data: /var/www
