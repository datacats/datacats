#!/bin/bash

set -e

datacats create site1 -bn --ckan $1
[ ! -d site1/ckanext-site1theme ]
[ "$(echo `datacats list`)" == "site1" ]
datacats info site1
datacats start site1 8999
datacats info site1
datacats shell site1 echo hello from inside site1
datacats logs site1
datacats create site2 -n --ckan $1
[ -d site2/ckanext-site2theme ]
[ "$(echo `datacats list`)" == "site1 site2" ]
### FIXME: Redis doesn't pull right on CircleCI's docker storage driver (btrfs)
#datacats tweak --add-redis site1
datacats reload site1
#[ "$(docker ps | grep datacats_redis_site1_primary | wc -l)" == 1 ]
[ "$(cat ~/.datacats/site1/sites/primary/run/development.ini | egrep 127.0.0.1 | wc -l | xargs)" == 0 ]
datacats purge -y site1
[ "$(echo `datacats list`)" == "site2" ]
datacats init site1 -n
datacats reset -yn site1
datacats install site1
datacats migrate -y -r 1 site1
[ -e ~/.datacats/site1/postgres ]
datacats purge -y site1
datacats init -n site1
datacats migrate -y -r 1 site1
datacats migrate -y -r 2 site1
datacats init site1 -s two -n
datacats install --clean site1
datacats shell site1 cat /usr/lib/ckan/bin/ckanapi
datacats start -s two site1
[ -e ~/.datacats/site1/sites/primary/postgres ]
[ $(datacats --version | wc -l) == 1 ]
