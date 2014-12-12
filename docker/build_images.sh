#! /bin/bash

set -e

docker build -t datacats_solr solr/
docker build -t datacats_db postgresql/
docker build -t datacats_web web/

docker run -i --name datacats_web_master \
    -e BRANCH=master datacats_web \
    /bin/bash < setup_ckan.sh
docker commit datacats_web_master datacats_web:master
docker rm datacats_web_master
