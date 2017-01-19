#!/usr/bin/env python3
# dvcz/test_user.py

""" Test the functioning of various user-related classes. """

import unittest

from Crypto.PublicKey import RSA
from dvcz.user import User
from dvcz import DvczError


class TestUser(unittest.TestCase):
    """ Test the functioning of various user-related classes. """

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def do_test_good(self, login, sk_priv, ck_priv, key_bits):
        """
        Verify that a known-good set of parameters is accepted
        and the resultant User object works as expected.
        """
        user = User(login, sk_priv, ck_priv, key_bits)
        self.assertEqual(user.login, login)
        self.assertEqual(user.sk_priv.size() + 1, user.key_bits)
        self.assertEqual(user.ck_priv.size() + 1, user.key_bits)

        # round-trip it
        ser = user.__str__()
        # DEBUG
        # print("SERIALIZATION:\n%s" % ser)
        # END
        user_b = User.create_from_string(ser)
        self.assertEqual(user_b, user)

    def test_good_users(self):
        """
        Feed various cominations of known-good parameters to the
        do_test_good() function.
        """

        #                  login, key_bits)
        self.do_test_good('grinch', None, None, 1024)
        self.do_test_good('charlie', None, None, 2048)

        sk_priv = RSA.generate(1024)
        ck_priv = RSA.generate(1024)
        self.do_test_good('fred', sk_priv, ck_priv, 1024)

    def do_test_bad_login(self, login, sk_priv, ck_priv, key_bits):
        """Verify that bad login strings are rejected. """
        try:
            _ = User(login, sk_priv, ck_priv, key_bits)
            self.fail("User didn't detect bad login '%s'" % login)
        except DvczError:
            pass

    def test_bad_logins(self):
        """ Feed known-bad logins to do_test_bad_login(). """

        #                      login, sk_priv, ck_priv, key_bits)
        self.do_test_bad_login('', None, None, 1024)
        self.do_test_bad_login('a-b', None, None, 1024)
        self.do_test_bad_login('.b', None, None, 1024)
        self.do_test_bad_login('a b', None, None, 1024)


if __name__ == '__main__':
    unittest.main()
