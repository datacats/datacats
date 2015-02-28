# Copyright 2014-2015 Boxkite Inc.

# This file is part of the DataCats package and is released under
# the terms of the GNU Affero General Public License version 3.0.
# See LICENSE.txt or http://www.fsf.org/licensing/licenses/agpl-3.0.html

from os.path import expanduser, exists, isdir
from os import makedirs
from ConfigParser import SafeConfigParser
from socket import gethostname
from getpass import getuser

from datacats.docker import web_command, WebCommandError
from datacats.scripts import KNOWN_HOSTS, SSH_CONFIG

DATACATS_USER_HOST = 'datacats@command.datacats.com'

class UserProfile(object):
    """
    DataCats user profile settings object
    """
    def __init__(self):
        self.profiledir = expanduser('~/.datacats/user-profile')
        config = self.profiledir + '/config'
        if isdir(self.profiledir) and exists(config):
            cp = SafeConfigParser()
            cp.read([config])
            self.ssh_private_key = cp.get('ssh', 'private_key')
            self.ssh_public_key = cp.get('ssh', 'public_key')
        else:
            self.ssh_private_key = None
            self.ssh_public_key = None

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
                "datacats generated {0}@{1}".format(getuser(), gethostname()),
                "-f", "/output/id_rsa"],
            rw={self.profiledir: '/output'},
            )

    def test_ssh_key(self, project):
        """
        Return True if this key is accepted by DataCats.com
        """
        try:
            web_command(
                command=["ssh",
                    _project_user_host(project),
                    'test'],
                ro={
                    KNOWN_HOSTS: '/root/.ssh/known_hosts',
                    SSH_CONFIG: '/etc/ssh/ssh_config',
                    self.profiledir + '/id_rsa': '/root/.ssh/id_rsa'},
                clean_up=True
                )
            return True
        except WebCommandError:
            return False

    def create(self, project, target_name, stream_output=None):
        """
        Return True if project was created and now belongs to this user
        """
        try:
            web_command(
                command=[
                    "ssh", _project_user_host(project), "create", target_name,
                    ],
                ro={KNOWN_HOSTS: '/root/.ssh/known_hosts',
                    SSH_CONFIG: '/etc/ssh/ssh_config',
                    self.profiledir + '/id_rsa': '/root/.ssh/id_rsa'},
                stream_output=stream_output,
                clean_up=True,
                )
            return True
        except WebCommandError:
            return False

    def admin_password(self, project, target_name, password):
        """
        Return True if password was set successfully
        """
        try:
            web_command(
                command=[
                    "ssh", _project_user_host(project),
                    "admin_password", target_name, password,
                    ],
                ro={KNOWN_HOSTS: '/root/.ssh/known_hosts',
                    SSH_CONFIG: '/etc/ssh/ssh_config',
                    self.profiledir + '/id_rsa': '/root/.ssh/id_rsa'},
                clean_up=True,
                )
            return True
        except WebCommandError:
            return False


    def deploy(self, project, target_name, stream_output=None):
        """
        Return True if deployment was successful
        """
        try:
            web_command(
                command=[
                    "rsync", "-lrv", "--safe-links", "--munge-links",
                    "--delete", "--inplace", "--chmod=ugo=rwX",
                    "--exclude=.datacats-environment",
                    "--exclude=.git",
                    "/project/.",
                    _project_user_host(project) + ':' + target_name],
                ro={project.target: '/project',
                    KNOWN_HOSTS: '/root/.ssh/known_hosts',
                    SSH_CONFIG: '/etc/ssh/ssh_config',
                    self.profiledir + '/id_rsa': '/root/.ssh/id_rsa'},
                stream_output=stream_output,
                clean_up=True,
                )
            web_command(
                command=[
                    "ssh", _project_user_host(project), "install", target_name,
                    ],
                ro={KNOWN_HOSTS: '/root/.ssh/known_hosts',
                    SSH_CONFIG: '/etc/ssh/ssh_config',
                    self.profiledir + '/id_rsa': '/root/.ssh/id_rsa'},
                stream_output=stream_output,
                clean_up=True,
                )
            return True
        except WebCommandError:
            return False

def _project_user_host(project):
    if project.deploy_target is None:
        return DATACATS_USER_HOST
    return project.deploy_target

