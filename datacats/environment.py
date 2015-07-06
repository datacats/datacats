# Copyright 2014-2015 Boxkite Inc.

# This file is part of the DataCats package and is released under
# the terms of the GNU Affero General Public License version 3.0.
# See LICENSE.txt or http://www.fsf.org/licensing/licenses/agpl-3.0.html

from os.path import isdir, exists, join
from os import makedirs, remove, environ
import sys
import subprocess
import shutil
import json
import time
import socket
from sha import sha
from struct import unpack
from ConfigParser import (SafeConfigParser, Error as ConfigParserError)

from datacats import task
from datacats.docker import (web_command, run_container, remove_container,
                             inspect_container, is_boot2docker,
                             docker_host, container_logs, APIError)
from datacats.template import ckan_extension_template
from datacats.scripts import (WEB, SHELL, PASTER, PASTER_CD, PURGE,
    RUN_AS_USER, INSTALL_REQS, CLEAN_VIRTUALENV, INSTALL_PACKAGE,
    COMPILE_LESS, DATAPUSHER, INSTALL_POSTGIS, ADJUST_DEVINI,
    UPDATE_ADD_ADMIN, INSTALL_EXTRA_PACKAGES)
from datacats.network import wait_for_service_available, ServiceTimeout
from datacats.password import generate_password
from datacats.error import DatacatsError, WebCommandError, PortAllocatedError

WEB_START_TIMEOUT_SECONDS = 30
DB_INIT_RETRY_SECONDS = 30
DB_INIT_RETRY_DELAY = 2
DOCKER_EXE = 'docker'


