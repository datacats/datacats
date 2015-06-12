#!/bin/bash

# Copyright 2014-2015 Boxkite Inc.

# This file is part of the DataCats package and is released under
# the terms of the GNU Affero General Public License version 3.0.
# See LICENSE.txt or http://www.fsf.org/licensing/licenses/agpl-3.0.html

set -e

trap 'kill $!' SIGUSR1

while true; do
	# fix our development.ini
	if [ "$2" = "true" ]; then
		python -c "from ConfigParser import SafeConfigParser;cp = SafeConfigParser();cp.read('development.ini');cp.set('app:main', 'ckan.site_url', '$(ip route get 8.8.8.8 | awk 'NR==1 {print $NF}')'); cp.write(open('development.ini', 'w'))"
	fi

	# production
	if [ "$1" = "true" ]; then
		/usr/bin/apachectl -DFOREGROUND
	else
		sudo -u www-data /usr/lib/ckan/bin/paster --plugin=ckan serve \
			/project/development.ini --reload &r
	fi

	wait && exit
done
