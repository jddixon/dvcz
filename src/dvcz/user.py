# dvcz/user.py
"""
User, PubUser, Committer, and PubCommitter objects and related classes
and functions.
"""

import os
# import re
import sys
import time
import hashlib

from buildlist import(check_dirs_in_path, generate_rsa_key,
                      read_rsa_key, rm_f_dir_contents)
from dvcz import DvczError
from dvcz.project import Project
from xlattice import HashTypes
from xlattice.u import UDir

from Crypto.PublicKey import RSA

if sys.version_info < (3, 6):
    # pylint: disable=unused-import
    import sha3
    assert sha3     # suppress warning

# == adduser ========================================================


def make_committer_id(pubkey, hashtype=HashTypes.SHA2):
    """
    Create a unique committer ID derived from the user's RSA public key
    using this SHA type.

    This implementation adds the current time to the hash.

    Returns a 40- or 64-character hex value.
    """

    if hashtype == HashTypes.SHA1:
        sha = hashlib.sha1()
    elif hashtype == HashTypes.SHA2:
        sha = hashlib.sha256()
    elif hashtype == HashTypes.SHA3:
        sha = hashlib.sha3_256()
    elif hashtype == HashTypes.BLAKE2B:
        sha = hashlib.blake2b(digest_size=32)
    else:
        raise NotImplementedError
    sha.update(pubkey.exportKey())  # PEM format
    sha.update(str(time.time()).encode('utf-8'))
    return sha.hexdigest()


def do_add_user(options):
    """
    Carry out the configuration.
    """

    if options.testing:
        if os.path.exists('tmp'):
            rm_f_dir_contents('tmp')                # empties the directory
            os.makedirs(options.home, exist_ok=True, mode=0o755)

    # user_dvcz_path ------------------------------------------------
    # this is $HOME/.dvcz unless testing

    if os.path.exists(options.user_dvcz_path) and options.force:
        rm_f_dir_contents(options.user_dvcz_path)  # empties the directory

    if not os.path.exists(options.user_dvcz_path):
        os.makedirs(options.user_dvcz_path, exist_ok=True, mode=0o755)

    # write RSA private key to $DVCZ_DIR/node/sk_priv.pem
    if not os.path.exists(options.key_path):
        check_dirs_in_path(options.key_path)
        if options.testing:
            generate_rsa_key(options.key_path, 1024)
        else:
            generate_rsa_key(options.key_path, options.key_bits)

    # Read the RSA private key from disk ------------------
    privkey = read_rsa_key(options.key_path)
    pubkey = privkey.publickey()

    # Generate and write a unique committer ID to $DVCZ_DIR/id.
    path_to_id = os.path.join(options.user_dvcz_path, 'id')
    if os.path.exists(path_to_id):
        with open(path_to_id, 'r') as file:
            committer_id = file.read()
    else:
        committer_id = make_committer_id(pubkey, options.hashtype)
        with open(path_to_id, 'w+') as file:
            file.write(committer_id)
    # DEBUG
    print("committer ID: %s" % committer_id)
    # END

    # proj_dvcz_path ------------------------------------------------
    # if testing, remove it; otherwise just make sure that it exists
    if options.testing and os.path.exists(options.proj_dvcz_path):
        # DEBUG
        print("deleting %s" % options.proj_dvcz_path)
        # END
        rm_f_dir_contents(options.proj_dvcz_path)      # empties directory

    os.makedirs(options.proj_dvcz_path, 0o755, exist_ok=True)

    # u_path --------------------------------------------------------
    hashtype = options.hashtype
    if options.testing and options.u_path and os.path.exists(options.u_path):
        rm_f_dir_contents(options.u_path)

    if options.u_path:
        # if necessary create $U_DIR with requisite DIR_STRUC and hashtype
        # u_dir =
        UDir.discover(options.u_path, hashtype=hashtype)
        # can get SHA type from u_dir

        # create $U_DIR/in/$ID/ which is DIR_FLAT with the correct hashtype
        my_in_path = os.path.join(options.u_path, 'in', committer_id)
        # my_in_dir =
        UDir.discover(my_in_path, hashtype=hashtype)

# CLASSES ===========================================================


