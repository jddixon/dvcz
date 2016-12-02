# dvcz/__init__.py

""" Our distributed version control system. """

import os
import sys

__all__ = ['__version__', '__version_date__', 'dvc_get_project_info']

__version__ = '0.0.15'
__version_date__ = '2016-12-01'


def dvc_get_project_info(args):
    """
    Find the project name and project directory.

    The project directory is the first found searching upward with
    a .dvcz subdirectory.   Make that the current working directory.
    If not found, program exit.  If the user's home directory is the
    first found, program exit: this is not a valid project directory.
    Otherwise add project name and directory to the args namelist.
    """

    project = 'UNKNOWN_PROJECT'
    proj_dir = 'UNKNOWN_PATH'
    start_dir = os.getcwd()
    curdir = start_dir

    while curdir:
        above, sep, project = curdir.rpartition('/')    # parse path
        if sep != '/':
            print("invalid working directory: '%s'" % curdir)
            sys.exit(1)
        if os.path.exists(os.path.join(curdir, '.dvcz')):
            # we have a .dvcz subdirectory, so this is a project directory
            proj_dir = curdir
            os.chdir(proj_dir)
            break
        # otherwise we need to loop
        curdir = above

    if project.startswith('UNKNOWN') or proj_dir.startswith('UNKNOWN'):
        print(
            "unable to determine project name or directory for %s" % start_dir)
        sys.exit(1)

    if curdir == os.environ['HOME']:
        print("no project directory found above %s" % start_dir)
        sys.exit(0)

    args.project = project
    args.proj_dir = proj_dir
