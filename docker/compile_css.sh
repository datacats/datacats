#!/bin/bash

cd /project
npm install less@1.7.5 > /dev/null 2>&1
node_modules/less/bin/lessc ckan/ckan/public/base/less/main.less

exit
