# Copyright 2014-2015 Boxkite Inc.

# This file is part of the DataCats package and is released under
# the terms of the GNU Affero General Public License version 3.0.
# See LICENSE.txt or http://www.fsf.org/licensing/licenses/agpl-3.0.html

import sys
from os import listdir
from os.path import isdir, exists
from datacats.docker import container_logs

from clint.textui import colored

from datacats.cli import manage
from datacats.docker import check_connectivity
from datacats.error import DatacatsError
from datacats.environment import Environment


def install(environment, opts):
    """Install or reinstall Python packages within this environment

Usage:
  datacats install [-cq] [--address=IP] [ENVIRONMENT]

Options:
  --address=IP          The address to bind to when reloading after install [default: 127.0.0.1]
  -c --clean            Reinstall packages into a clean virtualenv
  -q --quiet            Do not show output from installing packages and requirements.

ENVIRONMENT may be an environment name or a path to an environment directory.
Default: '.'
"""
    environment.require_data()
    install_all(environment, opts['--clean'], verbose=not opts['--quiet'])

    for site in environment.sites:
        environment = Environment.load(environment.name, site)
        if 'web' in environment.containers_running():
            # FIXME: reload without changing debug setting?
            manage.reload_(environment, {
                '--address': opts['--address'],
                '--background': False,
                '--no-watch': False,
                '--production': False,
                'PORT': None,
                '--syslog': False,
                '--site-url': None,
                '--interactive': False
                })


def install_all(environment, clean, verbose=False, quiet=False):
    logs = check_connectivity()
    if logs.strip():
        raise DatacatsError(logs)

    srcdirs = set()
    reqdirs = set()
    for d in listdir(environment.target):
        fulld = environment.target + '/' + d
        if not isdir(fulld):
            continue
        if not exists(fulld + '/setup.py'):
            continue
        srcdirs.add(d)
        if (exists(fulld + '/requirements.txt') or
                exists(fulld + '/pip-requirements.txt')):
            reqdirs.add(d)
    try:
        srcdirs.remove('ckan')
        reqdirs.remove('ckan')
    except KeyError:
        raise DatacatsError('ckan not found in environment directory')

    if clean:
        environment.clean_virtualenv()
        environment.install_extra()

    for s in ['ckan'] + sorted(srcdirs):
        if verbose:
            print colored.yellow('Installing ' + s + '\n')
        elif not quiet:
            print 'Installing ' + s
        environment.install_package_develop(s, sys.stdout if verbose and not quiet else None)
        if verbose and not quiet:
            print
    for s in ['ckan'] + sorted(reqdirs):
        if verbose:
            print colored.yellow('Installing ' + s + ' requirements' + '\n')
        elif not quiet:
            print 'Installing ' + s + ' requirements'
        environment.install_package_requirements(s, sys.stdout if verbose and not quiet else None)
        if verbose:
            print


def _print_logs(c_id):
    for item in container_logs(c_id, "all", True, None):
        print item
