# DataCats

The easiest way to develop and deploy CKAN cross-platform


## Install

OSX | Linux | Windows
--- | --- | ---
1. Install boot2docker | 1. Install docker | coming soon
2. `pip install datacats` | 2. `pip install datacats` |


## Start a CKAN project

```
datacats create myproject
```

This will create a new project called "myproject" in the current
directory, new data files in "~/.datacats/myproject" and start
your project containers, serving your new site locally.

```
Creating project "myproject".............
Site available at http://localhost:5425/
admin user password:
```

Open your brower to the address shown to try out your new site.


## Customize your project

In your project directory you will find
"ckan" and "ckanext-myproject" subdirectories.
"ckanext-myproject" is a simple example extension that modifies
some templates and adds some static files.

Customize your Jinja2 templates in
"ckanext-myproject/ckanext/myproject/templates", using
the files in "ckan/ckan/templates" as a reference.

Full CKAN extension possibilities are covered in the official CKAN
documentation.

The site is run with "paster serve --reload" by default so your
Changes to templates and source files should be visible almost immediately
after saving them. Refresh your browser window to see the changes.

For changes to configuration files and
new template files use "reload" to force a site reload.

```
datacats reload myproject
```


## Add existing extensions

Install any of the 100+ existing CKAN extensions.

First download or clone the extension in to your project directory,
then add the plugins and configuration options as required by the extension
to the "development.ini" file.

Reinstall all project extensions and reload the site with:
```
datacats install myproject
```

Refresh your browser window to see the changes.


## Deploy your project

Deploy your customized CKAN project to the DataCats cloud service.
```
datacats deploy myproject
```

Follow the prompts and your site will be live in minutes.

