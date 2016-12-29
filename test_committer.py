#!/usr/bin/env python3
# dvcz/test_committer.py

""" Exercise the Committer class and related functions. """

import unittest

from Crypto.PublicKey import RSA
from dvcz import DvczError
from dvcz.user import Committer


class TestCommitter(unittest.TestCase):
    """ Exercise the Committer class and related functions. """

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def do_test_good(self, handle, login, sk_priv, ck_priv, key_bits):
        """ Verify that a known-good set of parameters is accepted. """
        committer = Committer(handle, login, sk_priv, ck_priv, key_bits)
        self.assertEqual(committer.handle, handle)
        self.assertEqual(committer.login, login)
        self.assertEqual(committer.sk_priv.size(), committer.key_bits)
        self.assertEqual(committer.ck_priv.size(), committer.key_bits)

        # round-trip it
        ser = committer.__str__()
        # DEBUG
        #print("SERIALIZATION:\n%s" % ser)
        # END
        committer_b = Committer.create_from_string(ser)
        self.assertEqual(committer_b, committer)

    def test_good_committers(self):
        """ Test a range of valid parameter values. """

        #                  login, key_bits)
        self.do_test_good('froggy', 'grinch', None, None, 1024)
        self.do_test_good('wombat', 'charlie', None, None, 2048)

        sk_priv = RSA.generate(1024)
        ck_priv = RSA.generate(1024)
        self.do_test_good('gorp', 'fred', sk_priv, ck_priv, 1024)

    def do_test_bad_handle(self, handle, login, sk_priv, ck_priv, key_bits):
        """ Verify that a known-bad handle is rejected. """
        try:
            _ = Committer(handle, login, sk_priv, ck_priv, key_bits)
            self.fail("Committer didn't detect bad handle '%s'" % handle)
        except DvczError:
            pass

    def test_bad_handles(self):
        """ Confirm that a range of known-bad handles are rejected. """
        #                      handle, login, sk_priv, ck_priv, key_bits)
        self.do_test_bad_handle('', 'julie', None, None, 1024)
        self.do_test_bad_handle('a-b', 'julie', None, None, 1024)
        self.do_test_bad_handle('.b', 'julie', None, None, 1024)
        self.do_test_bad_handle('a b', 'julie', None, None, 1024)


if __name__ == '__main__':
    unittest.main()
