Change Log
==========

0.9.2
-----

- fix for deploy with docker 1.6

0.9.1
-----

- fix for shell command when containers already running

0.9
---

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

- initial public release
