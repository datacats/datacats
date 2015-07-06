#!/usr/bin/env python2

# Takes two arguments - JSON for a dictionary

# We use this so we don't have to depend on Bash 4 (which has dictionary features, but isn't in Mac OS X 10.11 or
# earlier)

import sys
import json

if __name__ == '__main__':
    json_text = sys.argv[1]
    key = sys.argv[2]
    data = json.loads(json_text)
    sys.stdout.write(data[key])
    sys.stdout.flush()
