#!/usr/bin/env python3

# buildlist/test_get_project_info.py

from argparse import Namespace
import os
import unittest

from dvcz import dvc_get_project_info


class TestGetProjectInfo(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_namespace(self):
        """ Verify Namespace works as expected. """

        # empty Namespace
        ns0 = Namespace()
        ns0.foo_ = 'bar'
        self.assertEqual(ns0.foo_, 'bar')

        # simple Namespace
        kwargs = {'abc': 52, 'froggy': 47, 'jungle': 'green'}
        ns = Namespace(**kwargs)
        self.assertEqual(ns.abc, 52)
        self.assertEqual(ns.froggy, 47)
        self.assertEqual(ns.jungle, 'green')

    def test_simple_case(self):
        curdir = os.getcwd()
        # assume that this gets run in $DEV_BASE/py/dvcz
        expected_path = os.path.join(os.environ['DEV_BASE'],
                                     os.path.join('py', 'dvcz'))
        self.assertEqual(curdir, expected_path)

        args = Namespace()
        dvc_get_project_info(args)
        self.assertEqual(args.project, 'dvcz')
        self.assertEqual(args.proj_path, expected_path)

    def test_search_up(self):
        basedir = os.getcwd()
        newdir = os.path.join(basedir, 'tmp')
        os.makedirs(newdir, exist_ok=True, mode=0o755)
        os.chdir(newdir)

        args = Namespace()
        dvc_get_project_info(args)
        dirnow = os.getcwd()
        self.assertEqual(dirnow, basedir)
        self.assertEqual(args.project, 'dvcz')

        # put me in setUp() !
        expected_path = os.path.join(os.environ['DEV_BASE'],
                                     os.path.join('py', 'dvcz'))
        self.assertEqual(args.proj_path, expected_path)


if __name__ == '__main__':
    unittest.main()
