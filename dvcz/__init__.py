# dvcz/__init__.py

""" Our distributed version control system. """

import os
import re
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
    import sha3

__all__ = ['__version__', '__version_date__',
           'get_proj_info',
           'do_add_user',
           'DvczError']

__version__ = '0.1.0'
__version_date__ = '2016-12-22'


def get_proj_info(options):
    """
    Given a candidate path the the project, determine the actual path,
    change to that directory, and return the project name, path, and
    parent path.

    The candidate path is options.proj_path.  If this is not a valid
    directory, raise DvczError.

    The project directory is the first found searching upward which has
    a .dvcz subdirectory.   Make that the current working directory.
    If not found, raise DvczError.  If the user's home directory is the
    first found, program exit: this is not a valid project directory.
    Otherwise add project name and directory to the options Namespace.

    The project name, path, and parent are added to the options
    Namespace as options.proj_name, options.proj_path, and
    options.proj_parent respectively.
    """

    proj_name = ''
    proj_parent = ''
    try:
        proj_path = options.proj_path
        try:
            os.chdir(proj_path)
        except FileNotFoundError:
            raise DvczError("%s does not exist" % proj_path)
    except AttributeError:
        proj_path = os.getcwd()
    curdir = proj_path
    start_dir = curdir

    while curdir:
        proj_parent, sep, proj_name = curdir.rpartition('/')    # parse path
        if sep != '/':
            raise DvczError("invalid working directory: '%s'" % curdir)
        if os.path.exists(os.path.join(curdir, '.dvcz')):
            # we have a .dvcz subdirectory, so this is a project directory
            proj_path = curdir
            os.chdir(proj_path)
            break
        # otherwise we need to loop
        curdir = proj_parent

    if curdir == os.environ['HOME'] or curdir == '' or curdir is None:
        raise DvczError("no project directory found above %s" % start_dir)

    options.proj_name = proj_name
    options.proj_path = proj_path
    options.proj_parent = proj_parent
    os.chdir(proj_path)


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


class DvczError(RuntimeError):
    pass


class User(object):
    """
    This version of the user descriptor includes secret RSA keys.
    """

    def __init__(self, login, sk_priv=None, ck_priv=None, key_bits=2048):

        # The login must always be a valid name, one including no
        # delimiters or other odd characters.

        if not valid_name(login):
            raise AtttributeError("not a valid login: '%s'" % login)

        if sk_priv is None:
            sk_priv = RSA.generate(bit_count)
        if ck_priv is None:
            ck_priv = RSA.generate(bit_count)
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
        return self._sk_priv

    @property
    def ck_priv(self):
        return self._ck_priv

    @property
    def key_bits(self):
        return self._key_bits

    def __str__(self):

        return "NOT IMPLEMENTED: User.__str__()"

    def create_from_file(self, path):

        return NotImplementedError()


class PubUser(object):
    """
    This version of the user descriptor includes the public part of  RSA keys.
    """

    def __init__(self, login, sk, ck):

        # The login must always be a valid name, one including no
        # delimiters or other odd characters.

        if not valid_name(login):
            raise AtttributeError("not a valid login: '%s'" % login)

        # To write use
        #   with open(path, 'wb+') as file: file.write(sk.exportKey('PEM'))
        # To read use
        #   with open(path, 'rb') as file: sk = RSA.importKey(file.read())
        self._sk = sk
        self._ck = ck

    @property
    def login(self):
        return self._login

    @property
    def sk(self):
        return self._sk

    @property
    def ck(self):
        return self._ck

    def __str__(self):

        return "NOT IMPLEMENTED: User.__str__()"

    def create_from_file(self, path):

        raise NotImplementedError()

    @classmethod
    def create_from_user(cls, user):
        """ Replaces private RSA keys with public parts. """
        return PubUser(user.login,
                       user.sk_priv.publickey(),
                       user.ck_priv.publickey())


class Committer(User):
    """
    """

    def __init__(self, login, handle,
                 sk_priv=None, ck_priv=None, key_bits=2048):
        super().__init(login, sk_priv, ck_priv, key_bits)


class PubCommitter(PubUser):
    """
    """

    def __init__(self, login, handle,
                 sk_priv=None, ck_priv=None, key_bits=2048):
        super().__init(login, sk_priv, ck_priv, key_bits)


class DvcProject(object):
    """
    Dvcz project descriptor.

    The project name must be a valid name (incorporate no delimiters or
    odd characters) and should be unique in the context.  The project
    path (proj_path) may be either relative or absolute.  If it does
    not exist it will be created with the mode indicated.  main_lang,
    indicating the computer language used, is optional but if supplied
    must be another valid name.
    """

    def __init__(self, name, proj_path, main_lang='', mode=0o755):

        if not valid_file_name(name):
            raise AtttributeError("not a valid project name: '%s'" % name)
        if main_lang and not valid_file_name(main_lang):
            raise AtttributeError(
                "not a valid language name: '%s'" %
                main_lang)

        os.makedirs(proj_path, exist_ok=True, mode=mode)

        self._name = name
        self._proj_path = proj_path
        self._main_lang = main_lang

    @property
    def name(self):
        return self._name

    @property
    def proj_path(self):
        return self._proj_path

    @property
    def main_lang(self):
        return self._main_lang


class Store(UDir):
    """
    Specifies a content-keyed store.

    The name should be unique within the context and must be a valid file
    name.  The name need have nothing to do with u_path.

    If the directory at u_path already exists, its directory
    structure (dir_struc) and SHA hash type (using_sha) are discovered
    and override the attributes supplied.

    If u_path does not exist, the directory is created using the attributes
    passed.

    """

    def __init__(self, name, u_path, dir_struc=UDir.DIR_FLAT,
                 using_sha=QQQ.USING_SHA2, mode=0o755):

        if not valid_file_name(name):
            raise AttributeError("not a valid file name: '%s'" % name)

        super().__init__(u_path, dir_struc, using_Sha, mode)
        self._name = name

    @property
    def name(self):
        """
        Return the name assigned to the store.  This is a valid file
        name, a single word incorporating no delimiters.
        """
