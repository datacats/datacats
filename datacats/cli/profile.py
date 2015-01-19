# Copyright 2014-2015 Boxkite Inc.

# This file is part of the DataCats package and is released under
# the terms of the GNU Affero General Public License version 3.0.
# See LICENSE.txt or http://www.fsf.org/licensing/licenses/agpl-3.0.html

from os.path import exists
from socket import gethostname
from getpass import getuser

from datacats.userprofile import UserProfile
from datacats.docker import web_command

def get_working_profile():
    """
    Return a complete UserProfile with ssh keys configured either
    by loading an existing profile or setting one up with the
    user interactively.
    """
    profile = UserProfile()

    if profile.ssh_private_key is None or not exists(
            profile.ssh_private_key) or not exists(profile.ssh_public_key):
        _create_profile(profile)

    return profile

def _create_profile(profile):
    """
    Generate SSH private/public keys so for logging in to
    DataCats.com, display them then prompt the user to copy the
    public key to their account and save the profile.
    """
    # FIXME: let user choose existing ssh key if they prefer
    profile.ssh_private_key = profile.profiledir + '/id_rsa'
    profile.ssh_public_key = profile.profiledir + '/id_rsa.pub'
    profile.save()

    if not exists(profile.ssh_private_key):
        web_command(
            command=["ssh-keygen", "-q", "-t", "rsa", "-N", "", "-C",
                "datacats generated {0}@{1}".format(getuser(), gethostname()),
                "-f", "/output/id_rsa"],
            rw={profile.profiledir: '/output'},
            )




