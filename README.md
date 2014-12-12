# DataCats

The easiest way to develop and deploy CKAN cross-platform


## Install

1. Install docker (linux) or boot2docker (mac)
2. `pip install datacats` or clone and install this repo


## Start a CKAN project

```
datacats create myproject
```

This will create a new project called "myproject" in the current
directory, new data files in "~/.datacats/myproject and start
your project containers, serving your new site locally.

Open your brower to the address shown to try out your new site.


## Customize your project

First "cd" into your project directory so that the
datacats command knows which project to work on:
```
cd myproject
```

In this directory you will find a "src"
directory with "ckan" and "ckanext-myproject" directories.
"ckanext-myproject" is a simple example extension that modifies the
CKAN site header to include the text "myproject".

Customize your Jinja2 templates in
"src/myproject/ckanext/myproject/templates", using
the files in "src/ckan/ckan/templates" as a reference.

Full CKAN extension possibilities are covered in the official CKAN
documentation.

Test your changes locally by running:
```
datacats restart
```

Refresh your browser window to see the changes.


## Add existing extensions

Install any of the 100+ existing CKAN extensions.

First download or clone the extension in to your project's "src" folder,
then add the plugins and configuration options as required by the extension
to the "ckan.ini" file in your project directory.

Then reinstall all project extensions and dependencies found under "src" with:
```
datacats install
```

Refresh your browser window to see the changes.


## Deploy your project

Deploy your customized CKAN project to the DataCats cloud service.
```
datacats deploy
```

Follow the prompts and your site will be live in minutes.

