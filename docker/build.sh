#! /bin/bash

#Script that gives you a test Datacats environment, to check the workflow works
set -e

NAME="${1:-master}"
BRANCH="${2:-master}"
WORKDIR="$(readlink -f "${3:-.}")"
DATADIR="${HOME}/.datacats/${NAME}"

TARGET="$WORKDIR/$NAME"
mkdir -p "$DATADIR"
mkdir "$DATADIR/venv"
mkdir "$DATADIR/solr"
mkdir "$DATADIR/db"
mkdir "$DATADIR/storage"
mkdir "$TARGET"
mkdir "$TARGET/ini"
mkdir "$TARGET/src"

#Setup the virtualenv
docker run -i \
    -e "BRANCH=$BRANCH" \
    -v "$DATADIR/venv:/usr/lib/ckan" \
    -v "$TARGET/src:/project/src" \
    -v "$TARGET/ini:/etc/ckan/default" \
    datacats_web /bin/bash < setup_ckan.sh

echo Starting DB
#Run postgres
docker run -d --name="datacats_db_${NAME}" datacats_db

echo Starting Solr
#Run Solr
docker run -d --name="datacats_solr_${NAME}" \
    -v $TARGET/venv/src/ckan/ckan/config/solr/schema.xml:/etc/solr/conf/schema.xml \
    datacats_solr

#Initialize the ckan .ini files
id=$(cat init_ini.sh | docker run -i -a stdin \
    -v $TARGET/venv:/usr/lib/ckan \
    -v $TARGET/ini:/etc/ckan/default \
    datacats_web /bin/bash)
test $(docker wait $id) -eq 0

# create a writable version of the ckan INI file
cp "$TARGET/ini/default.production.ini" "$TARGET/ini/production.ini"

#Initialize the database
id=$(docker run -i -a stdin \
    -v $TARGET/venv:/usr/lib/ckan \
    -v $TARGET/ini:/etc/ckan/default \
    --link "datacats_solr_${NAME}":solr \
    --link "datacats_db_${NAME}":db \
    datacats_web /usr/lib/ckan/bin/paster --plugin=ckan db init -c /etc/ckan/default/production.ini)
test $(docker wait $id) -eq 0

# copy the wsgi file into the mounted host volume so that our user owns it
cp web/apache.wsgi "$TARGET/ini/apache.wsgi"

#Run the web container
docker run --name="datacats_web_${NAME}" -it \
    -v $TARGET/venv:/usr/lib/ckan \
    -v $TARGET/ini:/etc/ckan/default \
    --link "datacats_solr_${NAME}":solr \
    --link "datacats_db_${NAME}":db \
    -p 80 \
    datacats_web