class Environment(object):
    """
    DataCats environment settings object

    Create with Environment.new(path) or Environment.load(path)
    """
    def __init__(self, name, target, datadir, site_name, ckan_version=None,
                 port=None, deploy_target=None, site_url=None, always_prod=False,
                 extension_dir='ckan', address=None, remote_server_key=None):
        self.name = name
        self.target = target
        self.datadir = datadir
        self.extension_dir = extension_dir
        self.ckan_version = ckan_version
        # This is the site that all commands will operate on.
        self.site_name = site_name
        self.port = int(port if port else self._choose_port())
        self.address = address
        self.deploy_target = deploy_target
        self.remote_server_key = remote_server_key
        self.site_url = site_url
        self.always_prod = always_prod
        self.sites = None

    def _set_site_name(self, site_name):
        self._site_name = site_name
        self.sitedir = join(self.datadir, 'sites', site_name)

    def _get_site_name(self):
        return self._site_name

    site_name = property(fget=_get_site_name, fset=_set_site_name)

    def _load_sites(self):
        """
        Gets the names of all of the sites from the datadir and stores them
        in self.sites. Also returns this list.
        """
        if not self.sites:
            self.sites = task.list_sites(self.datadir)
        return self.sites

    def save_site(self):
        """
        Save environment settings in the directory that need to be saved
        even when creating only a new sub-site env.
        """
        self._load_sites()
        self.sites.append(self.site_name)

        task.save_new_site(self.site_name, self.sitedir, self.target, self.port,
            self.address, self.site_url, self.passwords)

    def save(self):
        """
        Save environment settings into environment directory, overwriting
        any existing configuration and discarding site config
        """
        task.save_new_environment(self.name, self.datadir, self.target,
            self.ckan_version, self.deploy_target, self.always_prod)

    @classmethod
    def new(cls, path, ckan_version, site_name, **kwargs):
        """
        Return a Environment object with settings for a new project.
        No directories or containers are created by this call.

        :params path: location for new project directory, may be relative
        :params ckan_version: release of CKAN to install
        :params site_name: The name of the site to install database and solr \
                            eventually.

        For additional keyword arguments see the __init__ method.

        Raises DatcatsError if directories or project with same
        name already exits.
        """
        name, datadir, srcdir = task.new_environment_check(path, site_name)
        environment = cls(name, srcdir, datadir, site_name, ckan_version, **kwargs)
        environment._generate_passwords()
        return environment

    @classmethod
    def load(cls, environment_name=None, site_name='primary', data_only=False):
        """
        Return an Environment object based on an existing environnment+site.

        :param environment_name: exising environment name, path or None to
            look in current or parent directories for project
        :param data_only: set to True to only load from data dir, not
            the project dir; Used for purging environment data.

        Raises DatacatsError if environment can't be found or if there is an
        error parsing the environment information.
        """
        srcdir, extension_dir, datadir = task.find_environment_dirs(
            environment_name, data_only)

        if datadir and data_only:
            return cls(environment_name, None, datadir, site_name)

        (datadir, name, ckan_version, always_prod, deploy_target,
            remote_server_key) = task.load_environment(srcdir, datadir)

        (port, address, site_url, passwords
            ) = task.load_site(srcdir, datadir, site_name)

        environment = cls(name, srcdir, datadir, site_name, ckan_version=ckan_version,
                          port=port, deploy_target=deploy_target, site_url=site_url,
                          always_prod=always_prod, address=address,
                          extension_dir=extension_dir,
                          remote_server_key=remote_server_key)

        if passwords:
            environment.passwords = passwords
        else:
            environment._generate_passwords()

        environment._load_sites()
        return environment

    def data_exists(self):
        """
        Return True if the datadir for this environment exists
        """
        return isdir(self.datadir)

    def require_valid_site(self):
        if self.site_name not in self.sites:
            raise DatacatsError('Invalid site name: {}. Valid names are: {}'
                                .format(self.site_name,
                                        ', '.join(self.sites)))

    def data_complete(self):
        """
        Return True if all the expected datadir files are present
        """
        return task.data_complete(self.datadir, self.sitedir,
            self._get_container_name)

    def require_data(self):
        """
        raise a DatacatsError if the datadir or volumes are missing or damaged
        """
        files = task.source_missing(self.target)
        if files:
            raise DatacatsError('Missing files in source directory:\n' +
                                '\n'.join(files))
        if not self.data_exists():
            raise DatacatsError('Environment datadir missing. '
                                'Try "datacats init".')
        if not self.data_complete():
            raise DatacatsError('Environment datadir damaged or volumes '
                                'missing. '
                                'To reset and discard all data use '
                                '"datacats reset"')

    def create_directories(self, create_project_dir=True):
        """
        Call once for new projects to create the initial project directories.
        """
        return task.create_directories(self.datadir, self.sitedir,
            self.target if create_project_dir else None)

    def create_bash_profile(self):
        """
        Create a default .bash_profile for the shell user that
        activates the ckan virtualenv
        """
        with open(self.target + '/.bash_profile', 'w') as prof:
            prof.write('source /usr/lib/ckan/bin/activate\n')

    def _preload_image(self):
        # pylint: disable=no-self-use
        """
        Return the preloaded ckan src and venv image name
        """
        # FIXME: when we support more than one preload image
        # get the preload name from self.ckan_version
        return 'datacats/web:preload-2.3'

    def create_virtualenv(self):
        """
        Populate venv from preloaded image
        """
        return task.create_virtualenv(self.target, self.datadir,
            self._preload_image(), self._get_container_name)

    def clean_virtualenv(self):
        """
        Empty our virtualenv so that new (or older) dependencies may be
        installed
        """
        self.user_run_script(
            script=CLEAN_VIRTUALENV,
            args=[],
            rw_venv=True,
            )

    def install_extra(self):
        self.user_run_script(
            script=INSTALL_EXTRA_PACKAGES,
            args=[],
            rw_venv=True
        )

    def create_source(self, datapusher=True):
        """
        Populate ckan directory from preloaded image and copy
        who.ini and schema.xml info conf directory
        """
        task.create_source(self.target, self._preload_image(), datapusher)

    def start_supporting_containers(self):
        """
        Start all supporting containers (containers required for CKAN to
        operate) if they aren't already running.
        """
        task.start_supporting_containers(self.sitedir, self.target,
            self.passwords, self._get_container_name)

    def stop_supporting_containers(self):
        """
        Stop and remove supporting containers (containers that are used by CKAN but don't host
        CKAN or CKAN plugins). This method should *only* be called after CKAN has been stopped
        or behaviour is undefined.
        """
        task.stop_supporting_containers(self._get_container_name)

    def fix_storage_permissions(self):
        """
        Set the owner of all apache storage files to www-data container user
        """
        web_command(
            command='/bin/chown -R www-data: /var/www/storage',
            rw={self.sitedir + '/files': '/var/www/storage'})

    def create_ckan_ini(self):
        """
        Use make-config to generate an initial development.ini file
        """
        self.run_command(
            command='/usr/lib/ckan/bin/paster make-config'
            ' ckan /project/development.ini',
            rw_project=True,
            )

    def update_ckan_ini(self, skin=True):
        """
        Use config-tool to update development.ini with our environment settings

        :param skin: use environment template skin plugin True/False
        """
        command = [
            '/usr/lib/ckan/bin/paster', '--plugin=ckan', 'config-tool',
            '/project/development.ini', '-e',
            'sqlalchemy.url = postgresql://<hidden>',
            'ckan.datastore.read_url = postgresql://<hidden>',
            'ckan.datastore.write_url = postgresql://<hidden>',
            'ckan.datapusher.url = http://datapusher:8800',
            'solr_url = http://solr:8080/solr',
            'ckan.storage_path = /var/www/storage',
            'ckan.plugins = datastore resource_proxy text_view ' +
            ('datapusher ' if exists(self.target + '/datapusher') else '')
            + 'recline_grid_view recline_graph_view'
            + (' {0}_theme'.format(self.name) if skin else ''),
            'ckan.site_title = ' + self.name,
            'ckan.site_logo =',
            'ckan.auth.create_user_via_web = false',
            ]
        self.run_command(command=command, rw_project=True)

    def create_install_template_skin(self):
        """
        Create an example ckan extension for this environment and install it
        """
        ckan_extension_template(self.name, self.target)
        self.install_package_develop('ckanext-' + self.name + 'theme')

    def ckan_db_init(self, retry_seconds=DB_INIT_RETRY_SECONDS):
        """
        Run db init to create all ckan tables

        :param retry_seconds: how long to retry waiting for db to start
        """
        # XXX workaround for not knowing how long we need to wait
        # for postgres to be ready. fix this by changing the postgres
        # entrypoint, or possibly running once with command=/bin/true
        started = time.time()
        while True:
            try:
                self.run_command(
                    '/usr/lib/ckan/bin/paster --plugin=ckan db init '
                    '-c /project/development.ini',
                    db_links=True,
                    clean_up=True,
                    )
                break
            except WebCommandError:
                if started + retry_seconds > time.time():
                    raise
            time.sleep(DB_INIT_RETRY_DELAY)

    def install_postgis_sql(self):
        web_command(
            '/scripts/install_postgis.sh',
            image='datacats/postgres',
            ro={INSTALL_POSTGIS: '/scripts/install_postgis.sh'},
            links={self._get_container_name('postgres'): 'db'},
            )

    def _generate_passwords(self):
        """
        Generate new DB passwords and store them in self.passwords
        """
        self.passwords = {
            'POSTGRES_PASSWORD': generate_password(),
            'CKAN_PASSWORD': generate_password(),
            'DATASTORE_RO_PASSWORD': generate_password(),
            'DATASTORE_RW_PASSWORD': generate_password(),
            'BEAKER_SESSION_SECRET': generate_password(),
            }

    def needs_datapusher(self):
        cp = SafeConfigParser()
        try:
            cp.read(self.target + '/development.ini')
            return 'datapusher' in cp.get('app:main', 'ckan.plugins')
        except ConfigParserError as e:
            raise DatacatsError('Failed to read and parse development.ini: ' + str(e))

    def start_ckan(self, production=False, address='127.0.0.1', log_syslog=False,
                   paster_reload=True):
        """
        Start the apache server or paster serve

        :param production: True for apache, False for paster serve + debug on
        :param address: On Linux, the address to serve from (can be 0.0.0.0 for
                        listening on all addresses)
        :param paster_reload: Instruct paster to watch for file changes
        """
        self.stop_ckan()

        port = self.port

        production = production or self.always_prod
        override_site_url = self.address == '127.0.0.1' and not is_boot2docker()
        command = ['/scripts/web.sh', str(production), str(override_site_url), str(paster_reload)]

        if address != '127.0.0.1' and is_boot2docker():
            raise DatacatsError('Cannot specify address on boot2docker.')

        datapusher = self.needs_datapusher()

        # XXX nasty hack, remove this once we have a lessc command
        # for users (not just for building our preload image)
        if not production:
            css = self.target + '/ckan/ckan/public/base/css'
            if not exists(css + '/main.debug.css'):
                from shutil import copyfile
                copyfile(css + '/main.css', css + '/main.debug.css')

        ro = {
            self.target: '/project',
            DATAPUSHER: '/scripts/datapusher.sh'
        }

        if not is_boot2docker():
            ro[self.datadir + '/venv'] = '/usr/lib/ckan'

        if datapusher:
            run_container(
                self._get_container_name('datapusher'),
                'datacats/web',
                '/scripts/datapusher.sh',
                ro=ro,
                volumes_from=(self._get_container_name('venv') if is_boot2docker() else None))

        while True:
            self._create_run_ini(port, production)
            try:
                self._run_web_container(port, command, address, log_syslog=log_syslog,
                                        datapusher=datapusher)
                if not is_boot2docker():
                    self.address = address
            except PortAllocatedError:
                port = self._next_port(port)
                continue
            break

    def _create_run_ini(self, port, production, output='development.ini',
                        source='development.ini', override_site_url=True):
        """
        Create run/development.ini in datadir with debug and site_url overridden
        and with correct db passwords inserted
        """
        cp = SafeConfigParser()
        try:
            cp.read([self.target + '/' + source])
        except ConfigParserError:
            raise DatacatsError('Error reading development.ini')

        cp.set('DEFAULT', 'debug', 'false' if production else 'true')

        if self.site_url:
            site_url = self.site_url
        else:
            if is_boot2docker():
                web_address = socket.gethostbyname(docker_host())
            else:
                web_address = self.address
            site_url = 'http://{}:{}'.format(web_address, port)

        if override_site_url:
            cp.set('app:main', 'ckan.site_url', site_url)

        cp.set('app:main', 'sqlalchemy.url',
               'postgresql://ckan:{0}@db:5432/ckan'
               .format(self.passwords['CKAN_PASSWORD']))
        cp.set('app:main', 'ckan.datastore.read_url',
               'postgresql://ckan_datastore_readonly:{0}@db:5432/ckan_datastore'
               .format(self.passwords['DATASTORE_RO_PASSWORD']))
        cp.set('app:main', 'ckan.datastore.write_url',
               'postgresql://ckan_datastore_readwrite:{0}@db:5432/ckan_datastore'
               .format(self.passwords['DATASTORE_RW_PASSWORD']))
        cp.set('app:main', 'solr_url', 'http://solr:8080/solr')
        cp.set('app:main', 'beaker.session.secret', self.passwords['BEAKER_SESSION_SECRET'])

        if not isdir(self.sitedir + '/run'):
            makedirs(self.sitedir + '/run')  # upgrade old datadir
        with open(self.sitedir + '/run/' + output, 'w') as runini:
            cp.write(runini)

    def _run_web_container(self, port, command, address='127.0.0.1', log_syslog=False,
                           datapusher=True):
        """
        Start web container on port with command
        """
        if is_boot2docker():
            ro = {}
            volumes_from = self._get_container_name('venv')
        else:
            ro = {self.datadir + '/venv': '/usr/lib/ckan'}
            volumes_from = None

        links = {
            self._get_container_name('solr'): 'solr',
            self._get_container_name('postgres'): 'db'
        }

        if datapusher:
            if 'datapusher' not in self.containers_running():
                raise DatacatsError(container_logs(self._get_container_name('datapusher'), "all",
                                                   False, False))
            links[self._get_container_name('datapusher')] = 'datapusher'

        try:
            run_container(
                name=self._get_container_name('web'),
                image='datacats/web',
                rw={self.sitedir + '/files': '/var/www/storage',
                    self.sitedir + '/run/development.ini':
                        '/project/development.ini'},
                ro=dict({
                    self.target: '/project/',
                    WEB: '/scripts/web.sh',
                    ADJUST_DEVINI: '/scripts/adjust_devini.py'}, **ro),
                links=links,
                volumes_from=volumes_from,
                command=command,
                port_bindings={
                    5000: port if is_boot2docker() else (address, port)},
                log_syslog=log_syslog
                )
        except APIError as e:
            if '409' in str(e):
                raise DatacatsError('Web container already running. '
                                    'Please stop_web before running.')
            else:
                raise

    def wait_for_web_available(self):
        """
        Wait for the web server to become available or raise DatacatsError
        if it fails to start.
        """
        try:
            if not wait_for_service_available(
                    self._get_container_name('web'),
                    self.web_address(),
                    WEB_START_TIMEOUT_SECONDS):
                raise DatacatsError('Error while starting web container:\n' +
                                    container_logs(self._get_container_name('web'), "all",
                                                   False, None))
        except ServiceTimeout:
            raise DatacatsError('Timeout while starting web container. Logs:' +
                                container_logs(self._get_container_name('web'), "all", False, None))

    def _choose_port(self):
        """
        Return a port number from 5000-5999 based on the environment name
        to be used as a default when the user hasn't selected one.
        """
        # instead of random let's base it on the name chosen (and the site name)
        return 5000 + unpack('Q',
                             sha((self.name + self.site_name)
                             .decode('ascii')).digest()[:8])[0] % 1000

    def _next_port(self, port):
        """
        Return another port from the 5000-5999 range
        """
        port = 5000 + (port + 1) % 1000
        if port == self.port:
            raise DatacatsError('Too many instances running')
        return port

    def stop_ckan(self):
        """
        Stop and remove the web container
        """
        remove_container(self._get_container_name('web'), force=True)
        remove_container(self._get_container_name('datapusher'), force=True)

    def _current_web_port(self):
        """
        return just the port number for the web container, or None if
        not running
        """
        info = inspect_container(self._get_container_name('web'))
        if info is None:
            return None
        try:
            if not info['State']['Running']:
                return None
            return info['NetworkSettings']['Ports']['5000/tcp'][0]['HostPort']
        except TypeError:
            return None

    def fully_running(self):
        """
        Returns true iff the environment is fully up and functioning.
        Returns False otherwise.
        """
        running = self.containers_running()
        return ('postgres' in running and
                'solr' in running and
                'web' in running)

    def containers_running(self):
        """
        Return a list of containers tracked by this environment that are running
        """
        return task.containers_running(self._get_container_name)

    def web_address(self):
        """
        Return the url of the web server or None if not running
        """
        port = self._current_web_port()
        address = self.address or '127.0.0.1'
        if port is None:
            return None
        return 'http://{0}:{1}/'.format(
            address if address and not is_boot2docker() else docker_host(),
            port)

    def create_admin_set_password(self, password):
        """
        create 'admin' account with given password
        """
        with open(self.sitedir + '/run/admin.json', 'w') as out:
            json.dump({
                'name': 'admin',
                'email': 'none',
                'password': password,
                'sysadmin': True},
                out)
        self.user_run_script(
            script=UPDATE_ADD_ADMIN,
            args=[],
            db_links=True,
            ro={
                self.sitedir + '/run/admin.json': '/input/admin.json'
               },
            )
        remove(self.sitedir + '/run/admin.json')

    def interactive_shell(self, command=None, paster=False, detach=False):
        """
        launch interactive shell session with all writable volumes

        :param: list of strings to execute instead of bash
        """
        if not exists(self.target + '/.bash_profile'):
            # this file is required for activating the virtualenv
            self.create_bash_profile()

        if not command:
            command = []
        use_tty = sys.stdin.isatty() and sys.stdout.isatty()

        background = environ.get('CIRCLECI', False) or detach

        if is_boot2docker():
            venv_volumes = ['--volumes-from', self._get_container_name('venv')]
        else:
            venv_volumes = ['-v', self.datadir + '/venv:/usr/lib/ckan:rw']

        self._create_run_ini(self.port, production=False, output='run.ini')
        self._create_run_ini(self.port, production=True, output='test.ini',
                             source='ckan/test-core.ini', override_site_url=False)

        script = SHELL
        if paster:
            script = PASTER
            if command and command != ['help'] and command != ['--help']:
                command += ['--config=/project/development.ini']
            command = [self.extension_dir] + command

        proxy_settings = self._proxy_settings()
        if proxy_settings:
            venv_volumes += ['-v',
                             self.sitedir + '/run/proxy-environment:/etc/environment:ro']

        # FIXME: consider switching this to dockerpty
        # using subprocess for docker client's interactive session
        return subprocess.call([
            DOCKER_EXE, 'run',
            ] + (['--rm'] if not background else []) + [
            '-t' if use_tty else '',
            '-d' if detach else '-i',
            ] + venv_volumes + [
            '-v', self.target + ':/project:rw',
            '-v', self.sitedir + '/files:/var/www/storage:rw',
            '-v', script + ':/scripts/shell.sh:ro',
            '-v', PASTER_CD + ':/scripts/paster_cd.sh:ro',
            '-v', self.sitedir + '/run/run.ini:/project/development.ini:ro',
            '-v', self.sitedir +
                '/run/test.ini:/project/ckan/test-core.ini:ro',
            '--link', self._get_container_name('solr') + ':solr',
            '--link', self._get_container_name('postgres') + ':db']
            + (['--link', self._get_container_name('datapusher') + ':datapusher']
               if self.needs_datapusher() else []) +
            ['--hostname', self.name,
            'datacats/web', '/scripts/shell.sh'] + command)

    def install_package_requirements(self, psrc, stream_output=None):
        """
        Install from requirements.txt file found in psrc

        :param psrc: name of directory in environment directory
        """
        package = self.target + '/' + psrc
        assert isdir(package), package
        reqname = '/requirements.txt'
        if not exists(package + reqname):
            reqname = '/pip-requirements.txt'
            if not exists(package + reqname):
                return
        return self.user_run_script(
            script=INSTALL_REQS,
            args=['/project/' + psrc + reqname],
            rw_venv=True,
            rw_project=True,
            stream_output=stream_output
            )

    def install_package_develop(self, psrc, stream_output=None):
        """
        Install a src package in place (setup.py develop)

        :param psrc: name of directory under project directory
        """
        package = self.target + '/' + psrc
        assert isdir(package), package
        if not exists(package + '/setup.py'):
            return
        return self.user_run_script(
            script=INSTALL_PACKAGE,
            args=['/project/' + psrc],
            rw_venv=True,
            rw_project=True,
            stream_output=stream_output
            )

    def user_run_script(self, script, args, db_links=False, rw_venv=False,
                        rw_project=False, rw=None, ro=None, stream_output=None):
        return self.run_command(
            command=['/scripts/run_as_user.sh', '/scripts/run.sh'] + args,
            db_links=db_links,
            rw_venv=rw_venv,
            rw_project=rw_project,
            rw=rw,
            ro=dict(ro or {}, **{
                RUN_AS_USER: '/scripts/run_as_user.sh',
                script: '/scripts/run.sh',
                }),
            stream_output=stream_output
            )

    def run_command(self, command, db_links=False, rw_venv=False,
                    rw_project=False, rw=None, ro=None, clean_up=False,
                    stream_output=None):

        rw = {} if rw is None else dict(rw)
        ro = {} if ro is None else dict(ro)

        ro.update(self._proxy_settings())

        if is_boot2docker():
            volumes_from = self._get_container_name('venv')
        else:
            volumes_from = None
            venvmount = rw if rw_venv else ro
            venvmount[self.datadir + '/venv'] = '/usr/lib/ckan'
        projectmount = rw if rw_project else ro
        projectmount[self.target] = '/project'

        if db_links:
            self._create_run_ini(self.port, production=False, output='run.ini')
            links = {
                self._get_container_name('solr'): 'solr',
                self._get_container_name('postgres'): 'db',
                }
            ro[self.sitedir + '/run/run.ini'] = '/project/development.ini'
        else:
            links = None

        return web_command(command=command, ro=ro, rw=rw, links=links,
                           volumes_from=volumes_from, clean_up=clean_up,
                           commit=True, stream_output=stream_output)

    def purge_data(self, which_sites=None, never_delete=False):
        """
        Remove uploaded files, postgres db, solr index, venv
        """
        # Default to the set of all sites
        if not which_sites:
            which_sites = self.sites

        datadirs = []
        boot2docker = is_boot2docker()

        if which_sites:
            if self.target:
                cp = SafeConfigParser()
                cp.read([self.target + '/.datacats-environment'])

            for site in which_sites:
                if boot2docker:
                    remove_container(self._get_container_name('pgdata'))
                else:
                    datadirs += [site + '/postgres']
                # Always rm the site dir & solr & files
                datadirs += [site, site + '/files', site + '/solr']
                if self.target:
                    cp.remove_section('site_' + site)
                    self.sites.remove(site)

            if self.target:
                with open(self.target + '/.datacats-environment', 'w') as conf:
                    cp.write(conf)

        datadirs = ['sites/' + datadir for datadir in datadirs]

        if not self.sites and not never_delete:
            datadirs.append('venv')

        web_command(
            command=['/scripts/purge.sh']
                + ['/project/data/' + d for d in datadirs],
            ro={PURGE: '/scripts/purge.sh'},
            rw={self.datadir: '/project/data'},
            )

        if not self.sites and not never_delete:
            shutil.rmtree(self.datadir)

    def logs(self, container, tail='all', follow=False, timestamps=False):
        """
        :param container: 'web', 'solr' or 'postgres'
        :param tail: number of lines to show
        :param follow: True to return generator instead of list
        :param timestamps: True to include timestamps
        """
        return container_logs(
            self._get_container_name(container),
            tail,
            follow,
            timestamps)

    def compile_less(self):
        c = run_container(
            name=self._get_container_name('lessc'), image='datacats/lessc',
            rw={self.target: '/project/target'},
            ro={COMPILE_LESS: '/project/compile_less.sh'})
        for log in container_logs(c['Id'], "all", True, False):
            yield log
        remove_container(c)

    def _proxy_settings(self):
        """
        Create/replace ~/.datacats/run/proxy-environment and return
        entry for ro mount for containers
        """
        if not ('https_proxy' in environ or 'HTTPS_PROXY' in environ
                or 'http_proxy' in environ or 'HTTP_PROXY' in environ):
            return {}
        https_proxy = environ.get('https_proxy')
        if https_proxy is None:
            https_proxy = environ.get('HTTPS_PROXY')
        http_proxy = environ.get('http_proxy')
        if http_proxy is None:
            http_proxy = environ.get('HTTP_PROXY')
        no_proxy = environ.get('no_proxy')
        if no_proxy is None:
            no_proxy = environ.get('NO_PROXY', '')
        no_proxy = no_proxy + ',solr,db'

        out = [
            'PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:'
            '/bin:/usr/games:/usr/local/games"\n']
        if https_proxy is not None:
            out.append('https_proxy=' + posix_quote(https_proxy) + '\n')
            out.append('HTTPS_PROXY=' + posix_quote(https_proxy) + '\n')
        if http_proxy is not None:
            out.append('http_proxy=' + posix_quote(http_proxy) + '\n')
            out.append('HTTP_PROXY=' + posix_quote(http_proxy) + '\n')
        if no_proxy is not None:
            out.append('no_proxy=' + posix_quote(no_proxy) + '\n')
            out.append('NO_PROXY=' + posix_quote(no_proxy) + '\n')

        with open(self.sitedir + '/run/proxy-environment', 'w') as f:
            f.write("".join(out))

        return {self.sitedir + '/run/proxy-environment': '/etc/environment'}

    def _get_container_name(self, container_type):
        """
        Gets the full name of a container of the type specified.
        Currently the supported types are:
            - 'venv'
            - 'postgres'
            - 'solr'
            - 'web'
            - 'pgdata'
            - 'lessc'
            - 'datapusher'
        The name will be formatted appropriately with any prefixes and postfixes
        needed.

        :param container_type: The type of container name to generate (see above).
        """
        if container_type in ['venv']:
            return 'datacats_{}_{}'.format(container_type, self.name)
        else:
            return 'datacats_{}_{}_{}'.format(container_type, self.name, self.site_name)


def posix_quote(s):
    return "\\'".join("'" + p + "'" for p in s.split("'"))
