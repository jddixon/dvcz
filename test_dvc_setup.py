#!/usr/bin/env python3
# dvcz/test_dvc_setup.py

""" Test the setUp function for dvcz testing. """

from argparse import Namespace
import os
import unittest

from dvcz import get_proj_info, DvczError
from rnglib import SimpleRNG, valid_file_name
from xlattice.u import UDir


class DvcTestSetup(object):
    """
    Create a directory structure under ./tmp/

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

    def __init__(self):

        self._rng = SimpleRNG()
        self._run_id = self.rng.next_file_name(8)
        self._run_dir = os.path.join('tmp', self._run_id)
        while os.path.exists(self._run_dir):
            self._run_id = self.rng.next_file_name(8)
            self._run_dir = os.path.join('tmp', self._run_id)
        os.makedirs(self._run_dir, mode=0o755)

        # under this add home/LOGIN/dvcz/home_committers/ and stores/
        self._login = os.environ['LOGNAME']
        dvc_dir = os.path.join(
            self._run_dir, os.path.join(
                'home', os.path.join(self._login, 'dvcz')))
        self._home_committers_dir = os.path.join(dvc_dir, 'home_committers')
        self._home_stores_dir = os.path.join(dvc_dir, 'stores')
        os.makedirs(self._home_committers_dir, mode=0o755)
        os.makedirs(self._home_stores_dir, mode=0o755)

        # on the same level as home
        self._projects_dir = os.path.join(self._run_dir, 'projects')
        os.makedirs(self._projects_dir, mode=0o755)

        # on the same level as home
        self._stores_dir = os.path.join(self._run_dir, 'stores')
        os.makedirs(self._stores_dir, mode=0o755)

        # maps
        self._name2project = None
        self._name2store = None

        # lists
        self._projects = []     # a list of Project objects
        self._stores = []       # a list of UStore objects

    @property
    def rng(self):
        return self._rng

    @property
    def run_id(self):
        return self._run_id

    @property
    def run_dir(self):
        return self._run_dir

    @property
    def login(self):
        return self._login

    @property
    def home_committers_dir(self):
        return self._home_committers_dir

    @property
    def home_stores_dir(self):
        return self._home_stores_dir

    @property
    def projects_dir(self):
        return self._projects_dir

    @property
    def stores_dir(self):
        return self._stores_dir


class TestDvcSetup(unittest.TestCase):
    """ Test the setUp function for dvcz testing. """

    def tearDown(self):
        pass

    def test_setup(self):
        """
        We verify that setUp() has created the expected directory
        structure.
        """

        cfg = DvcTestSetup()

        self.assertTrue(valid_file_name(cfg.run_id))
        self.assertTrue(os.path.exists(cfg.run_dir))
        self.assertEqual(cfg.run_dir, os.path.join('tmp', cfg.run_id))

        # weird problem with python: os.getlogin() usually returns '' but
        # sometimes returns eg 'jdd'
        try:
            ret = os.getlogin()
            print("os.getlogin() unexpecedly worked, returning %s" % ret)
        except FileNotFoundError:
            pass

        self.assertEqual(cfg.login, os.environ['LOGNAME'])

        # pure lazinessM
        self.assertEqual(cfg.home_committers_dir, cfg.run_dir + '/home/' +
                         cfg.login + '/dvcz/home_committers')
        self.assertTrue(os.path.exists(cfg.home_committers_dir))
        self.assertTrue(os.path.exists(cfg.home_stores_dir))

        self.assertTrue(os.path.exists(cfg.projects_dir))
        self.assertTrue(os.path.exists(cfg.stores_dir))

if __name__ == '__main__':
    unittest.main()
