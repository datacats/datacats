#!/bin/bash
# This expects /input/admin.json to be the generated admin.json file

if /usr/lib/ckan/bin/ckanapi action user_show -c /project/development.ini id=admin; then
    # Generate a file with info on the user and add a password w/ Python
    /usr/lib/ckan/bin/ckanapi action user_show id=admin -c /project/development.ini > info.json
    python -c "from json import dump, load;obj=load(open('info.json'));obj['password'] = load(open('/input/admin.json'))['password'];dump(obj, open('info.json', 'w'))"
    # Actually update the user
    /usr/lib/ckan/bin/ckanapi action user_update -i -c /project/development.ini < info.json
else
    /usr/lib/ckan/bin/ckanapi action user_create -i -c /project/development.ini < /input/admin.json
fi
