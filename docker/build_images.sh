#! /bin/bash

# Copyright 2014-2015 Boxkite Inc.

# This file is part of the DataCats package and is released under
# the terms of the GNU Affero General Public License version 3.0.
# See LICENSE.txt or http://www.fsf.org/licensing/licenses/agpl-3.0.html

set -e

HERE="$(cd "$(dirname "$(dirname "$0")")" && pwd)"

docker build -t datacats/solr solr/
docker build -t datacats/postgres postgres/
docker build -t datacats/web web/
docker build -t datacats/lessc lessc/

# Json for image dict
image_dict='{"2.3": "release-v2.3-latest", "2.4b": "release-v2.4.0", "master": "master"}'

# Loop through the keys
for key in '2.3' '2.4b' 'master'; do
    docker rm datacats_preload_1 || true
    docker run -i --name datacats_preload_1 \
        -e "BRANCH=$(./json_lookup.py "$image_dict" "$key")" datacats/web \
        /bin/bash < "$HERE/setup_ckan.sh"
    docker rmi datacats_preload_1_image || true
    docker commit datacats_preload_1 datacats_preload_1_image

    rm -rf "$HERE/src" || true
    mkdir "$HERE/src"

    docker cp datacats_preload_1:/project/ckan \
        "$HERE/src"

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

    docker rmi "datacats/web:preload-$key" || true
    docker commit datacats_preload_2 "datacats/web:preload-$key"

    rm -rf "$HERE/src"
    docker rm -f datacats_preload_1
    docker rm -f datacats_preload_2
done

[ "$1" == "push" ] || exit

docker push datacats/web
docker push datacats/postgres
docker push datacats/solr
docker push datacats/lessc
