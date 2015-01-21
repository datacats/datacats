User Guide
==========

What is DataCats
----------------

CKAN can be very difficult to develop and deploy. The aim of DataCats is to make
this easier and bring CKAN within reach for a much wider audience.

DataCats relies on Docker_ to container-ize the CKAN environment. If you don't
know much about Docker, it doesn't matter. You need to know very little about
how Docker works in order to use DataCats. If you wish to know more about how
this project works, take a look at :ref:`docker`.

.. _Docker: https://www.docker.com/
.. _How DataCats uses Docker: :ref:`docker`


Installation
------------

Install Docker
""""""""""""""
You will need to install Docker first:

Linux
#####
Follow the instructions over at the `Docker Docs`_

.. _Docker Docs: https://docs.docker.com/installation/ubuntulinux/

OSX
###
You will need `boot2docker`_, the standard way to get Docker running on your Mac.

.. _boot2docker: https://docs.docker.com/installation/mac/

Windows
#######
Windows support is coming soon. For now, you can run DataCats inside any Linux
Virtual Machine. Simply install VirtualBox or VMWare, create a Ubuntu VM and
`install Docker`__ on it.

__ `Docker Docs`_

Install DataCats
"""""""""""""""""""""
The easiest way to install DataCats is with ``pip``. In your shell run: ::

    pip install datacats

If you do not have ``pip`` installed, you can install it by running: ::

    easy_install pip


Getting Started
---------------

Create an environment
"""""""""""""""""""""
Create a CKAN development environment. Open a shell and run: ::

    datacats create kittyville

This will take a few minutes. DataCats will pull the Docker images needed to
create your environment. This will only happen **once**. Those images are then
re-used for all subsequent environments you create.

Once done, a CKAN environment is created for you in the directory ``kittyville``.
You will be prompted to create an admin password for your instance. You can
use this password to log into your CKAN site.A message will also appear in your
promprt at the end of the create command, with the address of where your CKAN
instance is running. To open that address easily at any time, you can always run: ::

    datacats open kittyville

Let's see what is inside our new project directory. ``cd`` into the directory
and take a look at the file structure. You should see something like this: ::

    kittyville/
    |-ckan/
    |-ckanext-kittyville/
    |-development.ini
    |-schema.xml

The ``ckan/`` directory is the `source code of the CKAN project`_. By default,
DataCats will initialize each project with the lastest version of CKAN. You can
change the version you wish to run by going into that directory and checking
out a different branch or tag. Alternatively, if you know ahead of time which
version of CKAN you wish to run, you can pass a flag directly to the
``datacats create`` command.

The ``ckanext-kittyville`` directory is an auto-generated sample `CKAN extension`_.
While you can use CKAN in it's default form, most organizations and governments
deploying CKAN customize it in some way. Many forms of customization, such as
`designing your own custom theme`_, do not require a deep knowledge of CKAN. The
``ckanext-kittyville`` extension gives you a very basic skeleton which you can
use to get started.

The ``development.ini`` file holds all the configuration options for your CKAN
environment. All of these options are described here_. Open this file and find a
line that starts with ``ckan.plugins``. It will look something like this: ::

    ckan.plugins = datastore kittyville_skin

The ``kittyville_skin`` is the extension endpoint for our kittyville extension,
defined in ``ckanext-kittyville/setup.py``. We can enable and disable our
extension by adding it or removing it from the plugins list above.

Extensions & Customization
---------------------------
To see how this works, let us install another extension into our environment.
A good one to use is pages_, which adds a simple CMS to CKAN so we can add
custom content pages to our site. First, clone the pages source code into your
environment. In the ``kittyville/`` directory, run: ::

    git clone git@github.com:ckan/ckanext-pages.git

This will clonse the source into the ckanext-pages/ directory, right next to
``ckan/`` and ``ckanext-kittyville/`` like so: ::

    kittyville/
    |-ckan/
    |-ckanext-kittyville/
    |-ckanext-pages/
    |-development.ini
    |-schema.xml

Next, install this extension into your environment by running: ::

    datacats install

The install command will iterate through your environment directory and install
all your extensions. After this is complete, we need to open the ``development.ini``
file again and add the pages extension to our list of installed extensions: ::

    ckan.plugins = datastore kittyville_skin pages

Finally, reload CKAN for the config changes to take effect: ::

    datacats reload

And our extension is now live! Open up your CKAN site, log into it, and you should
see a button in the top toolbar that will let you create custom content pages.

Deploying
---------
To deploy your brand new CKAN instance to the DataCats managed cloud, simply run: ::

    datacats deploy

This will create a new deployment with all your settings and installed extensions,
as well as the correct CKAN version.

If you prefer to now use the DataCats cloud, you can deploy CKAN using DataCats
on your own server. This is outside of the scope for this documentation, but the
process is similar to following this guide, with some minor but important changes.
You will want to make sure your CKAN is running a production web server,
you will need to set up DNS and, optionally, emails, backups, logs and other
miscellaneous items. If you plan to go this route, you should understand a bit
more about how DataCats works under-the-hood_.

.. _source code of the CKAN project: http://github.com/ckan/ckan
.. _CKAN extension: http://extensions.ckan.org/
.. _extension guide: http://docs.ckan.org/en/latest/extensions/
.. _designing your own custom theme: http://docs.ckan.org/en/latest/theming/index.html
.. _here: http://docs.ckan.org/en/latest/maintaining/configuration.html
.. _pages: http://github.com/ckan/ckanext-pages
.. _under-the-hood: :ref:`docker`
