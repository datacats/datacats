from clint.textui import colored


class DatacatsError(Exception):

    def __init__(self, message, format_args=(), parent_exception=None):
        self.message = message
        if parent_exception:
            self.message += '\n\n' + '~' * 30 + \
                "\nTechnical Details:\n" + \
                parent_exception.__str__() + \
                '~' * 30 + '\n'
        self.format_args = format_args
        super(DatacatsError, self).__init__(message, format_args)

    def __str__(self):
        return self.message.format(*self.format_args)

    def pretty_print(self):
        """
        Print the error message to stdout with colors and borders
        """
        print colored.blue("-" * 40)
        print colored.red("datacats: problem was encountered:")
        for line in self.message.format(*self.format_args).split('\n'):
            print "  ", line
        print colored.blue("-" * 40)


class WebCommandError(Exception):

    def __init__(self, command, container_id, logs):
        self.command = command
        self.container_id = container_id
        self.logs = logs

    def __str__(self):
        return \
            ('\nDocker container "/web" command failed\n'
             '    Command: {0}\n'
             '    Docker Error Log:\n'
             '    {1}\n'
             ).format(" ".join(self.command), self.logs, self.container_id)


class RemoteCommandError(WebCommandError):
    def __init__(self, base_WebCommandError):
        self.__dict__ = base_WebCommandError.__dict__

    def __str__(self):
        return \
            ('\nSending a command to remote server failed\n'
             '    Command: {0}\n'
             '    Docker Error Log:\n'
             '    {1}\n'
             ).format(" ".join(self.command), self.logs, self.container_id)


class PortAllocatedError(Exception):
    pass
