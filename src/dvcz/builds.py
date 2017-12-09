# dvcz/dvcz/builds.py

import os
import re

from buildlist import BLError, BuildList
from dvcz import DvczError
from xlattice import HashTypes
from xlattice.u import UDir

__all__ = ['check_builds', ]

TIMESTAMP_PAT = r'(\d\d\d\d\-\d\d\-\d\d \d\d:\d\d:\d\d)'
VERSION_PAT = r'v(\d+\.\d+\.\d+)'
HASH1_PAT = r'([0-9a-fA-F]{40})'
HASH2_PAT = r'([0-9a-fA-F]{64})'
LINE1_PAT = TIMESTAMP_PAT + ' ' + VERSION_PAT + ' ' + HASH1_PAT
LINE2_PAT = TIMESTAMP_PAT + ' ' + VERSION_PAT + ' ' + HASH2_PAT
LINE1_RE = re.compile(LINE1_PAT)
LINE2_RE = re.compile(LINE2_PAT)


def _check_builds_line(line, u_dir, hashtype, verbose=False):
    u_path = u_dir.u_path

    if hashtype == HashTypes.SHA1:
        regexp = LINE1_RE
    elif hashtype == HashTypes.SHA2 or hashtype == HashTypes.SHA3:
        regexp = LINE2_RE
    else:
        print("BAD HASH FIELD:\n  %s" % line)
        return
    matches = regexp.match(line)
    if matches:
        timestamp = matches.group(1)
        version = matches.group(2)
        my_hash = matches.group(3)
        if verbose:
            print("timestamp: %s" % timestamp)
            print("version:   v%s" % version)
            print("my_hash:   %s" % my_hash)
    else:
        print("\nCANNOT PARSE LINE:\n  %s" % line)
        return

    data = u_dir.get_data(my_hash)
    if not data:
        print("\nCANNOT FIND BUILD LIST AT %s IN %s" % (my_hash, u_path))
        return

    # POSSIBLE DECODE ERROR
    text = data.decode('utf-8')

    try:
        blist = BuildList.parse(text, hashtype)
    except BLError as exc:
        print("EXCEPTION %s PARSING LINE:\n  %s" % (exc, line))
        return

    files_not_found = blist.check_in_u_dir(u_path)
    if files_not_found:
        print("\nLINE: %s" % line)
        print("SOME BUILD LIST FILES NOT FOUND:")
        for file in files_not_found:
            print("  %s %s" % (file[0], file[1]))


def check_builds(proj_path='./', u_path='/var/app/sharedev/U', verbose=False):
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
    dirstruc = u_dir.dir_struc
    hashtype = u_dir.hashtype

    if verbose:
        print("check_builds: proj_path   = %s" % proj_path)
        print("              builds_file = %s" % builds_file)
        print("              dirstruc    = %s" % dirstruc.name)
        print("              hashtype    = %s" % hashtype.name)

    with open(builds_file, 'r') as file:
        data = file.read()
    lines = data.split('\n')[:-1]       # skip the last empty line

    for line in lines:
        _check_builds_line(line, u_dir, hashtype)
