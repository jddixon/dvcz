# dvcz/dvcz/builds.py

import os
import re

from dvcz import DvczError
from xlattice import HashTypes
from xlattice.u import DirStruc

__all__ = ['check_builds', ]

TIMESTAMP_PAT = r'(\d\d\d\d\-\d\d\-\d\d \d\d:\d\d:\d\d)'
VERSION_PAT = r'v([\d]{1-3}\.[\d]{1-3}\.[\d]{1-3})'
HASH1_PAT = r'([0-9a-fA-F]{40})'
HASH2_PAT = r'([0-9a-fA-F]{64})'
LINE1_PAT = TIMESTAMP_PAT + ' ' + VERSION_PAT + ' ' + HASH1_PAT
LINE2_PAT = TIMESTAMP_PAT + ' ' + VERSION_PAT + ' ' + HASH2_PAT
LINE1_RE = re.compile(LINE1_PAT)
LINE2_RE = re.compile(LINE2_PAT)


def _check_builds_line(line, u_dir, hashtype):
    pass


def check_builds(proj_path='./', u_path='/var/app/sharedev/U'):
    """
    Verify that the BuildLists in .dvcz/builds are correct and that
    files listed are in uDir, the content-keyed store
    """

    builds_file = os.path.join(proj_path, '.dvcz', 'builds')
    if not os.path.exists(builds_file):
        raise DvczError("builds file at %s does not exist" % builds_file)

    if not os.path.exists(u_path):
        raise DvczError("cannot locate content-keyed store %s" % u_path)

    u_dir = UDir.discover(u_path)
    dirstruc = u_dir.dir_struc()
    hashtype = u_dir.hashtype

    # DEBUG
    print("check_builds: proj_path   = %s" % proj_path)
    print("              builds_file = %s" % builds_file)
    print("              dirstruc    = %s" % dirstruc.dir_struc.name)
    print("              hashtype    = %s" % hashtype.name)
    # END

    with open(builds_file, 'r') as file:
        data = file.read()
    lines = data.split('\n')[:-1]       # skip the last empty line

    for line in lines:
        # DEBUG
        print(line)
        # END
        _check_builds_line(line, u_dir, hashtype)
