#!/usr/bin/env python3

# dvcz/test_project.py

import os
import unittest

from dvcz import DvczError
from dvcz.project import Project


class TestProject(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def do_test_good(self, name, path, main_lang=''):
        proj = Project(name, path, main_lang)
        self.assertEqual(proj.name, name)
        self.assertEqual(proj.proj_path, path)
        self.assertEqual(proj.main_lang, main_lang)

        # round-trip it
        ser = proj.__str__()
        proj_b = Project.create_from_string(ser)
        self.assertEqual(proj_b, proj)

    def test_good_projects(self):
        #                  name      path            main_lang
        self.do_test_good('grinch', 'tmp/abc/def')
        self.do_test_good('grinch', 'tmp/pqr')

        self.do_test_good('bar', 'tmp/bunny', 'py')
        self.do_test_good('banana', 'tmp/frog', 'c')

    def do_test_bad_name(self, name, path, main_lang=''):
        try:
            proj = Project(name, path, main_lang)
            self.fail("Project didn't detect bad name '%s'" % name)
        except:
            pass

    def test_bad_names(self):
        self.do_test_bad_name('', 'tmp/frog')
        self.do_test_bad_name('a-b', 'tmp/frog')
        self.do_test_bad_name('.b', 'tmp/frog')
        self.do_test_bad_name('a b', 'tmp/frog')

    def do_test_bad_path(self, name, path, main_lang=''):
        try:
            proj = Project(name, path, main_lang)
            self.fail("Project didn't detect bad path '%s'" % name)
        except:
            pass

    def test_bad_paths(self):
        self.do_test_bad_path('frog', '/frog')      # no permission to write

if __name__ == '__main__':
    unittest.main()
