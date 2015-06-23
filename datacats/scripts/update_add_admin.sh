#!/bin/bash
# This expects /input/admin.json to be the generated admin.json file

. /usr/lib/ckan/bin/activate

if ckanapi action user_show -c /project/development.ini id=admin; then
    # Step 1: Grab the user's current info, step 2: add new pw, step 3: apply new info
    ckanapi action user_show id=admin -c /project/development.ini | \
        python -c "from sys import stdin, stdout;from json import load, dump;\
obj = load(stdin);obj['password'] = load(open('/input/admin.json'))['password'];dump(obj, stdout)" | \
        ckanapi action user_update -i -c /project/development.ini
else
    ckanapi action user_create -i -c /project/development.ini < /input/admin.json
fi
