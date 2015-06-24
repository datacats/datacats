"""
Watches a CKAN environment for changes in its .less files, and recompiles them when they do.

Usage:
  datacats-lesscd [--help] ENVIRONMENT

  --help -h         Show this help and quit.

ENVIRONMENT may be an environment name or a path to an environment directory.
Default: '.'
"""

from os.path import join as path_join, exists
import signal

from docopt import docopt
from datacats.version import __version__
from datacats.environment import Environment
from datacats.cli.less import less

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileModifiedEvent


class LessCompileEventHandler(FileSystemEventHandler):
    def __init__(self, environment):
        self.environment = environment

    def on_modified(self, event):
        if isinstance(event, FileModifiedEvent):
            less(self.environment, {})


def main():
    opts = docopt(__doc__, version=__version__)
    environment = Environment.load(opts['ENVIRONMENT'] or '.')
    env_path = environment.target
    less_paths = [
        path_join(env_path, 'ckan', 'ckan', 'public', 'base', 'less'),
        path_join(env_path, 'ckan', 'ckan', 'public', 'base', 'vendor')
    ]

    if not env_path or not all(exists(less_path) for less_path in less_paths):
        print 'No source code to watch found'
        return

    observer = Observer()
    event_handler = LessCompileEventHandler(environment)
    for less_path in less_paths:
        observer.schedule(event_handler, less_path, recursive=True)
    observer.start()

    # HACK: We make it so that the OS doesn't consult us and just kills us.
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    observer.join()
