#! /bin/bash

# Copyright 2014-2015 Boxkite Inc.

# This file is part of the DataCats package and is released under
# the terms of the GNU Affero General Public License version 3.0.
# See LICENSE.txt or http://www.fsf.org/licensing/licenses/agpl-3.0.html

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
