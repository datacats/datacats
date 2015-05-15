from clint.textui import colored


class DatacatsError(Exception):

    def __init__(self, message, format_args=()):
        self.message = message
        self.format_args = format_args
        super(DatacatsError, self).__init__(message, format_args)

    def __str__(self):
        return self.message.format(*self.format_args)

    def pretty_print(self):
        """
        Print the error message to stdout with colors and borders
        """
        print colored.blue("-" * 40)
        print colored.red("DATACATS: serious problem was encountered:")
        for line in self.message.format(*self.format_args).split('\n'):
            print "  ", line
        print colored.blue("-" * 40)
