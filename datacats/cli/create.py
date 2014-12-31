# Copyright 2014-2015 Boxkite Inc.

# This file is part of the DataCats package and is released under
# the terms of the GNU Affero General Public License version 3.0.
# See LICENSE.txt or http://www.fsf.org/licensing/licenses/agpl-3.0.html

import sys

from datacats.project import Project, ProjectError

def write(s):
    sys.stdout.write(s)
    sys.stdout.flush()

def create(opts):
    try:
        project = Project.new(opts['PROJECT'], 'master', opts['PORT'])
    except ProjectError as e:
        print e
        return

    write('Creating project "{0}"'.format(project.name))

    steps = [
        project.create_directories,
        project.save,
        project.create_virtualenv,
        project.create_source,
        project.start_data_and_search,
        project.fix_storage_permissions,
        project.create_ckan_ini,
        lambda: project.update_ckan_ini(skin=not opts['--bare']),
        project.fix_project_permissions,
        ]

    if not opts['--bare']:
        steps.append(project.create_install_template_skin)

    steps.append(project.ckan_db_init)

    for fn in steps:
        fn()
        write('.')

    if not opts['--image-only']:
        project.start_web()
        write('.\n')
        write('Site available at {0}\n'.format(project.web_address()))

    if not opts['--no-sysadmin']:
        write('\n')
        project.interactive_set_admin_password()

    if opts['--image-only']:
        project.stop_data_and_search()
        write('.\n')
