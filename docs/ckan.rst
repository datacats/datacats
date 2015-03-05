CKAN Reference
==============

This page contains a few recipes on how to use DataCats to easily accomplish
common CKAN tasks. We're always looking for more. If you have examples of your
own you wish to share, please submit a pull request.

Run an interactive Paster Shell
-------------------------------
Anywhere within your datacats environment directory, run::

    datacats shell . paster --plugin=pylons shell

Load data from one CKAN into another
------------------------------------

Run the CKAN test suite
-----------------------

Run Celery tasks
----------------
If you have an extension that is using Celery, make sure that the extension is
installed in your environment with ``datacats install``. You can then run a
container with a celery daemon like this: ::

    datacats paster celeryd


Working on Core CKAN
--------------------
If you plan on working on core CKAN code, you should first ``unshallow`` your
copy of the CKAN source. By default datacats only checks out a shallow copy of
the CKAN github repo. This can cause minor headaches if you are planning on
contributing your code changes to core CKAN.

In the ``/ckan`` directory of your datacats environment, run the following git
command: ::

    git fetch --unshallow
