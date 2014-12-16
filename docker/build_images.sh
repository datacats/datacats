#! /bin/bash

set -e

docker build -t datacats/solr solr/
docker build -t datacats/postgres postgres/
docker build -t datacats/web web/

docker run -i --name datacats_preload_master \
    -e BRANCH=master datacats_web \
    /bin/bash < setup_ckan.sh
docker commit datacats_preload_master datacats/web:preload_master
docker rm datacats_preload_master
