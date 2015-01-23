.. _docker:

How datacats uses Docker
========================

Images and Containers
---------------------

datacats puts CKAN inside of Docker containers. Each datacats CKAN environment
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

Throw-away containers
---------------------

The most important thing to remember about your datacats containers is that they
are `disposable`_. You can kill any of these containers without worry, for example: ::

    $ docker rm -f datacats_web_datapusher
    $ docker ps
    CONTAINER ID        IMAGE                      COMMAND                CREATED             STATUS              PORTS               NAMES
    2656f1dd7ecc        datacats/search:latest     "/usr/share/tomcat6/   27 hours ago        Up 27 hours         8080/tcp            datacats_solr_datapusher
    12dfb5f7950f        datacats/postgres:latest   "/docker-entrypoint.   27 hours ago        Up 27 hours         5432/tcp            datacats_postgres_datapusher

No big deal, let's reload. This will create a new container to serve our CKAN: ::

    $ datacats reload
    Starting web server at http://boot2docker:5716/...

Stateless development
---------------------

The second important thing to note is that containers are more or less immutable -
stuff inside a container doesn't change. This is not strictly true. Docker does
allow us to go inside a container and do whatever we want. However, this would
make our containers no longer disposable, since there is now state encapsulated
inside of them we presumably wish to not lose. Because of this, datacats treats
containers as stateless and disposable.

This comes with a couple of important exceptions. Our source files and our
database files. These are things that are obviously not
stateless - both our source and our database change constantly as we develop and
use our CKAN site. Our source files - the project directory - is mounted inside
each web container when that container is started.

Why is all of this important? First reason is maintainability. We have all of our
messy moving parts encapsulated inside two discrete places - our source directory
and our database. Everything else is disposable and we don't have to worry about it
breaking.

DevOps
------
Second important reason is deployment. Because all of CKAN is running
inside Docker, everything is in tightly controlled image environments that are immune to changes.
We can deploy these same images to a production server and achieve an extremly high
level of `development-production parity`_.

Note also that each of our containers is responsible for running `exactly one process`_.
postgres container is just running postgres, solr is running solr, and web is running
paster or apache. Each of these services is as simple as can be, and this architecture
also allows us to `scale out`_ each of these parts independently.

Here is an illustrative example to wrap your mind around this architecture.
Let's perform a database migration: ::

    datacats paster --plugin=ckan db upgrade

In the few seconds that this is running, run the following command: ::

    $ docker ps
    CONTAINER ID        IMAGE                      COMMAND                CREATED             STATUS              PORTS                    NAMES
    56392375f4e9        datacats/web:latest        "/scripts/shell.sh -   1 seconds ago       Up 1 seconds        5000/tcp                 grave_mayer
    1e6b951d172b        datacats/web:latest        "/scripts/web.sh"      46 minutes ago      Up 46 minutes       0.0.0.0:5716->5000/tcp   datacats_web_datapusher
    2656f1dd7ecc        datacats/search:latest     "/usr/share/tomcat6/   27 hours ago        Up 27 hours         8080/tcp                 datacats_solr_datapusher
    12dfb5f7950f        datacats/postgres:latest   "/docker-entrypoint.   27 hours ago        Up 27 hours         5432/tcp                 datacats_postgres_datapusher

We see there are two containers running from the image template ``datacats/web``.
One of those containers is our database migration. After the migration is done,
`the container is destroyed`_. It may take you some time to get used to this way
of doing things. After all, we just created and destroyed a perfectly good
"virtual machine" just so we can run a 5 second script. How wasteful! But this
is the primary paradigm of how Docker and containers work. The sooner you get
used to it, the happier your experience with Docker will be.

.. note::
    Traditionaly, we would ``ssh`` into our web server and run the migration scripts.
    However, remember that our containers are running only one process each, so they
    don't have an ssh daemon listening which would allow us to ``ssh`` into the server,
    even if we wanted to.

.. _development-production parity: http://12factor.net/dev-prod-parity
.. _exactly one process: http://12factor.net/processes
.. _scale out: http://12factor.net/concurrency
.. _disposable: http://12factor.net/disposability
.. _the container is destroyed: http://12factor.net/admin-processes
