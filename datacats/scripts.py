# Copyright 2014-2015 Boxkite Inc.

# This file is part of the DataCats package and is released under
# the terms of the GNU Affero General Public License version 3.0.
# See LICENSE.txt or http://www.fsf.org/licensing/licenses/agpl-3.0.html

from os.path import abspath, dirname

SCRIPTS_DIR = dirname(abspath(__file__)) + '/scripts'

SHELL = SCRIPTS_DIR + '/shell.sh'
PASTER = SCRIPTS_DIR + '/paster.sh'
PASTER_CD = SCRIPTS_DIR + '/paster_cd.sh'
WEB = SCRIPTS_DIR + '/web.sh'
KNOWN_HOSTS = SCRIPTS_DIR + '/known_hosts'
SSH_CONFIG = SCRIPTS_DIR + '/ssh_config'
PURGE = SCRIPTS_DIR + '/purge.sh'
RUN_AS_USER = SCRIPTS_DIR + '/run_as_user.sh'
CLEAN_VIRTUALENV = SCRIPTS_DIR + '/clean_virtualenv.sh'
INSTALL_REQS = SCRIPTS_DIR + '/install_reqs.sh'
INSTALL_PACKAGE = SCRIPTS_DIR + '/install_package.sh'
MIGRATE_BACKUP = SCRIPTS_DIR + '/migrate_backup.sh'
MIGRATE = SCRIPTS_DIR + '/migrate.sh'
COMPILE_LESS = SCRIPTS_DIR + '/compile_less.sh'
CHECK_CONNECTIVITY = SCRIPTS_DIR + '/check_connectivity.sh'
DATAPUSHER = SCRIPTS_DIR + '/datapusher.sh'
INSTALL_POSTGIS = SCRIPTS_DIR + '/install_postgis.sh'
ADJUST_DEVINI = SCRIPTS_DIR + '/adjust_devini.py'
UPDATE_ADD_ADMIN = SCRIPTS_DIR + '/update_add_admin.sh'
INSTALL_EXTRA_PACKAGES = SCRIPTS_DIR + '/install_extra_packages.sh'
