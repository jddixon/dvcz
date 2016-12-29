#!/usr/bin/env python3
# dvcz/test_get_proj_info.py

""" Verify that get_proj_info() works as expected. """

from argparse import Namespace
import os
import unittest

from dvcz import DvczError
from dvcz.project import get_proj_info


class TestGetProjInfo(unittest.TestCase):
    """ Verify that get_proj_info() works as expected. """

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_namespace(self):
        """ Verify Namespace works as expected. """

        # empty Namespace
        namespace0 = Namespace()
        namespace0.foo_ = 'bar'
        self.assertEqual(namespace0.foo_, 'bar')

        # simple Namespace
        kwargs = {'abc': 52, 'froggy': 47, 'jungle': 'green'}
        namespace = Namespace(**kwargs)

        # pylint can't handle namespace attributes
        # pylint: disable=no-member
        self.assertEqual(namespace.abc, 52)
        self.assertEqual(namespace.froggy, 47)
        self.assertEqual(namespace.jungle, 'green')

    def test_simple_case(self):
        """
        Verify that if you search for a .dvcz subdirectory and
        there is one in the current directory, it will be found.
        """
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
        # pylint: disable=no-member
        self.assertEqual(args.proj_name, 'dvcz')
        self.assertEqual(args.proj_path, expected_path)
        self.assertEqual(args.proj_parent, expected_parent)

    def test_search_up(self):
        """
        Verify that if it is necessary to search upward to find
        a .dvcz subdirectory, it works.
        """

        basedir = os.getcwd()
        newdir = os.path.join(basedir, 'tmp')
        os.makedirs(newdir, exist_ok=True, mode=0o755)
        os.chdir(newdir)

        args = Namespace()
        try:
            get_proj_info(args)
            dirnow = os.getcwd()
            # pylint: disable=no-member
            self.assertEqual(dirnow, basedir)
            self.assertEqual(args.proj_name, 'dvcz')
        finally:
            os.chdir(basedir)

        expected_parent = os.path.join(os.environ['DEV_BASE'], 'py')
        expected_path = os.path.join(expected_parent, 'dvcz')

        # pylint: disable=no-member
        self.assertEqual(args.proj_name, 'dvcz')
        self.assertEqual(args.proj_path, expected_path)
        self.assertEqual(args.proj_parent, expected_parent)

    def test_bad_paths(self):
        """ Verify that invalid paths raise. """
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
