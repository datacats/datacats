#! /bin/bash

#Script that gives you a test Datacats environment, to check the workflow works

#Build the images
docker build -t datacats_solr solr/
docker build -t datacats_db postgresql/
docker build -t datacats_web web/

#Setup the virtualenv
id=$(cat setup_ckan.sh | docker run -i -a stdin \
    -v $DATACATS_FILES/test/venv:/usr/lib/ckan/ \
    -v $DATACATS_FILES/test/ini:/etc/ckan/default \
    datacats_web /bin/bash -c "cat | sh")
test $(docker wait $id) -eq 0

#Run postgres
docker run -d --name=datacats_db_test datacats_db

#Run Solr
docker run -d --name=datacats_solr_test \
    -v $DATACATS_FILES/test/venv/src/ckan/ckan/config/solr/schema.xml:/etc/solr/conf/schema.xml \
    datacats_solr

#Initialize the ckan .ini files
id=$(cat init_ini.sh | docker run -i -a stdin \
    -v $DATACATS_FILES/test/venv:/usr/lib/ckan \
    -v $DATACATS_FILES/test/ini:/etc/ckan/default \
    datacats_web /bin/bash -c "cat | sh")
test $(docker wait $id) -eq 0

#Initialize the database
id=$(docker run -i -a stdin \
    -v $DATACATS_FILES/test/venv:/usr/lib/ckan \
    -v $DATACATS_FILES/test/ini/:/etc/ckan/default/ \
    --link datacats_solr_test:solr \
    --link datacats_db_test:db \
    datacats_web /usr/lib/ckan/bin/paster --plugin=ckan db init -c /etc/ckan/default/production.ini)
test $(docker wait $id) -eq 0

#copy the wsgi file into the mounted host volume
#I don't like the way this is done, but I can't think of a better way
cp web/apache.wsgi $DATACATS_FILES/test/ini/apache.wsgi

#Run the web container
docker run --name=datacats_web_test -it \
    -v $DATACATS_FILES/test/venv:/usr/lib/ckan \
    -v $DATACATS_FILES/test/ini/:/etc/ckan/default/ \
    --link datacats_solr_test:solr \
    --link datacats_db_test:db \
    -p 80:80 \
    datacats_web
