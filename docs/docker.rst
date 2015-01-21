.. _docker:

How DataCats uses Docker
========================

DataCats puts CKAN inside of Docker containers. Each DataCats CKAN environment
is actually at least 3 different Docker containers. You can see this by running
``datacats info`` inside your project directory: ::

    $ datacats info
    Project name: datapusher
    CKAN version: master
    Default port: 5716
     Project dir: /Users/dz/source/dcats-envs/datapusher
        Data dir: /Users/dz/.datacats/datapusher
      Containers: web postgres solr
    Available at: http://boot2docker:5716/

You can see we have a ``web`` container, a ``postgres`` container, and a ``solr``
container. Each is responsible for the corresponding piece of CKAN - the postgres
container is running the database, the solr container is running the solr search
engine, and web is running CKAN itself, connecting to solr and postgres as needed.

From a Docker perspective, you can see these containers by running ``docker ps``: ::

    $ docker ps
    CONTAINER ID        IMAGE                      COMMAND                CREATED             STATUS              PORTS                    NAMES
    a3a0654c3f0a        datacats/web:latest        "/scripts/web.sh"      26 hours ago        Up 26 hours         0.0.0.0:5716->5000/tcp   datacats_web_datapusher
    2656f1dd7ecc        datacats/search:latest     "/usr/share/tomcat6/   26 hours ago        Up 26 hours         8080/tcp                 datacats_solr_datapusher
    12dfb5f7950f        datacats/postgres:latest   "/docker-entrypoint.   26 hours ago        Up 26 hours         5432/tcp                 datacats_postgres_datapusher

You can see that each container is using a corresponding Docker image. An image
is like a template used to run each container.

The most important thing to remember about your DataCats containers is that they
are disposable. You can kill any of these containers without worry, for example: ::

    $ docker rm -f datacats_web_datapusher
    $ docker ps
    CONTAINER ID        IMAGE                      COMMAND                CREATED             STATUS              PORTS               NAMES
    2656f1dd7ecc        datacats/search:latest     "/usr/share/tomcat6/   27 hours ago        Up 27 hours         8080/tcp            datacats_solr_datapusher
    12dfb5f7950f        datacats/postgres:latest   "/docker-entrypoint.   27 hours ago        Up 27 hours         5432/tcp            datacats_postgres_datapusher

No big deal, let's create a new container to serve our CKAN: ::

    $ datacats reload
    Starting web server at http://boot2docker:5716/...

The second important thing to note is that containers are more or less immutable -
stuff inside a container doesn't change. This is not strictly true. Docker does
allow us to go inside a container and do whatever we want. However, this would
make our containers no longer disposable, since there is now state encapsulated
inside of them we presumably wish to not lose. Because of this, DataCats treats
containers as stateless and disposable.
