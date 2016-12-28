# dvcz/store.py

""" Our distributed version control system. """

import os
import sys

#import hashlib

from buildlist import(check_dirs_in_path, generate_rsa_key,
                      read_rsa_key, rm_f_dir_contents)
from rnglib import valid_file_name
from xlattice import QQQ
from xlattice.u import UDir

# from Crypto.PublicKey import RSA

# if sys.version_info < (3, 6):
#    import sha3

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

        super().__init__(u_path, dir_struc, using_sha, mode)
        self._name = name

    @property
    def name(self):
        """
        Return the name assigned to the store.  This is a valid file
        name, a single word incorporating no delimiters.
        """
        return self._name

    def __str__(self):
        return '::'.join([self.name,
                          self.u_path,
                          UDir.DIR_STRUC_NAMES[self.dir_struc],
                          self.using_sha._name_])

    @classmethod
    def create_from_file(cls, path):
        """ Given a serialization, create a Store object. """

        with open(path, 'r') as file:
            # Possible FileNotFound.
            text = file.read()
        return cls.create_from_string(text)

    @classmethod
    def create_from_string(cls, text):
        parts = text.split('::')
        pcount = len(parts)
        if pcount == 4:
            name = parts[0]
            u_path = parts[1]
            dir_struc = UDir.name_to_dir_struc(parts[2])
            # 'item access'
            using_sha = QQQ[parts[3]]
            return Store(name, u_path, dir_struc, using_sha)
        else:
            raise DvczError("Invalid Store descriptor: '%s'" % text)
