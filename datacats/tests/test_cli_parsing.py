# Copyright 2014-2015 Boxkite Inc.

# This file is part of the DataCats package and is released under
# the terms of the GNU Affero General Public License version 3.0.
# See LICENSE.txt or http://www.fsf.org/licensing/licenses/agpl-3.0.html

from unittest import TestCase

from datacats.cli.main import _subcommand_arguments
from datacats.error import DatacatsError


def _s(cmd):
    "helper to make our tests shorter"
    command, args = _subcommand_arguments(cmd.split())
    return command, ' '.join(args)


class TestParseArguments(TestCase):
    def test_help(self):
        self.assertEqual(_s('help'), (None, '--help'))

    def test_help_long_option(self):
        self.assertEqual(_s('--help'), (None, '--help'))

    def test_help_short_option(self):
        self.assertEqual(_s('-h'), (None, '-h'))

    def test_bad_subcommand(self):
        self.assertRaises(DatacatsError, _s, 'whatsup')

    def test_help_subcommand(self):
        self.assertEqual(_s('help info'), ('info', '--help info'))

    def test_subcommand(self):
        self.assertEqual(_s('info'), ('info', 'info'))

    def test_subcommand_option_first(self):
        self.assertEqual(_s('-q info'), ('info', '-q info'))

    def test_subcommand_option_last(self):
        self.assertEqual(_s('info -q'), ('info', 'info -q'))

    def test_shell_positional_only(self):
        self.assertEqual(_s('shell a b c d'), ('shell', 'shell a -- b c d'))

    def test_shell_option_last(self):
        self.assertEqual(_s('shell a b c -d'), ('shell', 'shell a -- b c -d'))

    def test_shell_option_after_inner_command(self):
        self.assertEqual(_s('shell a b -c d'), ('shell', 'shell a -- b -c d'))

    def test_shell_option_before_inner_command(self):
        self.assertEqual(_s('shell a -b c d'), ('shell', 'shell a -b -- c d'))

    def test_shell_option_first(self):
        self.assertEqual(_s('shell -a b c d'), ('shell', 'shell -a b -- c d'))

    def test_shell_site_short_first(self):
        self.assertEqual(_s('shell -s a b c d'),
            ('shell', 'shell -s a b -- c d'))

    def test_shell_site_long_first(self):
        self.assertEqual(_s('shell --site a b c d'),
            ('shell', 'shell --site a b -- c d'))

    def test_shell_site_long_equals_first(self):
        self.assertEqual(_s('shell --site=a b c d'),
            ('shell', 'shell --site=a b -- c d'))

    def test_shell_site_short_before_inner_command(self):
        self.assertEqual(_s('shell a -s b c d'),
            ('shell', 'shell a -s b -- c d'))

    def test_shell_site_long_before_inner_command(self):
        self.assertEqual(_s('shell a --site b c d'),
            ('shell', 'shell a --site b -- c d'))

    def test_shell_site_long_equals_before_inner_command(self):
        self.assertEqual(_s('shell a --site=b c d'),
            ('shell', 'shell a --site=b -- c d'))

    def test_shell_site_short_after_inner_command(self):
        self.assertEqual(_s('shell a b -s c d'),
            ('shell', 'shell a -- b -s c d'))

    def test_shell_site_long_after_inner_command(self):
        self.assertEqual(_s('shell a b --site c d'),
            ('shell', 'shell a -- b --site c d'))

    def test_shell_site_long_equals_after_inner_command(self):
        self.assertEqual(_s('shell a b --site=c d'),
            ('shell', 'shell a -- b --site=c d'))

    def test_paster_positional_only(self):
        self.assertEqual(_s('paster a b c'), ('paster', 'paster -- a b c'))

    def test_paster_option_last(self):
        self.assertEqual(_s('paster a b -c'), ('paster', 'paster -- a b -c'))

    def test_paster_option_after_inner_command(self):
        self.assertEqual(_s('paster a -b c'), ('paster', 'paster -- a -b c'))

    def test_paster_option_before_inner_command(self):
        self.assertEqual(_s('paster -a b c'), ('paster', 'paster -a -- b c'))

    def test_paster_site_short_after_inner_command(self):
        self.assertEqual(_s('paster a -s b c'),
            ('paster', 'paster -- a -s b c'))

    def test_paster_site_short_before_inner_command(self):
        self.assertEqual(_s('paster -s a b c'),
            ('paster', 'paster -s a -- b c'))
