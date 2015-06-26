Change Log
==========

1.0.1
-----

2015-06-26

- fix for a bug in start/restart that would remove site settings
  when passing a port or address option
- logs: new --datapusher option to view datapusher logs
- tweak: new --site option to specify site to modify
- fix for install --clean command not reinstalling ckanapi into
  virtualenv

1.0.0
-----

2015-06-24

- new support for multiple sites (DBs, files etc.) per environment
- new support for datapusher
- new support for ckanext-spatial
- new migrate command: migrate data directory formats between
  pre-multisite and post-multisite versions of datacats
- new reset command: reset DBs, files etc. to a default post-create
  state for a site
- init, create: now add postgis SQL to new DBs created
- create: now includes datapusher in the source directory by default
- tweak: new command can add postgis SQL to existing DBs
- lessc now streams output to show errors
- start, reload: new --no-watch option to prevent automatic paster
  reload on file changes, useful when testing updates to static files
- create, init, logs, open, paster, purge, reload, reset, shell,
  start, stop: new --site option to specify site
- bigger, shinier tracebacks and error messages

0.11.2
------

2015-06-19

- fix for a second deployment regression

0.11.1
------

2015-06-15

- fix for a deployment regression

0.11.0
------

2015-06-05

- workaround for common TLS error with boot2docker and recent openssl
- less: new command to compile less files to css
- new script datacats-lesscd to monitor less files for changes and
  automatically rebuild css files
- start/reload: errors now displayed immediately instead of prompting user
  to run "datacats logs"
- install: now verbose, use --quiet for old behavior
- install: now checks connectivity to pypi before starting
- create/init/install/start/reload: --syslog send log messages to syslog
- deploy: improved error reporting
- improved error messages when boot2docker containers are missing

0.10.0
------

2015-05-19

- create/start/reload --address=IP: choose the IP address to bind
  for serving ckan. allows use of datacats to serve public sites directly
  (linux only)
- shell --detach: run commands in the background
- purge: prompt user to confirm deletion unless -y specified
- better error reporting on failures during setup
- better error reporting when boot2docker isn't running
- better error reporting when deploy command fails
- fix docker build scripts to run on OSX
- fix reload incorrectly reporting already running when some containers
  have stopped


0.9.3
-----

2015-05-12

- fix for ConnectionError on OSX for some users

0.9.2
-----

2015-05-06

- fix for deploy with docker 1.6

0.9.1
-----

2015-05-05

- fix for shell command when containers already running

0.9
---

2015-05-05

- install --clean: install dependencies to an empty virtualenv
  to support running datacats with older ckan versions (local only)
- install: install packages before package requirements so that packages
  in the environment may override dependencies listed in other
  packages
- deploy: show the URL of the deployed site like start does for local sites
- create: warn when the name chosen may not be used with deploy
- for for negotiating docker API version so that docker-py and docker don't
  always need to be the exact matching versions
- fix for a breaking API change in the docker 1.6 API
- fix for docker-py constant moved to a different module in 1.2.0

0.8
---

2015-03-27

- create, init: fix for race between db creation and init
- create, init, start, reload: fix for automatic port selection
- install, start, reload, open, shell, paster:
  test for datadir condition before running commands that
  depend on it to prevent failures
- info: display if datadir is missing or damaged
- start: fix for false "already running" message after
  restarting host machine
- paster: stop creating 0-size .bash_profile files
  in ckan+extension module directories
- purge: work even when some directories are missing


0.7
---

2015-03-15

- initial public release
