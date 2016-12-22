#!/usr/bin/env python3
# dvcz/test_dvc_setup.py

""" Test the setUp function for dvcz testing. """

from argparse import Namespace
import os
import unittest

from dvcz import get_proj_info, DvczError
from rnglib import SimpleRNG, valid_file_name


class TestDvcSetup(unittest.TestCase):
    """ Test the setUp function for dvcz testing. """

    login, run_id, run_dir = '', '', ''
    home_committers_dir, home_stores_dir = '', ''
    rng = SimpleRNG()

    def setUp(self):
        """
        Create a directory structure under tmp/

        This looks like
            tmp/
              RUN_ID/
                home/
                  LOGIN/
                    dvcz/
                      committers/
                        HANDLE      # serialized Committer object
                        ...         #   containing secret keys, etc
                      stores/
                        STORE_NAME  # serialized UStore object
                        ...
                projects/
                  PROJECT_NAME/
                    dvcz/
                  ...
                stores/
                  STORE_NAME/
                    SHA_SIG     # hex value of SHAxNONE, where x is 1, 2, or 3
                    in/
                      USER_ID
                        SHA_SIG
                        in/
                        tmp/
                        CONTENT_KEY
                        ...

        That is, each run ID has a distinct subdirectory under tmp.
        In each such subdirectory there is a dummy home/login directory,
        and under that a dvcz directory that corresponds to $HOME/.dvcz.
        The keys in this dummy dvcz directory are used for digital
        signatures on BuildLists created during test runs

        At the same level as the home/ directory there is a projects/
        directory and under that dummy project directories for the test
        runs.  At the time of writing these are used only for collecting
        lastBuildList files and appending build info to the builds file.

        And at the same level there are dummy content-keyed stores used
        in the test runs.  Each such store has a unique name.  Each has
        an in/ directory and within that
        """

        # tmp/self.run_id

        self.run_id = self.rng.next_file_name(8)
        self.run_dir = os.path.join('tmp', self.run_id)
        while os.path.exists(self.run_dir):
            self.run_id = self.rng.next_file_name(8)
            self.run_dir = os.path.join('tmp', self.run_id)
        os.makedirs(self.run_dir, mode=0o755)

        # under this add home/LOGIN/dvcz/home_committers/ and stores/
        self.login = os.environ['LOGNAME']
        dvc_dir = os.path.join(
            self.run_dir, os.path.join(
                'home', os.path.join(self.login, 'dvcz')))
        self.home_committers_dir = os.path.join(dvc_dir, 'home_committers')
        self.home_stores_dir = os.path.join(dvc_dir, 'stores')
        os.makedirs(self.home_committers_dir, mode=0o755)
        os.makedirs(self.home_stores_dir, mode=0o755)

    def tearDown(self):
        pass

    def test_setup(self):
        """
        We verify that setUp() has created the expected directory
        structure.
        """
        self.assertTrue(valid_file_name(self.run_id))
        self.assertTrue(os.path.exists(self.run_dir))
        self.assertEqual(self.run_dir, os.path.join('tmp', self.run_id))

        # weird problem with python
        try:
            ret = os.getlogin()
            print("os.getlogin() unexpecedly worked, returning %s" % ret)
        except FileNotFoundError:
            pass

        self.assertEqual(self.login, os.environ['LOGNAME'])

        # pure lazinessM
        self.assertEqual(self.home_committers_dir, self.run_dir + '/home/' +
                         self.login + '/dvcz/home_committers')
        self.assertTrue(os.path.exists(self.home_committers_dir))
        self.assertTrue(os.path.exists(self.home_stores_dir))

if __name__ == '__main__':
    unittest.main()
