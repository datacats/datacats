# Copyright 2014-2015 Boxkite Inc.

# This file is part of the DataCats package and is released under
# the terms of the GNU Affero General Public License version 3.0.
# See LICENSE.txt or http://www.fsf.org/licensing/licenses/agpl-3.0.html

from sys import stdout

from datacats.cli.create import confirm_password
from datacats.validate import valid_deploy_name
from datacats.error import DatacatsError


def deploy(environment, opts, profile):
    """Deploy environment to production DataCats.com cloud service

Usage:
  datacats deploy [--create] [ENVIRONMENT [TARGET_NAME]]

Options:
  --create                Create a new environment on DataCats.com instead
                          of updating an existing environment

ENVIRONMENT may be an environment name or a path to a environment directory.
Default: '.'

TARGET_NAME is the name of the environment on DataCats.com. Defaults to
the environment name.
"""

    target_name = opts['TARGET_NAME']
    if target_name is None:
        target_name = environment.name

    if not valid_deploy_name(target_name):
        raise DatacatsError(" `{target_name}` target name for deployment can't be accepted.\n"
                            "Can't have http://{target_name}.datacats.io for your datcat URL\n"
                            "Please choose a target name at least 5 characters long,\n"
                            "and containing only lowercase letters and numbers\n"
                            .format(target_name=target_name))

    if opts['--create']:
        profile.create(environment, target_name)

    profile.deploy(environment, target_name, stdout)
    print "Deployed source to http://{0}.datacats.io".format(target_name)

    if opts['--create']:
        try:
            pw = confirm_password()
            profile.admin_password(environment, target_name, pw)
        except KeyboardInterrupt:
            pass
