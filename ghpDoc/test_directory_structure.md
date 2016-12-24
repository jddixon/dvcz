# Dvcz Test Directory Structure

## Directory Overview

The class `DvcTestSetup` is used to create a test directory under `tmp/`
in the current directory.  This looks like:

    tmp/
      RUN_ID/               # unique 8-character file name
        home/
          LOGIN/
            dvcz/
              committers/
                HANDLE      # serialized Committer object
                ...         #   containing secret keys, etc
              stores/
                STORE_NAME  # serialized Store object
                ...         * more such
        projects/
          PROJECT_NAME/     # per-project subdirectory
            dvcz/
              builds        # list of BuildLists, timestamp plus hash
              lastBuildList
          ...               # additional per-project subdirs
        stores/
          STORE_NAME/
            SHA_SIG         # hex value of SHAx_HEX_NONE, where x is 1, 2, or 3
            in/
              USER_ID
                SHA_SIG
                in/
                tmp/
                CONTENT_KEY # hash of data file
                ...         # more hashes
              ...           # more USER_ID subdirs


Here `run_id` is an 8-character file name not already in use under `tmp`,
so `run_dir` is `tmp/RUN_ID`.  This has

* home,
* projects, and
* stores

subdirectories.

## home

In each `run_dir` there is a dummy `home/LOGIN` directory,
and under that a `dvcz` directory that corresponds to `$HOME/.dvcz`.
The login may have any number of associated **Committer** objects.
The serialization of each Committer is to be found in a file whose
name is the Committer's handle.  The Committer's RSA key, `skPriv`,
is used for digital signatures on `BuildList`s created during test
runs

While in current use there is only one `LOGIN` subdirectory, it is
possible that in future there will be many such subdirectories, one
for each login using the test directory.

## projects

At the same level as the `home/` directory there is a `projects/`
directory and under that a per-project subdirectory with the same
name of as the project.  Each such project directory will contain a
`dvcz/` subdirectory.  At the time of writing `dvcz/` contains only
`builds` and `lastBuildList`.

And at the same level as `home/` and `projects/` is the `stores/`
subdirectory.  This contains the dummy content-keyed stores used
in the test runs.  Each such store has a unique name.  Each has
an `in/` directory and within that a subdirectory for each Committer
accessing the store.  Each such subdirectory has the Committers's
32-byte `user_id` as its name.  The subdirectory itself is a single-level
`FLAT_DIR` content-keyed store.  This will contain `in/` and `tmp/`
subdirectories, an `SHA_SIG` file, and zero or more data files named
with their content keys, each such content key being the SHA hash
of the file content.  The type of SHA hash used will be the same as
the type of hash used to encrypt None as `SHA_SIG`.

Currently, the store under `STORE_NAME` may be organized in any of three
ways: `DIR_FLAT`, `DIR16x16`, and `DIR256x256`.  In the first case
`SHA_SIG` is the full value of the quantity.  So if this is SHA1_HEX_NONE,
for example, then `SHA_SIG` is `da39a3ee...0709` (where I omit 28 hex chars
for clarity).  But if the directory structure is `DIR16x16`, only the first
nibble appears in the top directory and the second in the middle directory,
so `SHA_SIG` appears in the file system as `d/a/da39a3ee...0709`.  And
similarly if the directory structure is `DIR256x256` the value in the
file system is `da/39/da39a3ee...0709`.

Note that the `in/` subdirectories are always `DIR_FLAT`, so only the
simple form is used; for example, `da39a3e...0709` in the case where
`SHA_SIG` is `SHA1_HEX_NONE`.
