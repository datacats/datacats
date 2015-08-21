import sys
from datacats import docker
from datacats.cli.pull import retrying_pull_image
from getpass import getpass


def confirm_password():
    while True:
        p1 = getpass('admin user password:')
        if len(p1) < 4:
            print 'At least 4 characters are required'
            continue
        p2 = getpass('confirm password:')
        if p1 == p2:
            return p1
        print 'Passwords do not match'


def y_or_n_prompt(statement_of_risk):
    inp = None
    # Nothing (default, n), y and n are our valid inputs
    while inp is None or inp.lower()[:1] not in ['y', 'n', '']:
        inp = raw_input('{}. Are you sure? [n] (y/n): '.format(statement_of_risk))

    if inp.lower()[:1] == 'n' or not inp:
        print 'Aborting by user request.'
        sys.exit(0)


def require_extra_image(image_name):
    if not docker.image_exists(image_name):
        retrying_pull_image(image_name)
