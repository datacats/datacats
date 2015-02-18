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

Run a command within an extension
---------------------------------

Working on Core CKAN
--------------------
If you plan on working on core CKAN code, you should first ``unshallow`` your
copy of the CKAN source. By default datacats only checks out a shallow copy of
the CKAN github repo. This can cause minor headaches if you are planning on
contributing your code changes to core CKAN.

In the ``/ckan`` directory of your datacats environment, run the following git
command: ::

    git fetch --unshallow
