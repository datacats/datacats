# Copyright 2014-2015 Boxkite Inc.

# This file is part of the DataCats package and is released under
# the terms of the GNU Affero General Public License version 3.0.
# See LICENSE.txt or http://www.fsf.org/licensing/licenses/agpl-3.0.html

npm install less@1.7.5 > /dev/null 2>&1
node_modules/less/bin/lessc /project/ckan/ckan/public/base/less/main.less

exit
