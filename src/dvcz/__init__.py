# dvcz/__init__.py

""" Our distributed version control system. """

# import os
# import re
import sys
# import time
# import hashlib

# from buildlist import(check_dirs_in_path, generate_rsa_key,
#                       read_rsa_key, rm_f_dir_contents)
# from rnglib import valid_file_name
# from xlu import UDir

# from Crypto.PublicKey import RSA

if sys.version_info < (3, 6):
    import sha3
    assert sha3     # suppress warnings

__all__ = ['__version__', '__version_date__', 'DvczError']

__version__ = '0.1.23'
__version_date__ = '2018-03-07'


class DvczError(RuntimeError):
    """ Errors specific to the dvcz project. """
    pass
