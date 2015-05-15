# Copyright 2014-2015 Boxkite Inc.

# This file is part of the DataCats package and is released under
# the terms of the GNU Affero General Public License version 3.0.
# See LICENSE.txt or http://www.fsf.org/licensing/licenses/agpl-3.0.html

from os.path import exists

from datacats.userprofile import UserProfile
from datacats.environment import DatacatsError


def get_working_profile(environment):
    """
    Return a complete UserProfile with ssh keys configured either
    by loading an existing profile or setting one up with the
    user interactively.
    """
    profile = UserProfile()
    if not (profile.ssh_private_key is None) and \
        exists(profile.ssh_private_key) and \
        exists(profile.ssh_public_key):
        profile.test_ssh_key(environment)
        # we sucessfully loaded the ssh key and tested it by connecting to the server,
        #so all is good at this point and
        # we have got ourselves a working profile
        return profile

    new_key = _create_profile(profile)


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
    profile.generate_ssh_key()
    user_error_message = ("Your profile does not seem to have an ssh key (which is an equivalent of your password so that datacats.io could recognize you)."
        "So we generated a new ssh key for you. Please go to www.datacats.com/account/key and add the following public key:"
        " \n \n {public_key} \n \n to your profile.").format(public_key=profile.read_public_key())
    raise DatacatsError(user_error_message)

