#!/bin/bash

# Copyright 2014-2015 Boxkite Inc.

# This file is part of the DataCats package and is released under
# the terms of the GNU Affero General Public License version 3.0.
# See LICENSE.txt or http://www.fsf.org/licensing/licenses/agpl-3.0.html

set -e

trap 'kill $!' SIGUSR1

port=5000

if [ "$1" = "true" ]; then
	port=80
fi

while true; do
	# fix our development.ini
	if [ "$2" = "true" ]; then
		/scripts/adjust_devini.py "$(ip route get 8.8.8.8 | awk 'NR==1 {print $NF}')" "$port"
	fi

	# production
	if [ "$1" = "true" ]; then
		/usr/bin/apachectl -DFOREGROUND
	else
		sudo -u www-data /usr/lib/ckan/bin/paster --plugin=ckan serve \
			/project/development.ini --reload &
	fi

	wait && exit
done
