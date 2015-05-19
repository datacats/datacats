from clint.textui import colored


class DatacatsError(Exception):

    def __init__(self, message, format_args=(), parent_exception=None):
        self.message = message
        if parent_exception:
            self.message  += '\n\n' + '~' * 30 + \
                "\nTechnical Details:\n" + \
                parent_exception.__str__() + \
                '~' * 30  + '\n'
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
