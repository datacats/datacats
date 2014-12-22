from unittest import TestCase

from datacats.validate import valid_name

class TestValidate(TestCase):
    def test_good_name(self):
        self.assertTrue(valid_name('copper'))

    def test_name_with_numbers(self):
        self.assertTrue(valid_name('seven42'))

    def test_name_with_leading_numbers(self):
        self.assertFalse(valid_name('42seven'))

    def test_name_too_short(self):
        self.assertFalse(valid_name('foo'))
