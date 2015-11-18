FAQ
==============

This page contains a few recipes on how to use DataCats to easily accomplish
common CKAN tasks. We're always looking for more. If you have examples of your
own you wish to share, please submit a pull request.

Run an interactive Paster Shell
-------------------------------
Anywhere within a datacats source directory, run::

    datacats shell . paster --plugin=pylons shell

Run Celery tasks
----------------
If you have an extension that is using Celery, make sure that the extension is
installed with ``datacats install``. You can then run a
container with a celery daemon like this: ::

    datacats paster celeryd

Cleaning the database doesn't work.
-----------------------------------
When running the command ``paster db clean``, the command will freeze as it is
blocked from cleaning the database if CKAN is connected to the db (`see issue`_)
. To get around this, stop the ``web`` docker container for your site
first, then issue the command, and reload datacats: ::

    docker stop datacats_web_myckan
    datacats paster db clean
    datacats reload

.. _see issue: https://github.com/ckan/ckan/issues/2306

InsecurePlatformWarning
-----------------------
If you get an ``InsecurePlatformWarning``, this is an issue with the ``urllib3``
library - `more info here`_. If you'd like to make it go away, you can run the
following_: ::

    pip install pyopenssl ndg-httpsclient pyasn1

.. _more info here: https://urllib3.readthedocs.org/en/latest/security.html
.. _following: https://urllib3.readthedocs.org/en/latest/security.html#pyopenssl

Working on Core CKAN
--------------------
If you plan on working on core CKAN code, you should first ``unshallow`` your
copy of the CKAN source. By default datacats only checks out a shallow copy of
the CKAN github repo. This can cause minor headaches if you are planning on
contributing your code changes to core CKAN.

In the ``/ckan`` directory of your datacats source directory, run the following git
command: ::

    git fetch --unshallow

boot2docker - Upgrading or Recovering from failures
---------------------------------------------------
Sometimes you will need to upgrade boot2docker. Or, you may encounter a problem
where the boot2docker VM is unreachable or otherwise broken. Whatever the case,
if you had to delete the boot2docker VM and create a new one, follow these steps
to get your CKAN sites up and running again:

- First, you will need to pull the CKAN docker images again: ::

    datacats pull

- Clean your datacats environments so they can be re-initialized: ::

    cd myckan
    datacats purge

- Finally, initialize the environment: ::

    datacats init

Remove obsolete Docker images
-----------------------------
Building Docker images locally will retain the image snapshots and eventually 
raise a "Docker APIError 500: no space left on device".

To free up hard drive space, remove only the obsolete docker images with::

  rmi $(docker images -q)

Remember that the user running this command must be in the ``docker`` group.
``rmi`` will only remove images which are not currently running as containers.
This step is largely risk-free, as you can restore any images by simply pulling 
or building them again - only local modifications to images can be lost.

