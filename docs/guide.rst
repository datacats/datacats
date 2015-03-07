User Guide
==========

What is datacats
----------------

CKAN can be quite difficult to develop and deploy, especially for beginners.
The aim of datacats is to make this easier and bring CKAN within reach for a
much wider audience.

datacats relies on Docker_ to "containerize" the CKAN environment. If you don't
know much about Docker, it doesn't matter. You need to know very little about
it in order to use datacats. If you wish to know more about how
this project works, take a look at :doc:`docker`.

.. _Docker: https://www.docker.com/

Installation
------------

Install Docker
""""""""""""""
You will need to install Docker first:

Linux
#####
Follow the instructions over at the `Docker Docs`_. Make sure to install the
Docker-maintained version of Docker, not the official Ubuntu-maintained version
of Docker, which is out-of-date.

.. _Docker Docs: https://docs.docker.com/installation/ubuntulinux/#docker-maintained-package-installation

OSX
###
You will need `boot2docker`_, the standard way to get Docker running on your Mac.

.. _boot2docker: https://docs.docker.com/installation/mac/

Windows
#######
Native Windows support is coming soon. For now, you can run datacats inside any Linux
Virtual Machine. Simply install VirtualBox or VMWare, create a Ubuntu VM and
`install Docker`__ on it.

__ `Docker Docs`_

Install datacats
"""""""""""""""""""""
The easiest way to install datacats is with ``pip``. In your shell run: ::

    pip install datacats

If you do not have ``pip`` installed, you can install it first by running: ::

    easy_install pip

As part of the install datacats will pull the Docker images needed to
create your environment. This will only happen **once**. Those images are then
re-used for all subsequent environments you create.

To update the Docker images manually run::

    datacats pull


Getting Started
---------------

Create a CKAN development environment. Open a shell and run: ::

    datacats create catstown

Once done, a CKAN environment is created for you in the directory ``catstown``.
You will be prompted to create an admin password for your instance. You can
use this password to log into your CKAN site.A message will also appear in your
prompt at the end of the create command, with the address of where your CKAN
instance is running. To open that address easily at any time, you can always run: ::

    datacats open catstown

.. note::

    All ``datacats`` commands work without having to specify the project to run
    them on, as long as you are within a datacats environment directory. For the
    above command, we could as well have ran: ::

        cd catstown/
        datacats open

Let's see what is inside our new environment directory. ``cd`` into the directory
and take a look at the file structure. You should see something like this: ::

    catstown/
    |-ckan/
    |-ckanext-catstowntheme/
    |-development.ini
    |-schema.xml

The ``ckan/`` directory is the `source code of the CKAN project`_. By default,
datacats will initialize each project with the lastest version of CKAN. You can
change the version you wish to run by going into that directory and checking
out a different branch or tag. Alternatively, if you know ahead of time which
version of CKAN you wish to run, you can pass a flag directly to the
``datacats create`` command.

The ``ckanext-catstowntheme`` directory is an auto-generated sample
`CKAN extension`_.
While you can use CKAN in it's default form, most organizations and governments
deploying CKAN customize it in some way. Many forms of customization, such as
`designing your own custom theme`_, do not require a deep knowledge of CKAN. The
``ckanext-catstowntheme`` extension gives you a very basic skeleton which you
can use to get started.

The ``development.ini`` file holds all the configuration options for your CKAN
environment. All of these options are described here_. Open this file and find a
line that starts with ``ckan.plugins``. It will look something like this: ::

    ckan.plugins = datastore text_preview recline_preview catstown_theme

The ``catstown_theme`` is the extension endpoint for our kittyville extension,
defined in ``ckanext-catstowntheme/setup.py``. We can enable and disable our
extension by adding it or removing it from the plugins list above.

Extensions & Customization
---------------------------
To see how this works, let us install another extension into our environment.
A good one to use is pages_, which adds a simple CMS to CKAN so we can add
custom content pages to our site. First, clone the pages source code into your
environment. In the ``catstown/`` environment directory, run: ::

    git clone git@github.com:ckan/ckanext-pages.git

This will clone the source into the ckanext-pages/ directory, right next to
``ckan/`` and ``ckanext-catstowntheme/`` like so: ::

    kittyville/
    |-ckan/
    |-ckanext-catstowntheme/
    |-ckanext-pages/
    |-development.ini
    |-schema.xml

Next, install this extension into your environment by running: ::

    datacats install

The install command will iterate through your environment directory and install
all your extensions. After this is complete, we need to open the ``development.ini``
file again and add the pages extension to our list of installed extensions: ::

    ckan.plugins = datastore text_preview recline_preview catstown_theme pages

Finally, reload CKAN for the config changes to take effect: ::

    datacats reload

And our extension is now live! Open up your CKAN site, log into it, and you should
see a button in the top toolbar that will let you create custom content pages.

Deploying
---------
To deploy your brand new CKAN instance to the DataCats.com managed cloud, simply run: ::

    datacats deploy --create

This will create a new deployment with all your settings and installed extensions,
as well as the correct CKAN version.

If you prefer to use your own server, you can still deploy CKAN using datacats.
This is outside of the scope for this documentation, but the
process is similar to following this guide, with some minor but important changes.
You will want to make sure your CKAN is running a production web server,
you will need to set up DNS and, optionally, emails, backups, logs and other
miscellaneous items. If you plan to go this route, you should understand a bit
more about how datacats works under-the-hood. See :doc:`docker`

Shell Access
------------
To run an interactive shell within your CKAN environment, run: ::

    datacats shell catstown

Where ``catstown`` is your datacats environment name. The shell will immediately
drop you inside your project directory, and it will activate the ``virtualenv``.
The shell is useful if you want to run admin ``paster`` tasks such as database
migrations, or you simply want to poke around your CKAN instance.

Paster Commands
---------------
To quickly run CKAN ``paster`` commands, you can do the following: ::

    datacats paster sysadmin add joe

Take a look at the `CKAN paster page`_ for a list of available commands.

.. note::

    With datacats, you don't need to worry about activating your ``virtualenv``,
    and you do not need to pass the ``--config`` option to paster. You also
    do not need to specify the ``--plugin=ckan`` option.
    datacats handles this for you automatically.

If you have ``paster`` commands inside your CKAN extensions, you can ``cd`` into
the extension directory and run the command from there: ::

    cd ckanext-archiver/
    datacats paster archiver clean

Logs
----
To see the log output of your CKAN: ::

    datacats logs

.. _source code of the CKAN project: http://github.com/ckan/ckan
.. _CKAN extension: http://extensions.ckan.org/
.. _extension guide: http://docs.ckan.org/en/latest/extensions/
.. _designing your own custom theme: http://docs.ckan.org/en/latest/theming/index.html
.. _here: http://docs.ckan.org/en/latest/maintaining/configuration.html
.. _pages: http://github.com/ckan/ckanext-pages
.. _CKAN paster page: http://docs.ckan.org/en/latest/maintaining/paster.html
