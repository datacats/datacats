# Copyright 2014-2015 Boxkite Inc.

# This file is part of the DataCats package and is released under
# the terms of the GNU Affero General Public License version 3.0.
# See LICENSE.txt or http://www.fsf.org/licensing/licenses/agpl-3.0.html

from unittest import TestCase

from datacats.validate import valid_name, valid_deploy_name


class TestValidate(TestCase):
    def test_good_name(self):
        self.assertTrue(valid_name('copper'))

    def test_name_with_numbers(self):
        self.assertTrue(valid_name('seven42'))

    def test_name_with_leading_numbers(self):
        self.assertFalse(valid_name('42seven'))

    def test_name_too_short(self):
        self.assertFalse(valid_deploy_name('foo'))
