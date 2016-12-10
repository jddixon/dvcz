# dvcz/__init__.py

""" Our distributed version control system. """

import os
import sys
import hashlib

if sys.version_info < (3, 6):
    import sha3

from buildlist import(check_dirs_in_path, generate_rsa_key,
                      read_rsa_key, rm_f_dir_contents)
from xlattice import QQQ
from xlattice.u import UDir

__all__ = ['__version__', '__version_date__',
           'dvc_get_project_info',
           'do_add_user']

__version__ = '0.0.17'
__version_date__ = '2016-12-10'


def dvc_get_project_info(options):
    """
    Find the project name and project directory.

    The project directory is the first found searching upward with
    a .dvcz subdirectory.   Make that the current working directory.
    If not found, program exit.  If the user's home directory is the
    first found, program exit: this is not a valid project directory.
    Otherwise add project name and directory to the options namelist.
    """

    try:
        project = options.project
    except AttributeError:
        project = 'UNKNOWN_PROJECT'

    # WORKING HERE
    projdir = 'UNKNOWN_PATH'
    start_dir = os.getcwd()
    curdir = start_dir

    while curdir:
        above, sep, project = curdir.rpartition('/')    # parse path
        if sep != '/':
            print("invalid working directory: '%s'" % curdir)
            sys.exit(1)
        if os.path.exists(os.path.join(curdir, '.dvcz')):
            # we have a .dvcz subdirectory, so this is a project directory
            projdir = curdir
            os.chdir(projdir)
            break
        # otherwise we need to loop
        curdir = above

    if project.startswith('UNKNOWN') or projdir.startswith('UNKNOWN'):
        print(
            "unable to determine project name or directory for %s" % start_dir)
        sys.exit(1)

    if curdir == os.environ['HOME']:
        print("no project directory found above %s" % start_dir)
        sys.exit(0)

    options.project = project
    options.projdir = projdir


# == adduser ========================================================

def make_committer_id(pubkey, using_sha):
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
        u_dir = UDir.discover(options.u_path, using_sha=using_sha)

        # create $U_DIR/in/$ID/ which is DIR_FLAT with the correct using_sha
        my_in_path = os.path.join(options.u_path,
                                  os.path.join('in', committer_id))
        my_in_dir = UDir.discover(my_in_path, using_sha=using_sha)