class _User(object):
    """
    Abstract version of the User class.

    Includes secret RSA keys.
    """

    def __init__(self, login=os.environ['LOGNAME'],
                 sk_priv=None, ck_priv=None, key_bits=2048):

        # The login must always be a valid name, one including no
        # delimiters or other odd characters.  At least for the mement
        # we use the same rules for user names as Project names.

        if not Project.valid_proj_name(login):
            raise DvczError("not a valid login: '%s'" % login)
        self._login = login

        # Caller can supply keys with different sizes.
        if sk_priv:
            if sk_priv.size() + 1 != key_bits:
                sk_priv = None
            elif ck_priv.size() + 1 != key_bits:
                ck_priv = None
        if sk_priv is None:
            sk_priv = RSA.generate(key_bits)
            ck_priv = None
        if ck_priv is None:
            ck_priv = RSA.generate(key_bits)
        # To write use
        #   with open(path, 'wb+') as file:
        #       file.write(sk_priv.exportKey('PEM'))
        # To read use
        #   with open(path, 'rb') as file: sk_priv = RSA.importKey(file.read())
        self._sk_priv = sk_priv
        self._ck_priv = ck_priv
        self._key_bits = sk_priv.size() + 1

    @property
    def login(self):
        """ Return the user's login. """
        return self._login

    @property
    def sk_priv(self):
        """ Return the RSA key used for making digital signatures. """
        return self._sk_priv

    @property
    def ck_priv(self):
        """ Return the RSA key used for encryption. """
        return self._ck_priv

    @property
    def key_bits(self):
        """
        Return the size of the RSA key.

        Note that PyCrypt's RSA size is 1 less than key_bits.
        """
        return self._key_bits


class User(_User):
    """
    Descriptor for DVCZ users.

    Includes private keys and serialization/deserialization methods.
    """
    START_LINE = '-----START DVCZ USER-----'
    END_LINE = '-----END DVCZ USER-----'

    def __init__(self, login=os.environ['LOGNAME'],
                 sk_priv=None, ck_priv=None, key_bits=2048):
        # pylint: disable=useless-super-delegation
        super().__init__(login, sk_priv, ck_priv, key_bits)

    def __eq__(self, other):
        if not isinstance(other, User):
            return False
        return self._login == other.login and \
            self._sk_priv == other.sk_priv and \
            self._ck_priv == other.ck_priv

    def __str__(self):
        # possible ValueErrors here
        sk_exp_ = self.sk_priv.exportKey('PEM')
        # pylint is confused here
        # pylint: disable=no-member
        sk_exp = sk_exp_.decode('utf-8')

        ck_exp_ = self.ck_priv.exportKey('PEM')
        # pylint is confused here
        # pylint: disable=no-member
        ck_exp = ck_exp_.decode('utf-8')

        return """{0}
{1}
{2}
{3}
{4}
""".format(User.START_LINE,
           self.login,
           sk_exp,
           ck_exp,
           User.END_LINE)

    @classmethod
    def create_from_file(cls, path):
        """ Parse the serialized User object. """
        with open(path, 'r') as file:
            text = file.read()
        return cls.create_from_string(text)

    @classmethod
    def create_from_string(cls, string):
        """ Parse the serialized User object. """

        if not string:
            raise DvczError('empty string')

        strings = string.split('\n')
        if strings[-1] == '\n':
            strings = strings[:-1]
        return cls.create_from_string_array(strings)

    @classmethod
    def create_from_string_array(cls, strings):
        """ Parse the serialized User object from a list of strings. """

        if not strings:
            raise DvczError('empty string array')

        def collect_priv(lines, offset, line_count):
            """
            Interpret a list of lines of text as a PEM-formatted
            RSA private key.
            """

            # find the end of the PEM-formatted RSA private key
            found = False
            ndx = -1
            for ndx in range(offset, line_count):
                if lines[ndx] == '-----END RSA PRIVATE KEY-----':
                    found = True
                    break
            if not found:
                raise DvczError("can't find end of PEM-formatted RSA key")
            text = '\n'.join(lines[offset:ndx + 1])
            priv = RSA.importKey(text)
            return (ndx + 1, priv)

        line_count = len(strings)
        if line_count < 5:
            raise DvczError(
                "too few parts (%d) in User string array" % line_count)
        if strings[0] != cls.START_LINE:
            raise DvczError("found '%s' instead of '%s'" % (
                strings[0], cls.START_LINE))
        login = strings[1]
        offset = 2
        offset, sk_priv = collect_priv(strings, offset, line_count)
        offset, ck_priv = collect_priv(strings, offset, line_count)

        if strings[offset] != cls.END_LINE:
            raise DvczError("found '%s' instead of '%s'" % (
                strings[offset], cls.END_LINE))

        # XXX Ignoring possiblity of differences key sizes
        key_bits = sk_priv.size() + 1   # XXX TILT: PyCrypto returns eg 1023
        # DEBUG
        # print("create_from_string_array: found sk_priv size is %d" %
        #        key_bits)
        # END

        return User(login, sk_priv, ck_priv, key_bits)


