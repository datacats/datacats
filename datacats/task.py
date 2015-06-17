# Copyright 2014-2015 Boxkite Inc.

# This file is part of the DataCats package and is released under
# the terms of the GNU Affero General Public License version 3.0.
# See LICENSE.txt or http://www.fsf.org/licensing/licenses/agpl-3.0.html

"""
This modle includes the implementations for many Environment methods
separated from their configuration object to make them easier to test.
"""

# import modules not names inside so tests can mock functions
# inside these modules more easily
import os
from os import path
import ConfigParser

from datacats import docker, validate
from datacats.error import DatacatsError


def list_sites(datadir):
    """
    Return a list of the site names valid for this environment
    """
    try:
        return os.listdir(datadir + '/sites')
    except OSError:
        return []


def save_site(site_name, sitedir, srcdir, port, address, site_url, passwords):
    """
    Add a site's configuration to the source dir and site dir
    """
    cp = ConfigParser.SafeConfigParser()
    cp.read([srcdir + '/.datacats-environment'])

    section_name = 'site_' + site_name

    cp.add_section(section_name)
    cp.set(section_name, 'port', str(port))
    cp.set(section_name, 'address', address or '127.0.0.1')

    if site_url:
        cp.set(section_name, 'site_url', site_url)

    with open(srcdir + '/.datacats-environment', 'w') as config:
        cp.write(config)

    # save passwords to datadir
    cp = ConfigParser.SafeConfigParser()

    cp.add_section('passwords')
    for n in sorted(passwords):
        cp.set('passwords', n.lower(), passwords[n])

    # Write to the sitedir so we maintain separate passwords.
    with open(sitedir + '/passwords.ini', 'w') as config:
        cp.write(config)


def save(name, datadir, srcdir, ckan_version, deploy_target=None,
        always_prod=False):
    """
    Save an environment's configuration to the source dir and data dir
    """
    with open(datadir + '/.version', 'w') as f:
        f.write('2')

    cp = ConfigParser.SafeConfigParser()

    cp.add_section('datacats')
    cp.set('datacats', 'name', name)
    cp.set('datacats', 'ckan_version', ckan_version)

    if deploy_target:
        cp.add_section('deploy')
        cp.set('deploy', 'target', deploy_target)

    if always_prod:
        cp.set('datacats', 'always_prod', 'true')

    with open(srcdir + '/.datacats-environment', 'w') as config:
        cp.write(config)

    save_srcdir_location(datadir, srcdir)


def save_srcdir_location(datadir, srcdir):
    """
    Store the location of srcdir in datadir/project-dir
    """
    # project-dir because backwards compatibility
    with open(datadir + '/project-dir', 'w') as pdir:
        pdir.write(srcdir)


def new_environment_check(srcpath, site_name):
    """
    Check if a new environment or site can be created at the given path.

    Returns (name, datadir, sitedir, srcdir) or raises DatacatsError
    """
    workdir, name = path.split(path.abspath(path.expanduser(srcpath)))

    if not validate.valid_name(name):
        raise DatacatsError('Please choose an environment name starting'
                            ' with a letter and including only lowercase letters'
                            ' and digits')
    if not path.isdir(workdir):
        raise DatacatsError('Parent directory for environment'
                            ' does not exist')

    docker.require_images()

    datadir = path.expanduser('~/.datacats/' + name)
    sitedir = datadir + '/sites/' + site_name
    # We track through the datadir to the target if we are just making a
    # site
    if path.isdir(datadir):
        with open(datadir + '/project-dir') as pd:
            srcdir = pd.read()
    else:
        srcdir = workdir + '/' + name

    if path.isdir(sitedir):
        raise DatacatsError('Site data directory {0} already exists'.format(
                            sitedir))
    # This is the case where the data dir has been removed,
    if path.isdir(srcdir) and not path.isdir(datadir):
        raise DatacatsError('Environment directory exists, but data directory does not.\n'
                            'If you simply want to recreate the data directory, run '
                            '"datacats init" in the environment directory.')

    return name, datadir, srcdir


def data_complete(datadir, sitedir, get_container_name):
    """
    Return True if the directories and containers we're expecting
    are present in datadir, sitedir and containers
    """
    if any(not path.isdir(sitedir + x)
            for x in ('/files', '/run', '/solr')):
        return False

    if docker.is_boot2docker():
        # Inspect returns None if the container doesn't exist.
        return all(docker.inspect_container(get_container_name(x))
                for x in ('pgdata', 'venv'))

    return path.isdir(datadir + '/venv') and path.isdir(sitedir + '/postgres')


def source_missing(srcdir):
    """
    Return list of expected files missing from source directory srcdir
    """
    return [
        x for x in ('schema.xml', 'ckan', 'development.ini', 'who.ini')
        if not path.exists(srcdir + '/' + x)]


def create_directories(datadir, sitedir, srcdir=None):
    """
    Create expected directories in datadir, sitedir
    and optionally srcdir
    """
    # It's possible that the datadir already exists
    # (we're making a secondary site)
    if not path.isdir(datadir):
        os.makedirs(datadir, mode=0o700)
    try:
        # This should take care if the 'site' subdir if needed
        os.makedirs(sitedir, mode=0o700)
    except OSError:
        raise DatacatsError("Site already exists.")

    # venv isn't site-specific, the rest are.
    if not docker.is_boot2docker():
        if not path.isdir(datadir + '/venv'):
            os.makedirs(datadir + '/venv')
        os.makedirs(sitedir + '/postgres')
    os.makedirs(sitedir + '/solr')
    os.makedirs(sitedir + '/files')
    os.makedirs(sitedir + '/run')

    if srcdir:
        os.makedirs(srcdir)


def create_virtualenv(datadir, preload_image, get_container_name):
    """
    Populate venv from preloaded image
    """
    if docker.is_boot2docker():
        docker.data_only_container(
            get_container_name('venv'),
            ['/usr/lib/ckan'],
            )
        img_id = docker.web_command(
            '/bin/mv /usr/lib/ckan/ /usr/lib/ckan_original',
            image=preload_image,
            commit=True,
            )
        docker.web_command(
            command='/bin/cp -a /usr/lib/ckan_original/. /usr/lib/ckan/.',
            volumes_from=get_container_name('venv'),
            image=img_id,
            )
        docker.remove_image(img_id)
        return

    docker.web_command(
        command='/bin/cp -a /usr/lib/ckan/. /usr/lib/ckan_target/.',
        rw={datadir + '/venv': '/usr/lib/ckan_target'},
        image=preload_image,
        )
