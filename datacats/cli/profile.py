# Copyright 2014-2015 Boxkite Inc.

# This file is part of the DataCats package and is released under
# the terms of the GNU Affero General Public License version 3.0.
# See LICENSE.txt or http://www.fsf.org/licensing/licenses/agpl-3.0.html

from os.path import exists

from datacats.userprofile import UserProfile

def get_working_profile(environment):
    """
    Return a complete UserProfile with ssh keys configured either
    by loading an existing profile or setting one up with the
    user interactively.
    """
    profile = UserProfile()

    new_key = False
    if profile.ssh_private_key is None or not exists(
            profile.ssh_private_key) or not exists(profile.ssh_public_key):
        new_key = _create_profile(profile)

    if new_key:
        print 'New key generated. Please visit'
        print 'https://www.datacats.com/account/key'
        print 'and paste your public key in to the form:'

    if not new_key and not profile.test_ssh_key(environment):
        print 'There was an error connecting to DataCats.com'
        print 'If you have not installed your key please visit'
        print 'https://www.datacats.com/account/key'
        print 'and paste your public key in to the form:'
        new_key = True

    if new_key:
        print
        with open(profile.ssh_public_key) as pub_key:
            print pub_key.read()
        return

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

    if exists(profile.ssh_private_key):
        return False
    profile.generate_ssh_key()
    return True

