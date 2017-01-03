# dvcz/project.py

""" Project: a collection of code in and below a project root directory. """

import os
import re

from dvcz import DvczError

__all__ = ['get_proj_info', 'Project']


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
    except AttributeError:              # no such option
        proj_path = os.getcwd()
    os.chdir(proj_path)         # may raise FileNotFoundError

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

    # Project names may not contain dots or dashes; they may contain
    # digits but must not start with a digit.
    PROJ_NAME_CHARS =  \
        'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_'
    PROJ_NAME_STARTERS = \
        'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz_'

    VALID_PROJ_NAME_PAT = \
        r'^[' + PROJ_NAME_STARTERS + '][' + PROJ_NAME_CHARS + ']*$'
    VALID_PROJ_NAME_RE = re.compile(VALID_PROJ_NAME_PAT)

    @classmethod
    def valid_proj_name(cls, name):
        """ Return whether the name matches the regular expression. """
        match = cls.VALID_PROJ_NAME_RE.match(name)
        return match is not None

    def __init__(self, name, proj_path, main_lang='', mode=0o755):

        # DEBUG
        # print("PROJECT._INIT_: name %s, proj_path %s, main_lang %s" % (
        #       name, proj_path, main_lang))
        # END
        if not Project.valid_proj_name(name):
            raise DvczError("not a valid project name: '%s'" % name)
        if main_lang and not Project.valid_proj_name(main_lang):
            raise DvczError(
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

    def __eq__(self, other):
        if not isinstance(other, Project) or \
                self._name != other.name or \
                self._proj_path != other.proj_path:
            return False
        if self._main_lang and not other.main_lang:
            return False
        if not self._main_lang and other.main_lang:
            return False
        if self._main_lang != other.main_lang:
            return False
        return True

    def __str__(self):
        return "%s::%s::%s" % (self._name, self._proj_path, self._main_lang)

    @classmethod
    def create_from_file(cls, path):
        """ Given a serialization, create a Project object. """

        with open(path, 'r') as file:
            # Possible FileNotFound.
            text = file.read()
        return cls.create_from_string(text)

    @classmethod
    def create_from_string(cls, text):
        """ Create a Project object from a simple string serialization. """

        parts = text.split('::')
        pcount = len(parts)
        if pcount == 2:
            return Project(parts[0], parts[1])
        elif pcount == 3:
            return Project(parts[0], parts[1], parts[2])
        else:
            raise DvczError("invalid Project descriptor: '%s'" % text)
