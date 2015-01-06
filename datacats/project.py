# Copyright 2014-2015 Boxkite Inc.

# This file is part of the DataCats package and is released under
# the terms of the GNU Affero General Public License version 3.0.
# See LICENSE.txt or http://www.fsf.org/licensing/licenses/agpl-3.0.html

from os.path import abspath, split as path_split, expanduser, isdir, exists
from os import makedirs, getcwd, remove
import subprocess
import shutil
import json
from string import uppercase, lowercase, digits
from random import SystemRandom
from sha import sha
from struct import unpack
from ConfigParser import (SafeConfigParser, Error as ConfigParserError,
    NoOptionError)

from datacats.validate import valid_name
from datacats.docker import (web_command, run_container, remove_container,
    inspect_container, is_boot2docker, data_only_container, docker_host,
    PortAllocatedError, container_logs)
from datacats.template import ckan_extension_template
from datacats.scripts import SCRIPTS_DIR, SHELL

class ProjectError(Exception):
    def __init__(self, message, format_args=()):
        self.message = message
        self.format_args = format_args
        super(ProjectError, self).__init__(message, format_args)

    def __str__(self):
        return self.message.format(*self.format_args)


class Project(object):
    """
    DataCats project settings object

    Create with Project.new(path) or Project.load(path)
    """
    def __init__(self, name, target, datadir, ckan_version=None, port=None):
        self.name = name
        self.target = target
        self.datadir = datadir
        self.ckan_version = ckan_version
        self.port = int(port if port else self._choose_port())

    def save(self):
        """
        Save project settings into project directory
        """
        cp = SafeConfigParser()

        cp.add_section('datacats')
        cp.set('datacats', 'name', self.name)
        cp.set('datacats', 'ckan_version', self.ckan_version)
        cp.set('datacats', 'port', str(self.port))

        cp.add_section('passwords')
        for n in sorted(self.passwords):
            cp.set('passwords', n.lower(), self.passwords[n])
        with open(self.target + '/.datacats-project', 'w') as config:
            cp.write(config)

        self._update_saved_project_dir()

    def _update_saved_project_dir(self):
        """
        Store the last place we've seen this project so the user
        can use "datacats -p ..." to specify a project by name
        """
        with open(self.datadir + '/project-dir', 'w') as pdir:
            pdir.write(self.target)

    @classmethod
    def new(cls, path, ckan_version, port=None):
        """
        Return a Project object with settings for a new project.
        No directories or containers are created by this call.

        :params path: location for new project directory, may be relative
        :params ckan_version: release of CKAN to install
        :params port: preferred port for local instance

        Raises ProjectError if directories or project with same
        name already exits.
        """
        workdir, name = path_split(abspath(expanduser(path)))

        if not valid_name(name):
            raise ProjectError('Please choose a project name starting with a '
                'letter and including only lowercase letters and digits')
        if not isdir(workdir):
            raise ProjectError('Parent directory for project does not exist')

        datadir = expanduser('~/.datacats/' + name)
        target = workdir + '/' + name

        if isdir(datadir):
            raise ProjectError('Project data directory {0} already exists',
                (datadir,))
        if isdir(target):
            raise ProjectError('Project directory already exists')

        project = cls(name, target, datadir, ckan_version, port)
        project._generate_passwords()
        return project

    @classmethod
    def load(cls, project_name=None, data_only=False):
        """
        Return a Project object based on an existing project.

        :param project_name: exising project name or None to look in
            current or parent directories for project
        :param data_only: set to True to only load from data dir, not
            the project directory. used for purging project data.

        Raises ProjectError if project can't be found or if there is an
        error parsing the project information.
        """
        if project_name is None:
            wd = abspath(getcwd())
            while not exists(wd + '/.datacats-project'):
                oldwd = wd
                wd, ignore = path_split(wd)
                if wd == oldwd:
                    raise ProjectError(
                        'Project not found in current directory')
        else:
            datadir = expanduser('~/.datacats/' + project_name)
            if not isdir(datadir):
                raise ProjectError('No project found with that name')
            with open(datadir + '/project-dir') as pd:
                wd = pd.read()
            if not data_only and not exists(wd + '/.datacats-project'):
                raise ProjectError(
                    'Project data found but project directory is missing.'
                    ' Try again without "-p" from the new project directory'
                    ' location or remove this project data with'
                    ' "datacats purge"')

        if data_only and project_name:
            return cls(project_name, None, datadir)

        cp = SafeConfigParser()
        try:
            cp.read([wd + '/.datacats-project'])
        except ConfigParserError:
            raise ProjectError('Error reading project information')

        name = cp.get('datacats', 'name')
        datadir = expanduser('~/.datacats/' + name)
        ckan_version = cp.get('datacats', 'ckan_version')
        try:
            port = cp.getint('datacats', 'port')
        except NoOptionError:
            port = None
        passwords = {}
        for n in cp.options('passwords'):
            passwords[n.upper()] = cp.get('passwords', n)

        project = cls(name, wd, datadir, ckan_version, port)
        project.passwords = passwords

        if project_name is None:
            project._update_saved_project_dir()

        return project

    def create_directories(self):
        """
        Call once for new projects to create the initial project directories.
        """
        makedirs(self.datadir, mode=0o700)
        makedirs(self.datadir + '/venv')
        makedirs(self.datadir + '/search')
        if not is_boot2docker():
            makedirs(self.datadir + '/data')
        makedirs(self.datadir + '/files')
        makedirs(self.datadir + '/run')
        makedirs(self.target)

    def create_bash_profile(self):
        """
        Create a default .bash_profile for the shell user that
        activates the ckan virtualenv
        """
        with open(self.target + '/.bash_profile', 'w') as prof:
            prof.write('source /usr/lib/ckan/bin/activate\n')

    def _preload_image(self):
        """
        Return the preloaded ckan src and venv image name
        """
        return 'datacats/web:preload_{0}'.format(self.ckan_version)

    def create_virtualenv(self):
        """
        Populate venv directory from preloaded image
        """
        web_command(
            command='/bin/cp -a /usr/lib/ckan/. /usr/lib/ckan_target/.',
            rw={self.datadir + '/venv': '/usr/lib/ckan_target'},
            image=self._preload_image())

    def create_source(self):
        """
        Populate ckan directory from preloaded image and copy
        who.ini and schema.xml info conf directory
        """
        web_command(
            command='/bin/cp -a /project/ckan /project_target/ckan',
            rw={self.target: '/project_target'},
            image=self._preload_image())
        shutil.copy(
            self.target + '/ckan/ckan/config/who.ini',
            self.target)
        shutil.copy(
            self.target + '/ckan/ckan/config/solr/schema.xml',
            self.target)

    def start_data_and_search(self):
        """
        run the postgres and solr containers
        """
        # complicated because postgres needs hard links to
        # work on its data volume. see issue #5
        if is_boot2docker():
            data_only_container('datacats_dataonly_' + self.name,
                ['/var/lib/postgresql/data'])
            rw = {}
            volumes_from='datacats_dataonly_' + self.name
        else:
            rw = {self.datadir + '/data': '/var/lib/postgresql/data'}
            volumes_from=None

        # users are created when data dir is blank so we must pass
        # all the user passwords as environment vars
        run_container(
            name='datacats_data_' + self.name,
            image='datacats/data',
            environment=self.passwords,
            rw=rw,
            volumes_from=volumes_from)
        run_container(
            name='datacats_search_' + self.name,
            image='datacats/search',
            rw={self.datadir + '/search': '/var/lib/solr'},
            ro={self.target + '/schema.xml': '/etc/solr/conf/schema.xml'})

    def stop_data_and_search(self):
        """
        stop and remove postgres and solr containers
        """
        remove_container('datacats_data_' + self.name)
        remove_container('datacats_search_' + self.name)

    def fix_storage_permissions(self):
        """
        Set the owner of all apache storage files to www-data container user
        """
        web_command(
            command='/bin/chown -R www-data: /var/www/storage',
            rw={self.datadir + '/files': '/var/www/storage'})

    def create_ckan_ini(self):
        """
        Use make-config to generate an initial development.ini file
        """
        web_command(
            command='/usr/lib/ckan/bin/paster make-config'
                ' ckan /project/development.ini',
            ro={self.datadir + '/venv': '/usr/lib/ckan'},
            rw={self.target: '/project'})

    def update_ckan_ini(self, skin=True):
        """
        Use config-tool to update development.ini with our project settings

        :param skin: use project template skin plugin True/False
        """
        p = self.passwords
        command = [
            '/usr/lib/ckan/bin/paster', '--plugin=ckan', 'config-tool',
            '/project/development.ini', '-e',
            'sqlalchemy.url = postgresql://ckan:'
                '{CKAN_PASSWORD}@db:5432/ckan'.format(**p),
            'ckan.datastore.read_url = postgresql://ckan_datastore_readonly:'
                '{DATASTORE_RO_PASSWORD}@db:5432/ckan_datastore'.format(**p),
            'ckan.datastore.write_url = postgresql://ckan_datastore_readwrite:'
                '{DATASTORE_RW_PASSWORD}@db:5432/ckan_datastore'.format(**p),
            'solr_url = http://solr:8080/solr',
            'ckan.storage_path = /var/www/storage',
            'ckan.plugins = ' + (self.name + '_skin' if skin else ''),
            'ckan.site_title = ' + self.name,
            'ckan.site_logo = ',
            ]
        web_command(
            command=command,
            ro={self.datadir + '/venv': '/usr/lib/ckan'},
            rw={self.target: '/project'})

    def create_install_template_skin(self):
        """
        Create an example ckan extension for this project and install it
        """
        ckan_extension_template(self.name, self.target)
        self.install_package_develop('ckanext-' + self.name)


    def fix_project_permissions(self):
        """
        Reset owner of project files to the host user so they can edit,
        move and delete them freely.
        """
        web_command(
            command='/bin/chown -R --reference=/project'
                ' /usr/lib/ckan /project',
            rw={self.datadir + '/venv': '/usr/lib/ckan',
                self.target: '/project'})

    def ckan_db_init(self):
        """
        Run db init to create all ckan tables
        """
        web_command(
            command='/usr/lib/ckan/bin/paster --plugin=ckan db init'
                ' -c /project/development.ini',
            ro={self.datadir + '/venv': '/usr/lib/ckan',
                self.target: '/project'},
            links={'datacats_search_' + self.name: 'solr',
                'datacats_data_' + self.name: 'db'})

    def _generate_passwords(self):
        """
        Generate new DB passwords and store them in self.passwords
        """
        self.passwords = {
            'POSTGRES_PASSWORD': generate_db_password(),
            'CKAN_PASSWORD': generate_db_password(),
            'DATASTORE_RO_PASSWORD': generate_db_password(),
            'DATASTORE_RW_PASSWORD': generate_db_password(),
            }

    def start_web(self, production=False):
        """
        Start the apache server or paster serve

        :param production: True for apache, False for paster serve + debug on
        """
        port = self.port
        command = None
        if not production:
            command = [
                '/bin/su', 'www-data', '-s', '/bin/sh', '-c',
                '/usr/lib/ckan/bin/paster --plugin=ckan'
                ' serve /project/development.ini --reload']

        def bindings():
            return {5000: port if is_boot2docker() else ('127.0.0.1', port)}
        while True:
            self._create_run_ini(port, production)
            try:
                run_container(
                    name='datacats_web_' + self.name,
                    image='datacats/web',
                    rw={self.datadir + '/files': '/var/www/storage'},
                    ro={self.datadir + '/venv': '/usr/lib/ckan',
                        self.target: '/project/',
                        self.datadir + '/run/development.ini':
                            '/project/development.ini'},
                    links={'datacats_search_' + self.name: 'solr',
                        'datacats_data_' + self.name: 'db'},
                    command=command,
                    port_bindings=bindings(),
                    )
            except PortAllocatedError:
                port = self._next_port(port)
                continue
            break

    def _create_run_ini(self, port, production):
        """
        Create run/development.ini in datadir with debug and site_url overridden
        """
        cp = SafeConfigParser()
        try:
            cp.read([self.target + '/development.ini'])
        except ConfigParserError:
            raise ProjectError('Error reading development.ini')

        cp.set('DEFAULT', 'debug', 'false' if production else 'true')
        site_url = 'http://{0}:{1}/'.format(docker_host(), port)
        cp.set('app:main', 'ckan.site_url', site_url)

        if not isdir(self.datadir + '/run'):
            makedirs(self.datadir + '/run')  # upgrade old datadir
        with open(self.datadir + '/run/development.ini', 'w') as runini:
            cp.write(runini)

    def _choose_port(self):
        """
        Return a port number from 5000-5999 based on the project name
        to be used as a default when the user hasn't selected one.
        """
        # instead of random let's base it on the name chosen
        return 5000 + unpack('Q',
            sha(self.name.decode('ascii')).digest()[:8])[0] % 1000

    def _next_port(self, port):
        """
        Return another port from the 5000-5999 range
        """
        port = 5000 + (port + 1) % 1000
        if port == self.port:
            raise ProjectError('Too many instances running')
        return port

    def stop_web(self):
        """
        Stop and remove the web container
        """
        remove_container('datacats_web_' + self.name, force=True)

    def _current_web_port(self):
        """
        return just the port number for the web container, or None if
        not running
        """
        info = inspect_container('datacats_web_' + self.name)
        if info is None:
            return None
        return info['NetworkSettings']['Ports']['5000/tcp'][0]['HostPort']

    def containers_running(self):
        """
        Return a list including 0 or more of ['web', 'data', 'search']
        for containers tracked by this project that are running
        """
        running = []
        for n in ['web', 'data', 'search']:
            if inspect_container('datacats_' + n + '_' + self.name):
                running.append(n)
        return running

    def web_address(self):
        """
        Return the url of the web server or None if not running
        """
        port = self._current_web_port()
        if port is None:
            return None
        return 'http://{0}:{1}/'.format(docker_host(), port)

    def create_admin_set_password(self, password):
        """
        create 'admin' account with given password
        """
        with open(self.datadir + '/run/admin.json', 'w') as out:
            json.dump({
                'name': 'admin',
                'email': 'none',
                'password': password,
                'sysadmin': True},
                out)
        web_command(
            command=['/bin/bash', '-c',
                '/usr/lib/ckan/bin/ckanapi -c /project/development.ini '
                'action user_create -i < /input/admin.json'],
            ro={self.datadir + '/venv': '/usr/lib/ckan',
                self.target: '/project',
                self.datadir + '/run/admin.json': '/input/admin.json'},
            links={'datacats_search_' + self.name: 'solr',
                'datacats_data_' + self.name: 'db'})
        remove(self.datadir + '/run/admin.json')

    def interactive_shell(self):
        """
        launch interactive shell (bash) session with all writable volumes
        """
        # FIXME: consider switching this to dockerpty
        # using subprocess for docker client's interactive session
        subprocess.call([
            '/usr/bin/docker', 'run', '--rm', '-it',
            '-v', self.datadir + '/venv:/usr/lib/ckan:rw',
            '-v', self.target + ':/project:rw',
            '-v', self.datadir + '/files:/var/www/storage:rw',
            '-v', SHELL + ':/scripts/shell.sh:ro',
            '--link', 'datacats_search_' + self.name + ':solr',
            '--link', 'datacats_data_' + self.name + ':db',
            '--hostname', self.name,
            'datacats/web', '/scripts/shell.sh'])

    def install_package_requirements(self, psrc):
        """
        Install from requirements.txt file found in src_package

        :param src_package: name of directory under project src directory
        """
        package = self.target + '/' + psrc
        assert isdir(package), package
        if not exists(package + '/requirements.txt'):
            return
        web_command(
            command=[
                '/usr/lib/ckan/bin/pip', 'install', '-r',
                '/project/' + psrc + '/requirements.txt'
                ],
            rw={self.datadir + '/venv': '/usr/lib/ckan'},
            ro={self.target: '/project'},
            )

    def install_package_develop(self, psrc):
        """
        Install a src package in place (setup.py develop)

        :param psrc: name of directory under project directory
        """
        package = self.target + '/' + psrc
        assert isdir(package), package
        if not exists(package + '/setup.py'):
            return
        web_command(
            command=[
                '/usr/lib/ckan/bin/pip', 'install', '-e', '/project/' + psrc
                ],
            rw={self.datadir + '/venv': '/usr/lib/ckan',
                self.target + '/' + psrc: '/project/' + psrc},
            ro={self.target: '/project'},
            )
        # .egg-info permissions
        web_command(
            command=['/bin/chown', '-R', '--reference=/project',
                '/project/' + psrc],
            rw={self.target + '/' + psrc: '/project/' + psrc},
            ro={self.target: '/project'},
            )

    def purge_data(self):
        """
        Remove uploaded files, postgres db, solr index, venv
        """
        datadirs = ['files', 'search', 'venv']
        if is_boot2docker():
            remove_container('datacats_dataonly_' + self.name)
        else:
            datadirs.append('data')

        web_command(
            command=['/bin/rm', '-r']
                + ['/project/data/' + d for d in datadirs],
            rw={self.datadir: '/project/data'},
            )
        shutil.rmtree(self.datadir)

    def logs(self, container, tail='all', follow=False, timestamps=False):
        """
        :param container: 'web', 'search' or 'data'
        :param tail: number of lines to show
        :param follow: True to return generator instead of list
        :param timestamps: True to include timestamps
        """
        return container_logs(
            'datacats_' + container + '_' + self.name,
            tail,
            follow,
            timestamps)


def generate_db_password():
    """
    Return a 16-character alphanumeric random string generated by the
    operating system's secure pseudo random number generator
    """
    chars = uppercase + lowercase + digits
    return ''.join(SystemRandom().choice(chars) for x in xrange(16))

