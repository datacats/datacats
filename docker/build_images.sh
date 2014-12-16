#! /bin/bash

set -e

docker build -t datacats/search search/
docker build -t datacats/data data/
docker build -t datacats/web web/

docker run -i --name datacats_preload_master \
    -e BRANCH=master datacats/web \
    /bin/bash < setup_ckan.sh
docker commit datacats_preload_master datacats/web:preload_master
docker rm datacats_preload_master

[ "$1" == "push" ] || exit

docker push datacats/web
docker push datacats/data
docker push datacats/search

docker push datacats/web:preload_master
