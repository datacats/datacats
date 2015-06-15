import sys


def y_or_n_prompt(statement_of_risk):
    inp = None
    # Nothing (default, n), y and n are our valid inputs
    while inp is None or inp.lower()[:1] not in ['y', 'n', '']:
        inp = raw_input('{}. Are you sure? [n] (y/n): '.format(statement_of_risk))

    if inp.lower()[:1] == 'n' or not inp:
        print 'Aborting by user request.'
        sys.exit(0)
