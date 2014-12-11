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

## Customize your project

In your "myproject" project directory you will find a "src"
directory with "ckan" and "ckanext-myproject" directories.
"ckanext-myproject" is a simple example extension that modifies the
CKAN site header to include the text "myproject".

Customize your Jinja2 templates in
"src/myproject/ckanext/myproject/templates", using
the files in "src/ckan/ckan/templates" as a reference.

Full CKAN extension possibilities are covered in the official CKAN
documentation.

See your changes locally by running:
```
datacats restart myproject
```

## Add existing extensions

Install any of the 100+ existing CKAN extensions.

1. Download or clone the extension in to your project's "src" folder.
2. Add the plugins and configuration options as required by the extension
   to the "ckan.ini" file in your project directory.
3. Run `datacats install myproject` to reinstall all project extensions
   and dependencies then restart the site.

## Deploy your project

Deploy your customized CKAN project to DataCats
```
datacats deploy myproject
```

Follow the prompts and your site will be live in minutes.
