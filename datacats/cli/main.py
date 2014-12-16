"""datacats command line interface

Usage:
  datacats create (. | PROJECT) [-v CKAN_VERSION] [-i]
  datacats start [-p PROJECT] [-r]
  datacats stop [-p PROJECT] [-r]
  datacats restart [-p PROJECT] [-r]
  datacats deploy [-p PROJECT]
  datacats logs [-p PROJECT] [-f]
  datacats info [-p PROJECT] [-q] [-r]
  datacats open [-p PROJECT]
  datacats paster [-p PROJECT] PASTER_COMMAND...
  datacats install [-p PROJECT] [-c]
  datacats purge [-p PROJECT] [-y]

Options:
  -c --clean                  Reinstall into a clean virtual environment
  -f --follow                 Follow logs
  -i --image-only             Only create the project, don't start containers
  -r --remote                 Operate on cloud-deployed datacats instance
  -p --project=PROJECT        Use project named PROJECT, defaults to use
                              project from current working directory
  -q --quiet                  Simple text response suitable for scripting
  -v --version=CKAN_VERSION   Use CKAN version CKAN_VERSION, defaults to
                              latest development release
  -y --yes                    don't ask for confirmation
"""

import json
import sys
from docopt import docopt

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
    option_not_yet_implemented(opts, '--project')
    command_not_yet_implemented(opts, 'start')
    command_not_yet_implemented(opts, 'stop')
    command_not_yet_implemented(opts, 'deploy')
    command_not_yet_implemented(opts, 'logs')
    command_not_yet_implemented(opts, 'info')
    command_not_yet_implemented(opts, 'paster')
    command_not_yet_implemented(opts, 'purge')

    print json.dumps(docopt(__doc__), indent=4)
