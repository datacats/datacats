#! /bin/bash

#Script that gives you a test Datacats environment, to check the workflow works

NAME=${1:-master}
BRANCH=${2:-master}
WORKDIR=${3:-.}

TARGET="$WORKDIR/$NAME"
mkdir -p $TARGET

#Build the images
docker build -t datacats_solr solr/
docker build -t datacats_db postgresql/
docker build -t datacats_web web/

#Setup the virtualenv
id=$(cat setup_ckan.sh | docker run -i -a stdin \
    -e "BRANCH=$BRANCH" \
    -v $TARGET/venv:/usr/lib/ckan \
    -v $TARGET/ini:/etc/ckan/default \
    datacats_web /bin/bash -c "cat | sh")
test $(docker wait $id) -eq 0

#Run postgres
docker run -d --name="datacats_db_${NAME}" datacats_db

#Run Solr
docker run -d --name="datacats_solr_${NAME}" \
    -v $TARGET/venv/src/ckan/ckan/config/solr/schema.xml:/etc/solr/conf/schema.xml \
    datacats_solr

#Initialize the ckan .ini files
id=$(cat init_ini.sh | docker run -i -a stdin \
    -v $TARGET/venv:/usr/lib/ckan \
    -v $TARGET/ini:/etc/ckan/default \
    datacats_web /bin/bash -c "cat | sh")
test $(docker wait $id) -eq 0

#Initialize the database
id=$(docker run -i -a stdin \
    -v $TARGET/venv:/usr/lib/ckan \
    -v $TARGET/ini:/etc/ckan/default \
    --link "datacats_solr_${NAME}":solr \
    --link "datacats_db_${NAME}":db \
    datacats_web /usr/lib/ckan/bin/paster --plugin=ckan db init -c /etc/ckan/default/production.ini)
test $(docker wait $id) -eq 0

#copy the wsgi file into the mounted host volume
#I don't like the way this is done, but I can't think of a better way
cp web/apache.wsgi $TARGET/ini/apache.wsgi

#Run the web container
docker run --name="datacats_web_${NAME}" -it \
    -v $TARGET/venv:/usr/lib/ckan \
    -v $TARGET/ini:/etc/ckan/default \
    --link "datacats_solr_${NAME}":solr \
    --link "datacats_db_${NAME}":db \
    -p 80 \
    datacats_web
