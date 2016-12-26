#!/usr/bin/env python3
# dvcz/test_store.py

import os
import unittest

from dvcz import DvczError
from dvcz.store import Store
from xlattice import QQQ
from xlattice.u import UDir


class TestStore(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def do_test_good(self, name, u_path, dir_struc, using_sha):
        store = Store(name, u_path, dir_struc, using_sha)
        self.assertEqual(store.name, name)
        self.assertEqual(store.u_path, u_path)
        self.assertEqual(store.dir_struc, dir_struc)
        self.assertEqual(store.using_sha, using_sha)

        # round-trip it
        ser = store.__str__()
        # DEBUG
        # print("SERIALIZATION: %s" % ser)
        # END
        store_b = Store.create_from_string(ser)
        self.assertEqual(store_b, store)

    def test_good_stores(self):
        for dir_struc in [UDir.DIR_FLAT, UDir.DIR16x16, UDir.DIR256x256]:
            for using_sha in [QQQ.USING_SHA1, QQQ.USING_SHA2, QQQ.USING_SHA3]:
                self.do_test_good('grinch', 'tmp/pqr', dir_struc, using_sha)

    def do_test_bad_name(self, name, u_path, dir_struc=''):
        try:
            store = Store(name, u_path, dir_struc, using_sha)
            self.fail("Store didn't detect bad name '%s'" % name)
        except:
            pass

    def test_bad_names(self):
        self.do_test_bad_name('', 'tmp/frog')
        self.do_test_bad_name('a-b', 'tmp/frog')
        self.do_test_bad_name('.b', 'tmp/frog')
        self.do_test_bad_name('a b', 'tmp/frog')

    def do_test_bad_path(self, name, u_path, dir_struc=''):
        try:
            store = Store(name, u_path, dir_struc, using_sha)
            self.fail("Store didn't detect bad u_path '%s'" % name)
        except:
            pass

    def test_bad_paths(self):
        self.do_test_bad_path('frog', '/frog')      # no permission to write

if __name__ == '__main__':
    unittest.main()
