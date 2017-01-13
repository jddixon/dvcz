#!/usr/bin/env python3
# dvcz/test_store.py

""" Test the Store object and related functions. """

import unittest

from dvcz import DvczError
from dvcz.store import Store
from xlattice import HashTypes
from xlattice.u import UDir


class TestStore(unittest.TestCase):
    """ Test the Store object and related functions. """

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def do_test_good(self, name, u_path, dir_struc, hashtype):
        """ Verify that parameters that should succeed do so. """
        store = Store(name, u_path, dir_struc, hashtype)
        self.assertEqual(store.name, name)
        self.assertEqual(store.u_path, u_path)
        self.assertEqual(store.dir_struc, dir_struc)
        self.assertEqual(store.hashtype, hashtype)

        # round-trip it
        ser = store.__str__()
        # DEBUG
        # print("SERIALIZATION: %s" % ser)
        # END
        store_b = Store.create_from_string(ser)
        self.assertEqual(store_b, store)

    def test_good_stores(self):
        """ Test various combinations of parameters that should succeed. """
        for dir_struc in [UDir.DIR_FLAT, UDir.DIR16x16, UDir.DIR256x256]:
            for hashtype in HashTypes:
                self.do_test_good('grinch', 'tmp/pqr', dir_struc, hashtype)

    def do_test_bad_name(self, name, u_path,
                         dir_struc=UDir.DIR_FLAT, hashtype=HashTypes.SHA2):
        """ Verify that names that should be rejected are. """
        try:
            _ = Store(name, u_path, dir_struc, hashtype)
            self.fail("Store didn't detect bad name '%s'" % name)
        except DvczError:
            pass

    def test_bad_names(self):
        """ Test some instances of invalid names. """
        self.do_test_bad_name('', 'tmp/frog')
        self.do_test_bad_name(' ', 'tmp/frog')      # space
        self.do_test_bad_name('.', 'tmp/frog')      # dot
        self.do_test_bad_name('$', 'tmp/frog')      # dollar
        self.do_test_bad_name('a$b', 'tmp/frog')
        self.do_test_bad_name('.b', 'tmp/frog')
        self.do_test_bad_name('a b', 'tmp/frog')    # space
        self.do_test_bad_name('a\tb', 'tmp/frog')   # tab

    def do_test_bad_path(self, name, u_path,
                         dir_struc='', hashtype=HashTypes.SHA2):
        """ Verify that a bad path to a store is rejected. """
        try:
            _ = Store(name, u_path, dir_struc, hashtype)
            self.fail("Store didn't detect bad u_path '%s'" % name)
        except PermissionError:
            pass

    def test_bad_paths(self):
        """ Verify that various inacceptable store paths are rejected. """
        self.do_test_bad_path('frog', '/frog')      # no permission to write

if __name__ == '__main__':
    unittest.main()
