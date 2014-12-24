import sys

from datacats.project import Project, ProjectError

def write(s):
    sys.stdout.write(s)
    sys.stdout.flush()

def create(opts):
    try:
        project = Project.new(opts['PROJECT'], 'master')
    except ProjectError as e:
        print e
        return

    write('Creating project "{0}"'.format(project.name))

    for fn in (
            project.create_directories,
            project.save,
            project.create_virtualenv,
            project.create_source,
            project.start_data_and_search,
            project.fix_storage_permissions,
            project.create_ckan_ini,
            project.update_ckan_ini,
            project.fix_project_permissions,
            project.ckan_db_init,
            ):
        fn()
        write('.')

    if opts['--image-only']:
        project.stop_data_and_search()
        write('\n')
    else:
        project.start_web()
        write('.\n')
        ip = project.web_ipaddress()
        write('Site available at http://{0}/\n'.format(ip))

    if opts['--no-sysadmin']:
        return

    write('\n')
    project.interactive_set_admin_password()
