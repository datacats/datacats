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
  datacats install [-p PROJECT]
  datacats purge [-p PROJECT]

Options:
  -f --follow                     Follow logs
  -i --image-only                 Only create the project, don't start containers
  -r --remote                     Operate on cloud-deployed datacats instance
  -p --project=PROJECT            Use project named PROJECT, defaults to use
                                  project from current working directory
  -q --quiet                      Simple text response suitable for scripting
  -v --ckan-version=CKAN_VERSION  Use CKAN version CKAN_VERSION, defaults to
                                  latest stable release
"""

import json
from docopt import docopt

def main():
    print json.dumps(docopt(__doc__), indent=4)
