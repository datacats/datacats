#! /bin/bash
# vim:ts=4:sw=4:et

#Script that gives you a test Datacats environment, to check the workflow works
set -e

NAME="${1:-master}"
BRANCH="${2:-master}"
WORKDIR="$(readlink -f "${3:-.}")"
DATADIR="${HOME}/.datacats/${NAME}"
TARGET="$WORKDIR/$NAME"

POSTGRES_PASSWORD=$(</dev/urandom tr -cd '[:alnum:]' | head -c16)
CKAN_PASSWORD=$(</dev/urandom tr -cd '[:alnum:]' | head -c16)
DATASTORE_RO_PASSWORD=$(</dev/urandom tr -cd '[:alnum:]' | head -c16)
DATASTORE_RW_PASSWORD=$(</dev/urandom tr -cd '[:alnum:]' | head -c16)

echo '[1/2] Creating Project "'$NAME'"'
mkdir -p "$DATADIR"
mkdir "$DATADIR/venv"
mkdir "$DATADIR/search"
mkdir "$DATADIR/data"
mkdir "$DATADIR/files"
mkdir "$TARGET"
mkdir "$TARGET/conf"
mkdir "$TARGET/src"

# FIXME: based on ckan/master deps for now
docker run --rm -i \
    -e "BRANCH=$BRANCH" \
    -v "$DATADIR/venv:/usr/lib/ckan_target" \
    -v "$DATADIR/files:/var/www/storage" \
    -v "$TARGET/src:/project/src_target" \
    -v "$TARGET/conf:/etc/ckan/default" \
    datacats/web:preload_master /bin/bash < init_project.sh

docker run --rm -i \
    -e CKAN_PASSWORD="$CKAN_PASSWORD" \
    -e DATASTORE_RO_PASSWORD="$DATASTORE_RO_PASSWORD" \
    -e DATASTORE_RW_PASSWORD="$DATASTORE_RW_PASSWORD" \
    -v "$DATADIR/venv:/usr/lib/ckan" \
    -v "$TARGET/src:/project/src" \
    -v "$TARGET/conf:/etc/ckan/default" \
    datacats/web /bin/bash < init_ini.sh > /dev/null

docker run -d --name="datacats_data_${NAME}" \
    -e POSTGRES_PASSWORD="$POSTGRES_PASSWORD" \
    -e CKAN_PASSWORD="$CKAN_PASSWORD" \
    -e DATASTORE_RO_PASSWORD="$DATASTORE_RO_PASSWORD" \
    -e DATASTORE_RW_PASSWORD="$DATASTORE_RW_PASSWORD" \
    -v "$DATADIR/data:/var/lib/postgresql/data" \
    datacats/data > /dev/null

docker run -d --name="datacats_search_${NAME}" \
    -v "$DATADIR/search:/var/lib/solr" \
    -v "$TARGET/conf/schema.xml:/etc/solr/conf/schema.xml" \
    datacats/search > /dev/null

echo '[2/2] Initializing Database'
docker run --rm -i \
    -v "$DATADIR/venv:/usr/lib/ckan" \
    -v "$DATADIR/files:/var/www/storage" \
    -v "$TARGET/src:/project/src" \
    -v "$TARGET/conf:/etc/ckan/default" \
    --link "datacats_search_${NAME}":solr \
    --link "datacats_data_${NAME}":db \
    datacats/web /usr/lib/ckan/bin/paster --plugin=ckan db init -c /etc/ckan/default/ckan.ini > /dev/null 2>&1

docker run -d --name="datacats_web_${NAME}" \
    -v "$DATADIR/venv:/usr/lib/ckan" \
    -v "$DATADIR/files:/var/www/storage" \
    -v "$TARGET/src:/project/src" \
    -v "$TARGET/conf:/etc/ckan/default" \
    --link "datacats_search_${NAME}":solr \
    --link "datacats_data_${NAME}":db \
    -p 80 \
    datacats/web > /dev/null

IP=""
while true; do
    IP=$(docker inspect --format '{{ .NetworkSettings.IPAddress }}' "datacats_web_${NAME}" 2>/dev/null) || true
    if [ "$IP" == "" ]; then sleep 0.1; continue; fi
    break
done

echo "Site available at http://$IP/"
echo
echo Creating Initial Sysadmin User
docker run --rm -it \
    -v "$DATADIR/venv:/usr/lib/ckan" \
    -v "$DATADIR/files:/var/www/storage" \
    -v "$TARGET/src:/project/src" \
    -v "$TARGET/conf:/etc/ckan/default" \
    --link "datacats_search_${NAME}":solr \
    --link "datacats_data_${NAME}":db \
    datacats/web /usr/lib/ckan/bin/paster --plugin=ckan sysadmin add admin -c /etc/ckan/default/ckan.ini

