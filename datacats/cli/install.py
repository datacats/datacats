import sys
from os import listdir
from os.path import isdir

def write(s):
    sys.stdout.write(s)
    sys.stdout.flush()

def install(project, opts):
    """
    Install all packages found in the project src directory
    and their requirements.txt files
    """
    srcdirs = set(listdir(project.target + '/src'))
    try:
        srcdirs.remove('ckan')
    except KeyError:
        print 'ckan not found in project src directory'
        return

    write('Installing')

    srcdirs = ['ckan'] + sorted(srcdirs)
    for s in srcdirs:
        project.install_package_requirements(s)
        write('.')
    for s in srcdirs:
        project.install_package_develop(s)
        write('.')
    write('\n')
