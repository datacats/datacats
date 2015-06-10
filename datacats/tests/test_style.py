import unittest
import pep8
from pylint import epylint as lint


IGNORE_PEP8 = ('E131', 'E123', 'W503', 'E128', 'E125', 'E124', 'E121')


class TestStyle(unittest.TestCase):
    def test_pep8_conformance(self):
        """
        Tests pep8 conformence.
        """
        pep8style = pep8.StyleGuide(quiet=False, ignore=IGNORE_PEP8, max_line_length=100)
        result = pep8style.check_files(['datacats'])
        self.assertEqual(result.total_errors, 0, 'Found code style errors.')

    def test_pylint(self):
        (stdout, _) = lint.py_run('datacats', return_std=True)
        stdout_str = stdout.read().strip()
        self.failIf(stdout_str, stdout_str)
