# dvcz/store.py

""" Our distributed version control system. """

#import hashlib

# from buildlist import(check_dirs_in_path, generate_rsa_key,
#                      read_rsa_key, rm_f_dir_contents)
from dvcz import DvczError
from dvcz.project import Project
from xlattice import HashTypes
from xlattice.u import UDir, DirStruc

# from Crypto.PublicKey import RSA

# if sys.version_info < (3, 6):
#    import sha3

__all__ = ['Store']


class Store(UDir):
    """
    Specifies a content-keyed store.

    The name should be unique within the context and must be a valid store
    name.  The name need have nothing to do with u_path.  Currently the
    rules for store name are the same as the rules for project names.

    If the directory at u_path already exists, its directory
    structure (dir_struc) and SHA hash type (hashtype) are discovered
    and override the attributes supplied.

    If u_path does not exist, the directory is created using the attributes
    passed.

    """

    def __init__(self, name, u_path, dir_struc=DirStruc.DIR_FLAT,
                 hashtype=HashTypes.SHA2, mode=0o755):

        if not Project.valid_proj_name(name):
            raise DvczError("not a valid store name: '%s'" % name)
        if not isinstance(dir_struc, DirStruc):
            raise DvczError("not a valid dir_struc: '%s'" % dir_struc)
        super().__init__(u_path, dir_struc, hashtype, mode)
        self._name = name

    @property
    def name(self):
        """
        Return the name assigned to the store.  This is a valid store
        name, a single word incorporating no delimiters.
        """
        return self._name

    def __str__(self):
        return '::'.join([self.name,
                          self.u_path,
                          # pylint: disable=no-member
                          self.dir_struc.name,
                          self.hashtype.name])

    @classmethod
    def create_from_file(cls, path):
        """ Given an on-disk serialization, create a Store object. """

        with open(path, 'r') as file:
            # Possible FileNotFound.
            text = file.read()
        return cls.create_from_string(text)

    @classmethod
    def create_from_string(cls, text):
        """ Given a simple string serialization, create a Store object. """
        parts = text.split('::')
        pcount = len(parts)
        if pcount == 4:
            name = parts[0]
            u_path = parts[1]
            ds_name = parts[2]
            dir_struc = None
            for _ in DirStruc:
                if _.name == ds_name:
                    dir_struc = _
                    break
            else:
                raise DvczError(
                    "Not the name of a valid dir_struc name: '%s'" % ds_name)

            # 'item access'
            hashtype = HashTypes[parts[3]]
            return Store(name, u_path, dir_struc, hashtype)
        else:
            raise DvczError("Invalid Store descriptor: '%s'" % text)
