#! /bin/bash

# Copyright 2014-2015 Boxkite Inc.

# This file is part of the DataCats package and is released under
# the terms of the GNU Affero General Public License version 3.0.
# See LICENSE.txt or http://www.fsf.org/licensing/licenses/agpl-3.0.html

set -e

HERE="$(dirname $(readlink -f $0))"

docker build -t datacats/search search/
docker build -t datacats/data data/
docker build -t datacats/web web/

docker rm datacats_preload_1 || true
docker run -i --name datacats_preload_1 \
    -e BRANCH=master datacats/web \
    /bin/bash < "$HERE/setup_ckan.sh"
docker rmi datacats_preload_1_image || true
docker commit datacats_preload_1 datacats_preload_1_image

docker cp datacats_preload_1:/project/ckan \
    "$HERE/src"

rm -rf "$HERE/src" || true
mkdir "$HERE/src"

docker run -i --rm \
    -v "$HERE/src/ckan:/project/ckan:ro" \
    node:0.10-slim \
    /bin/bash < "$HERE/compile_less.sh" > "$HERE/src/main.debug.css"

docker rm datacats_preload_2 || true
docker run -i --name datacats_preload_2 \
    datacats_preload_1_image \
    /bin/bash -c \
    'cat > /project/ckan/ckan/public/base/css/main.debug.css' \
    < "$HERE/src/main.debug.css"
docker rmi datacats/web:preload_master
docker commit datacats_preload_2 datacats/web:preload_master

docker rm -f datacats_preload_1
docker rm -f datacats_preload_2

[ "$1" == "push" ] || exit

docker push datacats/web
docker push datacats/data
docker push datacats/search
