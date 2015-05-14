class DatacatsError(Exception):
    def __init__(self, message, format_args=()):
        self.message = message
        self.format_args = format_args
        super(DatacatsError, self).__init__(message, format_args)

    def __str__(self):
        return self.message.format(*self.format_args)
