#!/bin/bash

# Copyright 2014-2015 Boxkite Inc.

# This file is part of the DataCats package and is released under
# the terms of the GNU Affero General Public License version 3.0.
# See LICENSE.txt or http://www.fsf.org/licensing/licenses/agpl-3.0.html

set -e

userdel www-data

useradd -d /project -u $(stat -c %u /project) -M -s /bin/bash shell

shift
dir=/project/"$1"
shift
command="${@} --config=/project/development.ini"
sudo -i -u shell bash -c "cd $dir ; $command"
