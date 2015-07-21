import sys
from datacats import docker
from datacats.cli.pull import pull_image
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
        pull_image(image_name)


class CLIProgressTracker(object):
    """
    CliProgressTracker helps render a TTY progress bar
    and show progress to the user.

    The update_state function signature is similar to the one
    that is used by celery so the advantage is that
    functions that use this progress progress bar
    can be tied up to celery easily.

    Here is an example of use:
        with CliProgressTracker(
            task_title="", total=13) as pt:
            for i in range(14):
                pt.update_state(
                    state='PROGRESS',
                    meta={
                        'current': i,
                        'total': 13,
                        'status':'sup'}
                    )
    """
    BAR_TEMPLATE = "{title} : [{filled_bar}{empty_bar}] {percent}% : {status}..."
    symbol_width = 50

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.clean_up()
        return False  # not surpressing exceptions

    def __init__(self, task_title, total=100, stream=sys.stderr, quiet=False):
        self.quiet = quiet
        if self.quiet:
            return
        self.current = 0
        self.title = task_title
        self.total = total
        self.status = "Starting"
        self.stream = stream
        # when updating message we need to make sure we overwite the prev one
        # with the same number of symbols (as tty sucks as a UI)
        # so will store len of prev message too
        self.prev_sym_len = 0
        self.rendered = False
        self.stream.write("\n")
        self.show()

    def update_state(self, state='PROGRESS', meta=None):
        """
         Update the state of the progress bar.
        """
        if not (state == 'PROGRESS'):
            self.clean_up()
            return
        if self.quiet:
            return
        if not meta:
            return
        self.current = meta.get('current', self.current)
        if 'status' in meta:
            self.prev_status_len = len(self.status)
            self.status = meta.get('status')
        self.show()

    def show(self):
        percent = int(100.0 * float(self.current) / float(self.total))
        filled_bar_num = int(self.symbol_width * float(percent) / 100.0)
        empty_bar_num = self.symbol_width - filled_bar_num
        output_str = self.BAR_TEMPLATE.format(
            title=self.title,
            filled_bar="=" * filled_bar_num,
            empty_bar=" " * empty_bar_num,
            percent=percent,
            status=self.status
        )
        self.stream.write(output_str)
        if len(output_str) < self.prev_sym_len:
            self.stream.write(" " * (self.prev_sym_len - len(output_str)))
        self.prev_sym_len = len(output_str)
        self.stream.write("\r")
        self.stream.flush()

    def clean_up(self):
        """
        Clean up after the progress bar by
        overwriting whatever was printed so far with white spaces
        """
        if self.quiet:
            return
        self.stream.write(" " * self.prev_sym_len)
        self.prev_sym_len = 0
        self.stream.write("\r")
        self.stream.flush()


def function_as_step(func, description=None):
    """
    Returns a tuple of function and first string of docstring
    to provide the user is some details on what the function does

    For procedures with a lot of steps or that take a long time
    one would like to print out a status message
    to the user to provide her with more details of
    what is going on.
    """
    if description:
        return func, description
    if func.__doc__:
        doc_lines = func.__doc__.split('\n')
        if len(doc_lines) > 0:
            return func, doc_lines[1].lstrip().rstrip()
    return func, func.__name__
