Quickstart
---------------

Install Docker_. Then, in a shell, run:  ::

    pip install datacats
    datacats pull
    datacats create myckan

This will create a new CKAN dev environment, with all the source code
in the **myckan** directory. You can now start using it. To open your new
environment in a browser, run: ::

    datacats open myckan

Install a new CKAN extension: ::

    cd myckan/
    git clone git@github.com:ckan/ckanext-pages.git
    datacats install

Edit the development.ini file and add the extension to the CKAN config: ::

    ckan.plugins = pages

Reload CKAN for the config changes to take effect: ::

    datacats reload

Finally, deploy your project to the DataCats.com cloud: ::

    datacats deploy --create

.. _Docker: https://docs.docker.com/installation/


