from datacats.cli.pull import _retry_func
from datacats.error import DatacatsError
from unittest import TestCase


def raise_an_error(_):
    raise DatacatsError('Hi')


class TestPullCli(TestCase):
    def test_cli_pull_retry(self):
        def count(*dummy, **_):
            count.counter += 1
        count.counter = 0

        try:
            _retry_func(raise_an_error, None, 5, count,
                        'Error! We wanted this to happen')
            self.fail('Exception was not raised.')
        except DatacatsError as e:
            self.assertEqual(count.counter, 4)
            self.failIf('We wanted this to happen' not in str(e))
