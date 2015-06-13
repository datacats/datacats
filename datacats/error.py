from clint.textui import colored


class DatacatsError(Exception):

    def __init__(self, message, format_args=(), parent_exception=None):
        self.message = message
        if parent_exception and hasattr(parent_exception, 'user_description'):
            vals = {
                "original": self.message,
                "type_description": parent_exception.user_description,
                "message": str(parent_exception),
            }
            self.message = "".join([str(colored.blue("{original}\n\n")),
                                    "~" * 30,
                                    "\n{type_description}:\n",
                                    str(colored.yellow("{message}\n"))]
                                    ).format(**vals)

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
        print self.message.format(*self.format_args)
        print colored.blue("-" * 40)


class WebCommandError(Exception):
    user_description = "Docker container \"/web\" command failed"

    def __init__(self, command, container_id, logs):
        # pylint: disable=unused-argument
        super(WebCommandError, self).__init__()
        self.command = command
        self.container_id = container_id
        self.logs = logs

    def __str__(self):
        return ('    Command: {0}\n'
                '    Docker Error Log:\n'
                '    {1}\n'
                ).format(''.join(self.command), self.logs)


class PortAllocatedError(Exception):
    user_description = "Unable to allocate port"


class UndocumentedError(Exception):
    user_description = "Please quote this traceback when reporting this error"
