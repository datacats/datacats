def migrate(environment, opts):
    """Stop serving environment and remove all its containers

Usage:
  datacats migrate [ENVIRONMENT]

Migrates an environment to the newer datadir format if necessary.
Defaults to '.' if ENVIRONMENT_DIR isn't specified.
"""
    # Load will take care of the actual work
    pass
