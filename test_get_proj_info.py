#!/usr/bin/env python3

# dvcz/test_get_proj_info.py

from argparse import Namespace
import os
import unittest

from dvcz import get_proj_info, DvczError


class TestGetProjInfo(unittest.TestCase):

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
        basedir = os.getcwd()
        # assume that this gets run in $DEV_BASE/py/dvcz
        expected_parent = os.path.join(os.environ['DEV_BASE'], 'py')
        expected_path = os.path.join(expected_parent, 'dvcz')
        self.assertEqual(basedir, expected_path)

        args = Namespace()
        try:
            get_proj_info(args)
        finally:
            os.chdir(basedir)
        self.assertEqual(args.proj_name, 'dvcz')
        self.assertEqual(args.proj_path, expected_path)
        self.assertEqual(args.proj_parent, expected_parent)

    def test_search_up(self):
        basedir = os.getcwd()
        newdir = os.path.join(basedir, 'tmp')
        os.makedirs(newdir, exist_ok=True, mode=0o755)
        os.chdir(newdir)

        args = Namespace()
        try:
            get_proj_info(args)
            dirnow = os.getcwd()
            self.assertEqual(dirnow, basedir)
            self.assertEqual(args.proj_name, 'dvcz')
        finally:
            os.chdir(basedir)

        expected_parent = os.path.join(os.environ['DEV_BASE'], 'py')
        expected_path = os.path.join(expected_parent, 'dvcz')

        self.assertEqual(args.proj_name, 'dvcz')
        self.assertEqual(args.proj_path, expected_path)
        self.assertEqual(args.proj_parent, expected_parent)

    def test_bad_paths(self):
        basedir = os.getcwd()
        args = Namespace()
        args.proj_path = '/foo/foo/foo'         # does not exist
        try:
            get_proj_info(args)
            self.fail("didn't get FileNotFound on %s" % args.proj_path)
        except DvczError:
            pass
        finally:
            os.chdir(basedir)

        args = Namespace()
        args.proj_path = '/var/app/sharedev'    # exists, but no .dvcz
        try:
            get_proj_info(args)
            self.fail("didn't get FileNotFound on %s" % args.proj_path)
        except DvczError:
            pass
        finally:
            os.chdir(basedir)

if __name__ == '__main__':
    unittest.main()
