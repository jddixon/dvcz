# dvcz/store.py

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

__all__ = ['Store']


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
