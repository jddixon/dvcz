#!/usr/bin/env python3
# dvcz/test_project.py

""" Test the Project abstraction and related functions. """

import unittest

from dvcz import DvczError
from dvcz.project import Project


class TestProject(unittest.TestCase):
    """ Test the Project abstraction and related functions. """

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def do_test_good(self, name, path, main_lang=''):
        """
        Verify that good parameter sets are accepted and handled correctly.
        """
        proj = Project(name, path, main_lang)
        self.assertEqual(proj.name, name)
        self.assertEqual(proj.proj_path, path)
        self.assertEqual(proj.main_lang, main_lang)

        # round-trip it
        ser = proj.__str__()
        proj_b = Project.create_from_string(ser)
        self.assertEqual(proj_b, proj)

    def test_good_projects(self):
        """ Test a range of acceptable parameter sets. """
        #                  name      path            main_lang
        self.do_test_good('bar', 'tmp/bunny', 'py')
        self.do_test_good('banana', 'tmp/frog', 'c')
        self.do_test_good('grinch', 'tmp/abc/def')
        self.do_test_good('grinch', 'tmp/pqr')

    def do_test_bad_name(self, name, path, main_lang=''):
        """ Verify that a known-bad name is rejected. """
        try:
            _ = Project(name, path, main_lang)
            self.fail("Project didn't detect bad name '%s'" % name)
        except DvczError:
            pass

    def test_bad_names(self):
        """ Test a range of inacceptable project names. """
        self.do_test_bad_name('', 'tmp/frog')
        self.do_test_bad_name('.b', 'tmp/frog')
        self.do_test_bad_name('a b', 'tmp/frog')        # FAILS
        self.do_test_bad_name('a-b', 'tmp/frog')        # FAILS

    def do_test_bad_path(self, name, path, main_lang=''):
        """ Verify that a known-bad path to a project is rejected. """
        try:
            _ = Project(name, path, main_lang)
            self.fail("Project didn't detect bad path '%s'" % name)
        except PermissionError:
            pass

    def test_bad_paths(self):
        """ Test a range of invalid project paths. """
        self.do_test_bad_path('frog', '/frog')      # no permission to write

if __name__ == '__main__':
    unittest.main()
