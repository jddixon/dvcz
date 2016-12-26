# dvcz/user.py

import os
# import re
import sys
import time
import hashlib

from buildlist import(check_dirs_in_path, generate_rsa_key,
                      read_rsa_key, rm_f_dir_contents)
from rnglib import valid_file_name
from xlattice import QQQ
from xlattice.u import UDir

from Crypto.PublicKey import RSA

if sys.version_info < (3, 6):
    # pylint: disable=unused-import
    import sha3

# == adduser ========================================================


def make_committer_id(pubkey, using_sha):
    """
    Create a unique committer ID derived from the user's RSA public key
    using this SHA type.

    This implementation adds the current time to the hash.

    Returns a 40- or 64-character hex value.
    """

    # pylint: disable=redefined-variable-type
    if using_sha == QQQ.USING_SHA1:
        sha = hashlib.sha1()
    elif using_sha == QQQ.USING_SHA2:
        sha = hashlib.sha256()
    elif using_sha == QQQ.USING_SHA3:
        sha = hashlib.sha3_256()
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

    if os.path.exists(options.user_dvcz_path):
        if options.force:
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
        committer_id = make_committer_id(pubkey, options.using_sha)
        with open(path_to_id, 'w+') as file:
            file.write(committer_id)
    # DEBUG
    print("committer ID: %s" % committer_id)
    # END

    # proj_dvcz_path ------------------------------------------------
    # if testing, remove it; otherwise just make sure that it exists
    if options.testing:
        if os.path.exists(options.proj_dvcz_path):
            # DEBUG
            print("deleting %s" % options.proj_dvcz_path)
            # END
            rm_f_dir_contents(options.proj_dvcz_path)      # empties directory

    os.makedirs(options.proj_dvcz_path, 0o755, exist_ok=True)

    # u_path --------------------------------------------------------
    using_sha = options.using_sha
    if options.testing and options.u_path:
        if os.path.exists(options.u_path):
            rm_f_dir_contents(options.u_path)

    if options.u_path:
        # if necessary create $U_DIR with requisite DIR_STRUC and using_sha
        # u_dir =
        UDir.discover(options.u_path, using_sha=using_sha)
        # can get SHA type from u_dir

        # create $U_DIR/in/$ID/ which is DIR_FLAT with the correct using_sha
        my_in_path = os.path.join(options.u_path,
                                  os.path.join('in', committer_id))
        # my_in_dir =
        UDir.discover(my_in_path, using_sha=using_sha)

# CLASSES ===========================================================


class _User(object):
    """
    This version of the user descriptor includes secret RSA keys.
    """

    def __init__(self, login=os.environ['LOGNAME'],
                 sk_priv=None, ck_priv=None, key_bits=2048):

        # The login must always be a valid name, one including no
        # delimiters or other odd characters.

        if not valid_name(login):
            raise AtttributeError("not a valid login: '%s'" % login)

        # XXX: caller can supply keys with different sizes -- and
        # differing sizes.
        self._key_bits = key_bits
        if sk_priv is None:
            sk_priv = RSA.generate(key_bits)
        if ck_priv is None:
            ck_priv = RSA.generate(key_bits)
        # To write use
        #   with open(path, 'wb+') as file: file.write(sk_priv.exportKey('PEM'))
        # To read use
        #   with open(path, 'rb') as file: sk_priv = RSA.importKey(file.read())
        self._sk_priv = sk_priv
        self._ck_priv = ck_priv

    @property
    def login(self):
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
        """ Return the size of the RSA key. """
        return self._key_bits

    def __str__(self):

        return "NOT IMPLEMENTED: User.__str__()"


class User(_User):

    def create_from_file(self, path):
        """ Parse the serialized User object. """

        return NotImplementedError()


class _PubUser(object):
    """
    This version of the user descriptor includes the public part of  RSA keys.
    """

    def __init__(self, login, sk_, ck_):

        # The login must always be a valid name, one including no
        # delimiters or other odd characters.

        if not valid_name(login):
            raise AtttributeError("not a valid login: '%s'" % login)
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

    def __init__(self, handle, login=os.environ['LOGNAME'],
                 sk_priv=None, ck_priv=None, key_bits=2048):
        if not valid_file_name(handle):
            raise AttributeError("'%s' is not a valid handle" % handle)
        super().__init__(login, sk_priv, ck_priv, key_bits)
        self._handle = handle


class PubCommitter(_PubUser):
    """
    The public view of a Committer, one which contains no secret keys.
    """

    def __init__(self, handle, login=os.environ['LOGNAME'],
                 sk_=None, ck_=None):
        if not valid_file_name(handle):
            raise AttributeError("'%s' is not a valid handle" % handle)
        super().__init__(login, sk_, ck_)
        self._handle = handle
