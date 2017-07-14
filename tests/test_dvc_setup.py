#!/usr/bin/env python3
# dvcz/test_dvc_setup.py

""" Test the setUp function for dvcz testing. """

import os
import unittest

# from dvcz import DvczError
from rnglib import SimpleRNG, valid_file_name


class DvcTestSetup(object):
    """
    Create a directory structure under ./tmp/

    See https://jddixon.github.io/dvcz for an extended description
    of the subdirectory.
    """

    def __init__(self):

        self._rng = SimpleRNG()
        self._run_id = self.rng.next_file_name(8)
        self._run_dir = os.path.join('tmp', self._run_id)
        while os.path.exists(self._run_dir):
            self._run_id = self.rng.next_file_name(8)
            self._run_dir = os.path.join('tmp', self._run_id)
        os.makedirs(self._run_dir, mode=0o755)

        # under this add home/LOGIN/dvcz/committers/ and stores/
        self._login = os.environ['LOGNAME']
        dvc_dir = os.path.join(
            self._run_dir, os.path.join(
                'home', os.path.join(self._login, 'dvcz')))
        self._committers_dir = os.path.join(dvc_dir, 'committers')
        self._home_stores_dir = os.path.join(dvc_dir, 'stores')
        os.makedirs(self._committers_dir, mode=0o755)
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
        """ Return a simple random number generator. """
        return self._rng

    @property
    def run_id(self):
        """
        Return the quasi-random integer uniquely identifying this
        run directory.
        """
        return self._run_id

    @property
    def run_dir(self):
        """
        Return a path to this run directory, a path incorporating run_id."""
        return self._run_dir

    @property
    def login(self):
        """
        Return the host operating system login associated with this test run.
        """
        return self._login

    @property
    def committers_dir(self):
        """
        Return a path to the committers/ subdirectory containing
        serialized Committer objects.  In general one login may have many
        such Committer objects.
        """
        return self._committers_dir

    @property
    def home_stores_dir(self):
        """
        Return a path to the stores/ subdirectory containing serialized
        Store objects, one for each content-keyed store that a Committer
        might have access to.
        """
        return self._home_stores_dir

    @property
    def projects_dir(self):
        """
        Return a path to the projects/ subdirectory.  This will contain
        subdirectories by Committer name, and below each serialized
        Project objects .
        """
        return self._projects_dir

    @property
    def stores_dir(self):
        """
        Return a path to the stores/ subdirectory.
        """
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

        # DEBUG
        print('cfg.run_id = %s' % cfg.run_id)
        # END

        self.assertTrue(valid_file_name(cfg.run_id))
        self.assertTrue(os.path.exists(cfg.run_dir))
        self.assertEqual(cfg.run_dir, os.path.join('tmp', cfg.run_id))

        # weird problem with python: os.getlogin() usually returns '' but
        # sometimes returns eg 'jdd'
        try:
            ret = os.getlogin()
            print("os.getlogin() unexpectedly worked, returning %s" % ret)
        except FileNotFoundError:
            pass

        self.assertEqual(cfg.login, os.environ['LOGNAME'])

        # pure lazinessM
        self.assertEqual(cfg.committers_dir, cfg.run_dir + '/home/' +
                         cfg.login + '/dvcz/committers')
        self.assertTrue(os.path.exists(cfg.committers_dir))
        self.assertTrue(os.path.exists(cfg.home_stores_dir))

        self.assertTrue(os.path.exists(cfg.projects_dir))
        self.assertTrue(os.path.exists(cfg.stores_dir))


if __name__ == '__main__':
    unittest.main()
