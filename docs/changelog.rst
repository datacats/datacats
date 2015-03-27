Change Log
==========

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
