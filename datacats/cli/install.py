# Copyright 2014-2015 Boxkite Inc.

# This file is part of the DataCats package and is released under
# the terms of the GNU Affero General Public License version 3.0.
# See LICENSE.txt or http://www.fsf.org/licensing/licenses/agpl-3.0.html

import sys
from os import listdir
from os.path import isdir, exists

from datacats.cli import manage

def write(s):
    sys.stdout.write(s)
    sys.stdout.flush()

def install(project, opts):
    """Install or reinstall Python packages within this environment

Usage:
  datacats install [-c] [ENVIRONMENT]

Options:
  -c --clean         Reinstall packages into a clean virtualenv

ENVIRONMENT may be an environment name or a path to an environment directory.
Default: '.'
"""
    project.require_data()
    install_all(project, opts['--clean'])

    if 'web' in project.containers_running():
        # FIXME: reload without changing debug setting?
        manage.reload_(project, {
            '--production': False,
            'PORT': None,
            '--background': False})

def install_all(project, clean):
    srcdirs = set()
    reqdirs = set()
    for d in listdir(project.target):
        fulld = project.target + '/' + d
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
        print 'ckan not found in environment directory'
        return

    for s in ['ckan'] + sorted(reqdirs):
        write('Installing ' + s + ' requirements')
        project.install_package_requirements(s)
        write('\n')
    for s in ['ckan'] + sorted(srcdirs):
        write('Installing ' + s)
        project.install_package_develop(s)
        write('\n')
