"""
Watches a CKAN environment for changes in its .less files, and recompiles them when they do.

Usage:
  datacats-lesscd [--help] TARGET

  --help -h         Show this help and quit.
"""

from os.path import expanduser, join as path_join
import signal

from docopt import docopt
from datacats.version import __version__
from datacats.environment import Environment
from datacats.cli.less import less

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileModifiedEvent


# None to start off with, defined in main()
environment = None


class LessCompileEventHandler(FileSystemEventHandler):
    def __init__(self, environment):
        self.environment = environment

    def on_modified(self, event):
        if isinstance(event, FileModifiedEvent):
            less(self.environment, {})


def main():
    opts = docopt(__doc__, version=__version__)
    env_path = expanduser(opts['TARGET'])
    environment = Environment.load(env_path)
    # Path to less files in ckan. This is the path we're gonna watch.
    less_path = path_join(env_path, 'ckan', 'ckan', 'public', 'base', 'less')
    observer = Observer()
    event_handler = LessCompileEventHandler(environment)
    observer.schedule(event_handler, less_path, recursive=True)
    observer.start()

    # HACK: We make it so that the OS doesn't consult us and just kills us.
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    observer.join()
