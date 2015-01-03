#! /bin/bash

# Copyright 2014-2015 Boxkite Inc.

# This file is part of the DataCats package and is released under
# the terms of the GNU Affero General Public License version 3.0.
# See LICENSE.txt or http://www.fsf.org/licensing/licenses/agpl-3.0.html

set -e

docker build -t datacats/search search/
docker build -t datacats/data data/
docker build -t datacats/web web/

docker rm datacats_preload_interim || true
docker run -i --name datacats_preload_interim \
    -e BRANCH=master datacats/web \
    /bin/bash < setup_ckan.sh
docker commit datacats_preload_interim lessc_interim

CKAN_COPY="$(dirname $(readlink -f $0))/src"
docker cp datacats_preload_interim:/project/ckan \
    "$CKAN_COPY"

docker run -i --rm \
    -v "$CKAN_COPY/ckan:/project/ckan" \
    node:0.10-slim \
    /bin/bash < compile_css.sh > "$CKAN_COPY/main.debug.css"

docker rm datacats_preload_master || true
docker run -i --name datacats_preload_master \
    lessc_interim \
    /bin/bash -c \
    'cat > /project/ckan/ckan/public/base/css/main.debug.css' \
    < "$CKAN_COPY/main.debug.css"
docker commit datacats_preload_master datacats/web:preload_master

docker rm datacats_preload_interim
docker rm datacats_preload_master

[ "$1" == "push" ] || exit

docker push datacats/web
docker push datacats/data
docker push datacats/search
