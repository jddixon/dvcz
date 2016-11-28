<h1 class="libTop">dvcz</h1>

**dvcz** is a
[distributed version control system](https://en.wikipedia.org/wiki/Distributed_version_control)
in the early stages of specification and development.  It can be seen as
a front end to
a group of loosely coordinated servers.

## Existing Code and Project Structure

dvcz is one of a number of projects using
[Github](https://www.github.com)
for storage.  Each of these has a `**.dvcz**` subdirectory and a number of
scripts in the project's root directory.

### Environmental Variables

These must be defined in order for project software to work correctly;
they include:

* DEV_BASE, the path to the directory containing project directories
* DVCZ_DIR, which might be for example "/var/app/sharedev"
* DVCZ_UDIR, where files are stored by content key; eg `/var/app/sharedev/U`

* DVCZ_USER, path to this user's .dvcz/, so $HOME/.dvcz
* DVCZ_AUTHOR, the double-quoted name of the author, such as "John Smith"
* DVCZ_AUTHOR_EMAIL, such as "john.smith@example.com"
* DVCZ_PATH_TO_KEYS, conventionally "$DVCZ_USER/node"

On a Linux system these are conventionally set in `$HOME/.bashrc`, a bash
script, with a line like

    export DEV_BASE="$HOME/dev"

### User .dvcz Subdirectory

This is `$DVCZ_USER` which is conventionally `$HOME/.dvcz`.  Files in or
below this subdirectory include

* `node/skPriv.pem`, ie `$DVCZ_PATH_TO_KEYS/skPriv.pem`, the RSA secret key
    used for signing BuildLists etc
* `id`, the globally unique 160-bit ID used to identify the user

### Project .dvcz Subdirectory

Files in this directory describe the current state of the project.  At
this point these include

* **builds**, a list of of timestamps, version numbers, and content hashes
* **lastBuildlist*", the full text of the last build list, digitally signed
with the committer's RSA key
* **projCfg**, a description of what is to be included in each project build
* **projCfg.local**, a list of items (file or directory names)
    which must be included in `projCfg` if it is rewritten
* **version**, containing two newline-terminated lines, the first of which
    is a serialized `DecimalVersion` and the second a date in `CCYY-MM-DD`
    format

#### builds

This is a list in chronological order of

* the date and time at which each version of the project has been committed
* the corresponding version number
* and the content hash of the BuildList for the commit

An excerpt from a typical `builds` file:

    2016-05-19 18:31:36 v0.4.23 8a8ed84f8937a1f20c0d317c115e87fc9ebb12e8
    2016-05-25 19:53:11 v0.4.24 92d53f31e14c52de23830ad093db11440d77803a
    2016-05-25 20:04:30 v0.4.24 2026ccd5c10112e509108606f7770a4cd3f61a6c
    2016-06-15 00:32:54 v0.4.26 752e4eb5bca0033a6db4fb1391df120671c0daa9

Each line begins with a timestamp in `CCYY-MM-DD HH:MM:SS` format.
This is followed by a three or four part decimal version number, and
then the content key (the SHA hash of the contents of the BuildLists
committed).  The content key is 40 hexadecimal digits if using `SHA1`
and 64 hex digits if using `SHA2`.

### bkp2U Script

This is a bash script in the project's root directory.  This is
`$DEV_BASE/$PROJECT` and so might resemble `/home/jdd/dev/dvcz`.

The `bkp2U` script
backs up project files to the
content-keyed store, the path to which is set in `$DVCZ_UDIR`.   Before
doing the actual backup, the script changes the working directory to
the project's base directory,
`$DEV_BASE/$PROJECT`.  During the course of the backup the script generates a
BuildList for the contents of the project directory and subdirectories.
After committing
all of the project files, the script digitally signs the BuileList
using the RSA key
stored at `$DVCZ_PATH_TO_KEYS`.  This points to an RSA private key in
PEM format (and so might look like `$HOME/.dvcz/node`.  The key file
is conventionally named `skPriv.pem`.  That is, the path to the key
file is something like `/home/jdd/.dvcz/node/skPriv.pem`.

The signed build list is then (a) stored in `$DVCZ_UDIR` and (b) written
to `.dvcz/lastBuildList`.

## Implementation Language

In its current form dvcz is based on Python 3.

## Dependencies

dvcz depends upon a number of related projects:

* [**buildlist**](https://jddixon.github.io/buildlist), a technology
for authenticating the contents of a directory structure
* [**fieldz**](https://jddixon.github.io/fieldz), a communications
prototol intended to be compatible with a subset of Google's
[Protocol Buffers](https://developers.google.com/protocol-buffers)
* **upax**, as described above

## Project Status

In active development but and currently used for backup but
generally not yet specified in detail.

