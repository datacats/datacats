#! /bin/bash

#Script that gives you a test Datacats environment, to check the workflow works
set -e

NAME="${1:-master}"
BRANCH="${2:-master}"
WORKDIR="$(readlink -f "${3:-.}")"
DATADIR="${HOME}/.datacats/${NAME}"
TARGET="$WORKDIR/$NAME"

echo Creating CKAN Project
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
    -v "$TARGET/src:/project/src" \
    -v "$TARGET/ini:/etc/ckan/default" \
    datacats_web:master /bin/bash < init_project.sh

echo Starting DB
docker run -d --name="datacats_db_${NAME}" datacats_db

echo Starting Solr
docker run -d --name="datacats_solr_${NAME}" \
    -v "$DATADIR/solr:/var/lib/solr" \
    -v "$TARGET/src/ckan/ckan/config/solr/schema.xml:/etc/solr/conf/schema.xml" \
    datacats_solr

echo Creating INI files
docker run --rm -i \
    -v "$DATADIR/venv:/usr/lib/ckan" \
    -v "$TARGET/src:/project/src" \
    -v "$TARGET/ini:/etc/ckan/default" \
    datacats_web /bin/bash < init_ini.sh

echo Creating DB
docker run --rm -i \
    -v "$DATADIR/venv:/usr/lib/ckan" \
    -v "$TARGET/src:/project/src" \
    -v "$TARGET/ini:/etc/ckan/default" \
    --link "datacats_solr_${NAME}":solr \
    --link "datacats_db_${NAME}":db \
    datacats_web /usr/lib/ckan/bin/paster --plugin=ckan db init -c /etc/ckan/default/ckan.ini

echo Starting web server
docker run --name="datacats_web_${NAME}" -it \
    -v "$DATADIR/venv:/usr/lib/ckan" \
    -v "$TARGET/src:/project/src" \
    -v "$TARGET/ini:/etc/ckan/default" \
    --link "datacats_solr_${NAME}":solr \
    --link "datacats_db_${NAME}":db \
    -p 80 \
    datacats_web
