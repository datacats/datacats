# Copyright 2014-2015 Boxkite Inc.

# This file is part of the DataCats package and is released under
# the terms of the GNU Affero General Public License version 3.0.
# See LICENSE.txt or http://www.fsf.org/licensing/licenses/agpl-3.0.html

from unittest import TestCase

from datacats.cli.main import _subcommand_arguments


def _s(cmd):
    command, args = _subcommand_arguments(cmd.split())
    return command, ' '.join(args)


class TestParseArguments(TestCase):
    def test_help(self):
        self.assertEqual(_s('help'), (None, '--help'))

    def test_help_long_option(self):
        self.assertEqual(_s('--help'), (None, '--help'))

    def test_help_short_option(self):
        self.assertEqual(_s('-h'), (None, '-h'))
