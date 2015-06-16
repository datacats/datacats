# Copyright 2014-2015 Boxkite Inc.

# This file is part of the DataCats package and is released under
# the terms of the GNU Affero General Public License version 3.0.
# See LICENSE.txt or http://www.fsf.org/licensing/licenses/agpl-3.0.html

from os.path import expanduser, exists, isdir
from os import makedirs
from ConfigParser import SafeConfigParser
from socket import gethostname
from getpass import getuser

from datacats.docker import remote_server_command, web_command
from datacats.error import DatacatsError, WebCommandError


class UserProfile(object):

    """
    DataCats user profile settings object
    (at the moment only tracks ssh private key used to call remote commands)
    """

    def __init__(self):
        self.profiledir = expanduser('~/.datacats/user-profile')
        config = self.profiledir + '/config'
        if not isdir(self.profiledir) or not exists(config):
            self.create_profile()

        cp = SafeConfigParser()
        cp.read([config])
        self.ssh_private_key = cp.get('ssh', 'private_key')
        self.ssh_public_key = cp.get('ssh', 'public_key')

    def create_profile(self):
        self.ssh_private_key = self.profiledir + '/id_rsa'
        self.ssh_public_key = self.profiledir + '/id_rsa.pub'
        self.save()
        self.generate_ssh_key()
        user_error_message = ("Your profile does not seem to have an ssh key\n"
            " (which is an equivalent of your password so that datacats.io"
            " could recognize you).\n"
            "It is probably because this is your first time running"
            " a remote command in which case welcome!\n"
            "So we generated a new ssh key for you. \n "
            "Please go to www.datacats.com/account/key"
            " and add the following public key:"
            " \n \n {public_key} \n \n"
            " to your profile so that the server can recognize you as you."
                              ).format(public_key=self.read_public_key())
        raise DatacatsError(user_error_message)

    def read_public_key(self):
        """
        Read public key from file and reuturn as a string
        """
        with open(self.ssh_public_key) as pub_key:
            return pub_key.read()

    def save(self):
        """
        Save profile settings into user profile directory
        """
        config = self.profiledir + '/config'
        if not isdir(self.profiledir):
            makedirs(self.profiledir)

        cp = SafeConfigParser()

        cp.add_section('ssh')
        cp.set('ssh', 'private_key', self.ssh_private_key)
        cp.set('ssh', 'public_key', self.ssh_public_key)

        with open(config, 'w') as cfile:
            cp.write(cfile)

    def generate_ssh_key(self):
        """
        Generate a new ssh private and public key
        """
        web_command(
            command=["ssh-keygen", "-q", "-t", "rsa", "-N", "", "-C",
                     "datacats generated {0}@{1}".format(
                         getuser(), gethostname()),
                     "-f", "/output/id_rsa"],
            rw={self.profiledir: '/output'},
            )

    def test_ssh_key(self, environment):
        """
        Return True if this key is accepted by DataCats.com
        """
        try:
            remote_server_command(
                ["ssh", environment.deploy_target, 'test'],
                environment, self, clean_up=True)

        except WebCommandError as e:

            user_unrecognized_error_message = (
                "Your ssh key "
                "(which is an equivalent of your password so"
                " that datacats.io could recognize you) "
                "does not seem to be recognized by the datacats.io server. \n \n"
                "Most likely it is because you need to go to"
                " www.datacats.com/account/key"
                " and add the following public key: \n \n {public_key} \n \n"
                "to your profile so that datacat's server could recognize you."
                " So maybe try that?\n"
                "If the problem persists, please contact the developer team."
                ).format(public_key=self.read_public_key())

            network_unreachable_error_message = (
                "Unable to connect to the hosting server: {0} \n"
                "Some of the reasons for that may be: \n"
                "  1) the internet connection is down,\n"
                "  2) the server is not up or functioning properly,\n"
                "  3) there is a firewall block for the datacats application\n"
                " or something of this sort."
                ).format(environment.deploy_target)

            user_error_message = network_unreachable_error_message \
                if "Network is unreachable" in e.logs \
                else user_unrecognized_error_message
            raise DatacatsError(user_error_message, parent_exception=e)

    def create(self, environment, target_name):
        """
        Sends "create project" command to the remote server
        """
        remote_server_command(
            ["ssh", environment.deploy_target, "create", target_name],
            environment, self,
            clean_up=True,
            )

    def admin_password(self, environment, target_name, password):
        """
        Return True if password was set successfully
        """
        try:
            remote_server_command(
                ["ssh", environment.deploy_target,
                    "admin_password", target_name, password],
                environment, self,
                clean_up=True
                )
            return True
        except WebCommandError:
            return False

    def deploy(self, environment, target_name, stream_output=None):
        """
        Return True if deployment was successful
        """
        try:
            remote_server_command(
                [
                    "rsync", "-lrv", "--safe-links", "--munge-links",
                    "--delete", "--inplace", "--chmod=ugo=rwX",
                    "--exclude=.datacats-environment",
                    "--exclude=.git",
                    "/project/.",
                    environment.deploy_target + ':' + target_name
                ],
                environment, self,
                include_project_dir=True,
                stream_output=stream_output,
                clean_up=True,
                )
        except WebCommandError as e:
            raise DatacatsError(
                "Unable to deploy `{0}` to remote server for some reason:\n"
                " datacats was not able to copy data to the remote server",
                format_args=(target_name,), parent_exception=e
                )

        try:
            remote_server_command(
                [
                    "ssh", environment.deploy_target, "install", target_name,
                    ],
                environment, self,
                clean_up=True,
                )
            return True
        except WebCommandError as e:
            raise DatacatsError(
                "Unable to deploy `{0}` to remote server for some reason:\n"
                "datacats copied data to the server but failed to register\n"
                "(or `install`) the new catalog",
                format_args=(target_name,),
                parent_exception=e
                )
