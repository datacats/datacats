#!/bin/bash

# Copyright 2014-2015 Boxkite Inc.

# This file is part of the DataCats package and is released under
# the terms of the GNU Affero General Public License version 3.0.
# See LICENSE.txt or http://www.fsf.org/licensing/licenses/agpl-3.0.html

set -e

trap 'kill $!' SIGUSR1

while true; do
	sudo -u www-data /usr/lib/ckan/bin/paster --plugin=ckan serve \
		/project/development.ini --reload &
	wait && exit
done
