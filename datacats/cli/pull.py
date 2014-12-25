import sys
import json

from datacats.docker import pull_stream

IMAGES = [
    'datacats/web',
    'datacats/web:preload_master',
    'datacats/data',
    'datacats/search',
    'scratch',
    ]

def pull(opts):
    """
    Pull down all docker images used by DataCats
    """

    sameline = False
    for i in IMAGES:
        sys.stdout.write('Pulling image '+ i)
        sys.stdout.flush()
        for s in pull_stream(i):
            if 'status' not in s:
                print json.dumps(s, indent=2)
                continue
            if s['status'] == 'Download complete':
                sys.stdout.write('.')
                sys.stdout.flush()
                continue
        sys.stdout.write('\n')
