#!/usr/bin/env python2

from ConfigParser import SafeConfigParser
import sys

cp = SafeConfigParser()
cp.read('/project/development.ini')

cp.set('app:main', 'ckan.site_url', 'http://{}:{}'.format(sys.argv[1], sys.argv[2]))

with open('/project/development.ini', 'w') as fp:
    cp.write(fp)
