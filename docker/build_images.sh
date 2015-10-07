#! /bin/bash

# Copyright 2014-2015 Boxkite Inc.

# This file is part of the DataCats package and is released under
# the terms of the GNU Affero General Public License version 3.0.
# See LICENSE.txt or http://www.fsf.org/licensing/licenses/agpl-3.0.html

set -e

HERE="$(cd "$(dirname "$(dirname "$0")")" && pwd)"

docker rmi -f postgres:9.3 || true
docker build -t postgres:9.3 -f postgres/Dockerfile-postgres postgres/ 

docker build -t datacats/solr solr/
docker build -t datacats/postgres postgres/
docker build -t datacats/web web/
docker build -t datacats/lessc lessc/
docker build -t datacats/ckan ckan/
docker build -t datacats/ckan:2.3 -f ckan/Dockerfile-2.3 ckan/
docker build -t datacats/ckan:2.4 -f ckan/Dockerfile-2.4 ckan/


[ "$1" == "push" ] || exit

docker push datacats/web
docker push datacats/postgres
docker push datacats/solr
docker push datacats/lessc
docker push datacats/ckan
