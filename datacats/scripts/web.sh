#!/bin/bash

# Copyright 2014-2015 Boxkite Inc.

# This file is part of the DataCats package and is released under
# the terms of the GNU Affero General Public License version 3.0.
# See LICENSE.txt or http://www.fsf.org/licensing/licenses/agpl-3.0.html

set -e

trap 'kill $!' SIGUSR1
export HOME="/var/www/storage"

port=5000

if [ "$1" = "true" ]; then
	port=80
fi

while true; do
	# fix our development.ini
	if [ "$2" = "True" ]; then
		/scripts/adjust_devini.py "$(ip route get 8.8.8.8 | awk 'NR==1 {print $NF}')" "5000"
	fi

	# production
	if [ "$1" = "True" ]; then
		/usr/sbin/apachectl -DFOREGROUND
	elif [ "$3" == "True" ]; then
		sudo -u www-data /usr/lib/ckan/bin/paster --plugin=ckan serve \
			/project/development.ini --reload &
	else
		# Don't reload
		sudo -u www-data /usr/lib/ckan/bin/paster --plugin=ckan serve \
			/project/development.ini &
	fi

	wait && exit
done
