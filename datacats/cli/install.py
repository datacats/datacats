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
    """Install or reinstall Python packages within this project

Usage:
  datacats install [PROJECT] [-c]

Options:
  -c --clean         Reinstall into a clean virtualenv

PROJECT may be a project name or a path to a project directory. Default: '.'
"""
    clean = opts['--clean']

    srcdirs = set()
    reqdirs = set()
    for d in listdir(project.target):
        fulld = project.target + '/' + d
        if not isdir(fulld):
            continue
        if not exists(fulld + '/setup.py'):
            continue
        srcdirs.add(d)
        if exists(fulld + '/requirements.txt'):
            reqdirs.add(d)
    try:
        srcdirs.remove('ckan')
        reqdirs.remove('ckan')
    except KeyError:
        print 'ckan not found in project directory'
        return

    for s in ['ckan'] + sorted(reqdirs):
        write('Installing ' + s + ' requirements')
        project.install_package_requirements(s)
        write('\n')
    for s in ['ckan'] + sorted(srcdirs):
        write('Installing ' + s)
        project.install_package_develop(s)
        write('\n')

    if 'web' in project.containers_running():
        # FIXME: reload without changing debug setting?
        manage.reload_(project, {'--production': False})
