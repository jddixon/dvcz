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

__all__ = ['__version__', '__version_date__', 'DvczError']

__version__ = '0.1.2'
__version_date__ = '2016-12-24'


class DvczError(RuntimeError):
    pass


class Project(object):
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
            raise AttributeError("not a valid project name: '%s'" % name)
        if main_lang and not valid_file_name(main_lang):
            raise AttributeError(
                "not a valid language name: '%s'" %
                main_lang)

        os.makedirs(proj_path, exist_ok=True, mode=mode)

        self._name = name
        self._proj_path = proj_path
        self._main_lang = main_lang

    @property
    def name(self):
        """
        Return the name of the project.

        This is a valid file name, one containing no delimiters.
        """
        return self._name

    @property
    def proj_path(self):
        """ Return the POSIX path to the project's root directory."""
        return self._proj_path

    @property
    def main_lang(self):
        """
        Return the main programming language for the project.

        This is a short name such as 'c' (for ANSI C) or 'py' (Python).
        """
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
