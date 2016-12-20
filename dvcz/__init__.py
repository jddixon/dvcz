# dvcz/__init__.py

""" Our distributed version control system. """

import os
import sys
import hashlib

from buildlist import(check_dirs_in_path, generate_rsa_key,
                      read_rsa_key, rm_f_dir_contents)
from xlattice import QQQ
from xlattice.u import UDir

if sys.version_info < (3, 6):
    import sha3

__all__ = ['__version__', '__version_date__',
           'get_proj_info',
           'do_add_user',
           'DvczError']

__version__ = '0.0.19'
__version_date__ = '2016-12-19'


class DvczError(RuntimeError):
    pass


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
    Create a quasi-random committer ID by hashing the user's ssh RSA
    public key.
    """

    # pylint: disable=redefined-variable-type
    if using_sha == QQQ.USING_SHA1:
        sha = hashlib.sha1()
    elif using_sha == QQQ.USING_SHA2:
        sha = hashlib.sha256()
    elif using_sha == QQQ.USING_SHA3:
        sha = hashlib.sha3_256()
    sha.update(pubkey.exportKey())  # PEM format
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

    # write RSA private key to $DVCZ_DIR/node/skPriv.pem
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
