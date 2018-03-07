# dvcz/store.py

"""
Content-keyed store for our distributed version control system.

In production serialized Store descriptors for a given user are collected under
    $HOME/.dvcz/stores/
That is, stores/ is a collection of files, where each file is a
serialized Store.  The name of the file is the name of the Store.
Such names are guaranteed to be unique within stores/.

The store itself is not serialized.  What is serialized is the Store,
whcih contains metadata about the store.
/
Each store is a UDir, a content-keyed store, and so looks like

    PATH_TO_STORE/
        in/
        tmp/
        --hash--
        --hash--
        ...

Depending on the directory structure and hash type, `--hash--` will
represent either a 4-bit/single hex digit directory name, an
8-bit/two hex digit directory name, or a 160-bit/40 hext digit
content key or a 256-bit/64 hex digit file name, where the file
name is the hash of the file contents.

`in/` and `tmp/` are scratch (temporary) UDirs used by the system.
Each user has a unique 256-bit/32-byte/64 hex digit userID.  A
commit copies user files into the store.  Files are initially
copied to a subdirectory of `in/` which is itself a UDir with a
DIR_FLAT directory structure.  So the commit operation creates

    in/
        USER_ID/        # a UDir, DIR_FLAT
            --hash--
            --hash--
            --hash--
            ...
            --hash--

If N files are being committed, N new entries will appear below
`in/USER_ID` when the operation is complete.`:

"""

# import hashlib

# from buildlist import(check_dirs_in_path, generate_rsa_key,
#                      read_rsa_key, rm_f_dir_contents)
from dvcz import DvczError
from dvcz.project import Project
from xlattice import HashTypes
from xlu import UDir, DirStruc

# from Crypto.PublicKey import RSA

# if sys.version_info < (3, 6):
#    import sha3

__all__ = ['Store']


class Store(UDir):
    """
    Link a name to a content-keyed store.

    The name should be unique within the context and must be a valid store
    name.  The name need have nothing to do with u_path.  Currently the
    rules for store name are the same as the rules for project names.

    If the directory at u_path already exists, its directory
    structure (dir_struc) and SHA hash type (hashtype) are discovered
    and override any attributes supplied.

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
        Return the name assigned to the store.

        This is a convenience.  It is a valid store name, a single word
        incorporating no delimiters.
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