class _PubUser(object):
    """
    This version of the user descriptor includes the public part of  RSA keys.
    """

    def __init__(self, login, sk_, ck_):

        # The login must always be a valid name, one including no
        # delimiters or other odd characters.

        if not Project.valid_proj_name(login):
            raise DvczError("not a valid login: '%s'" % login)
        self._login = login

        # To write use
        #   with open(path, 'wb+') as file: file.write(sk.exportKey('PEM'))
        # To read use
        #   with open(path, 'rb') as file: sk = RSA.importKey(file.read())
        self._sk = sk_
        self._ck = ck_

    @property
    def login(self):
        """ Return the User's login, a valid file name. """
        return self._login

    @property
    def sk_(self):
        """ Return the public part of the RSA key used for digital sigs. """
        return self._sk

    @property
    def ck_(self):
        """ Return the public part of the RSA key used for encryption. """
        return self._ck

    def __str__(self):

        return "NOT IMPLEMENTED: User.__str__()"


class PubUser(_PubUser):
    """ The public view of a User, one which conains no secret keys. """

    @classmethod
    def create_from_user(cls, user):
        """ Replaces each private RSA key with its public part. """
        return PubUser(user.login,
                       user.sk_priv.publickey(),
                       user.ck_priv.publickey())

    def create_from_file(self, path):
        """ Parse the serialized PubUser object. """

        raise NotImplementedError()


class Committer(User):
    """
    Specifies a Committer, a User which can commit changes to a
    content-keyed store.

    In addition to the attributes of a User, a Committer has a
    handle, a unique valid file name unique with the cluster of
    cooperating servers housing content-keyed data stores.
    """

    START_LINE = '-----START DVCZ COMMITTER-----'
    END_LINE = '-----END DVCZ COMMITTER-----'

    def __init__(self, handle, login=os.environ['LOGNAME'],
                 sk_priv=None, ck_priv=None, key_bits=2048):
        if not Project.valid_proj_name(handle):
            raise DvczError("'%s' is not a valid handle" % handle)
        super().__init__(login, sk_priv, ck_priv, key_bits)
        self._handle = handle

    @property
    def handle(self):
        """ Return the committer's handle, a valid name. """
        return self._handle

    def __eq__(self, other):
        if not isinstance(other, Committer):
            return False
        return self._handle == other.handle and \
            self._login == other.login and \
            self._sk_priv == other.sk_priv and \
            self._ck_priv == other.ck_priv

    def __str__(self):
        return """{0}
{1}
{2}{3}
""".format(Committer.START_LINE,
           self.handle,
           super().__str__(),
           Committer.END_LINE)

    @classmethod
    def create_from_file(cls, path):
        """ Parse the serialized Committer object. """
        with open(path, 'r') as file:
            text = file.read()
        return cls.create_from_string(text)

    @classmethod
    def create_from_string(cls, string):
        """ Parse the serialized Committer object. """

        if not string:
            raise DvczError('empty string')

        # DEBUG
        # print("Committer.create_from_string: input is:\n%s" % string)
        # END
        strings = string.split('\n')
        while strings[-1] == '':
            strings = strings[:-1]
        return cls.create_from_string_array(strings)

    @classmethod
    def create_from_string_array(cls, strings):
        """ Parse the serialized Committer object from a list of strings. """

        if not strings:
            raise DvczError("empty string array")

        line_count = len(strings)
        if line_count < 5:
            raise DvczError(
                "too few lines (%d) in Committer string array" % line_count)

        if strings[0] != cls.START_LINE:
            raise DvczError("found '%s' instead of '%s'" % (
                strings[0], cls.START_LINE))
        handle = strings[1]

        if strings[-1] != cls.END_LINE:
            raise DvczError("found '%s' instead of '%s'" % (
                strings[-1], cls.END_LINE))

        user = User.create_from_string_array(strings[2:-1])

        return Committer(handle,
                         user.login,
                         user.sk_priv,
                         user.ck_priv,
                         user.key_bits)


class PubCommitter(_PubUser):
    """
    The public view of a Committer, one which contains no secret keys.
    """

    def __init__(self, handle, login=os.environ['LOGNAME'],
                 sk_=None, ck_=None):
        if not Project.valid_proj_name(handle):
            raise DvczError("'%s' is not a valid handle" % handle)
        super().__init__(login, sk_, ck_)
        self._handle = handle
