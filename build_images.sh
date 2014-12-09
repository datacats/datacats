#! /bin/bash

set -e

docker build -t datacats_solr solr/
docker build -t datacats_db postgresql/
docker build -t datacats_web web/
