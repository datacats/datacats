def less(environment, opts):
    """Recompiles less files in an environment.

Usage:
  datacats less [ENVIRONMENT]

ENVIRONMENT may be an environment name or a path to an environment directory.
Default: '.'
"""
    print 'Converting .less files to .css...'
    environment.compile_less()
