#! /bin/bash
# vim:ts=4:sw=4:et

#Script that gives you a test Datacats environment, to check the workflow works
set -e

NAME="${1:-master}"
BRANCH="${2:-master}"
WORKDIR="$(readlink -f "${3:-.}")"
DATADIR="${HOME}/.datacats/${NAME}"
TARGET="$WORKDIR/$NAME"

echo '[1/3] Creating Project "'$NAME'"'
mkdir -p "$DATADIR"
mkdir "$DATADIR/venv"
mkdir "$DATADIR/solr"
mkdir "$DATADIR/db"
mkdir "$DATADIR/storage"
mkdir "$TARGET"
mkdir "$TARGET/ini"
mkdir "$TARGET/src"

# FIXME: based on ckan/master deps for now
docker run --rm -i \
    -e "BRANCH=$BRANCH" \
    -v "$DATADIR/venv:/usr/lib/ckan" \
    -v "$DATADIR/storage:/var/www/storage" \
    -v "$TARGET/src:/project/src" \
    -v "$TARGET/ini:/etc/ckan/default" \
    datacats_web:master /bin/bash < init_project.sh

docker run -d --name="datacats_db_${NAME}" \
    -v "$DATADIR/db:/var/lib/postgresql/data" \
    datacats_db > /dev/null

docker run -d --name="datacats_solr_${NAME}" \
    -v "$DATADIR/solr:/var/lib/solr" \
    -v "$TARGET/src/ckan/ckan/config/solr/schema.xml:/etc/solr/conf/schema.xml" \
    datacats_solr > /dev/null

echo '[2/3] Creating INI files'
docker run --rm -i \
    -v "$DATADIR/venv:/usr/lib/ckan" \
    -v "$TARGET/src:/project/src" \
    -v "$TARGET/ini:/etc/ckan/default" \
    datacats_web /bin/bash < init_ini.sh > /dev/null

echo '[3/3] Creating DB'
docker run --rm -i \
    -v "$DATADIR/venv:/usr/lib/ckan" \
    -v "$DATADIR/storage:/var/www/storage" \
    -v "$TARGET/src:/project/src" \
    -v "$TARGET/ini:/etc/ckan/default" \
    --link "datacats_solr_${NAME}":solr \
    --link "datacats_db_${NAME}":db \
    datacats_web /usr/lib/ckan/bin/paster --plugin=ckan db init -c /etc/ckan/default/ckan.ini > /dev/null 2>&1

docker run -d --name="datacats_web_${NAME}" \
    -v "$DATADIR/venv:/usr/lib/ckan" \
    -v "$DATADIR/storage:/var/www/storage" \
    -v "$TARGET/src:/project/src" \
    -v "$TARGET/ini:/etc/ckan/default" \
    --link "datacats_solr_${NAME}":solr \
    --link "datacats_db_${NAME}":db \
    -p 80 \
    datacats_web > /dev/null

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
    -v "$DATADIR/storage:/var/www/storage" \
    -v "$TARGET/src:/project/src" \
    -v "$TARGET/ini:/etc/ckan/default" \
    --link "datacats_solr_${NAME}":solr \
    --link "datacats_db_${NAME}":db \
    datacats_web /usr/lib/ckan/bin/paster --plugin=ckan sysadmin add admin -c /etc/ckan/default/ckan.ini

