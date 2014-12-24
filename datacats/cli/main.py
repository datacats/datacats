"""datacats command line interface

Usage:
  datacats create PROJECT [-i] [-n] [--ckan=CKAN_VERSION]
  datacats start [-p PROJECT] [-r]
  datacats stop [-p PROJECT] [-r]
  datacats reload [-p PROJECT] [-r]
  datacats deploy [-p PROJECT]
  datacats logs [-p PROJECT] [-f]
  datacats info [-p PROJECT] [-q] [-r]
  datacats open [-p PROJECT]
  datacats paster [-p PROJECT] PASTER_COMMAND...
  datacats install [-p PROJECT] [-c]
  datacats purge [-p PROJECT] [-y]

Options:
  -c --clean                  Reinstall into a clean virtual environment
  --ckan=CKAN_VERSION         Use CKAN version CKAN_VERSION, defaults to
                              latest development release
  -f --follow                 Follow logs
  -i --image-only             Only create the project, don't start containers
  -r --remote                 Operate on cloud-deployed datacats instance
  -n --no-sysadmin            Don't create an initial sysadmin user account
  -p --project=PROJECT        Use project named PROJECT, defaults to use
                              project from current working directory
  -q --quiet                  Simple text response suitable for scripting
  -y --yes                    don't ask for confirmation
"""

import json
import sys
from docopt import docopt

from datacats.cli import create, manage, install
from datacats.project import Project, ProjectError

def option_not_yet_implemented(opts, name):
    if not opts[name]:
        return
    print "Option {0} is not yet implemented.".format(name)
    sys.exit(1)

def command_not_yet_implemented(opts, name):
    if not opts[name]:
        return
    print "Command {0} is not yet implemented.".format(name)
    sys.exit(1)

def main():
    opts = docopt(__doc__)
    option_not_yet_implemented(opts, '--project')
    option_not_yet_implemented(opts, '--ckan')
    command_not_yet_implemented(opts, 'deploy')
    command_not_yet_implemented(opts, 'logs')
    command_not_yet_implemented(opts, 'info')
    command_not_yet_implemented(opts, 'paster')
    command_not_yet_implemented(opts, 'purge')

    if opts['create']:
        return create.create(opts)

    try:
        project = Project.load(opts['PROJECT'])
    except ProjectError as e:
        print e
        return

    if opts['stop']:
        return manage.stop(project)
    if opts['start']:
        return manage.start(project)
    if opts['reload']:
        return manage.reload(project)
    if opts['install']:
        return install.main(project, op)

    print json.dumps(docopt(__doc__), indent=4)
