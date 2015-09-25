Quickstart
---------------

Install Docker_. Then, in a shell, run:  ::

    pip install datacats
    datacats pull
    datacats create myckan

This will create a new datacats source directory **myckan** and start
serving the site.
You can now start using it. To open your new site in a browser, run: ::

    datacats open myckan

Install a new CKAN extension: ::

    cd myckan/
    git clone git@github.com:ckan/ckanext-pages.git
    datacats install

Edit the development.ini file and add the extension to the CKAN config: ::

    ckan.plugins = pages

Reload CKAN for the config changes to take effect: ::

    datacats reload

.. _Docker: https://docs.docker.com/installation/


