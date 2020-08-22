Module inotify_lite
===================
inotify_lite: a wrapper around Linux's inotify functionality.

Exposes functionality for watching files or directories, and performing
actions on reported events. See also: Kovid Goyal's 2013 calibre implementation.

    Typical usage:

    watcher = TreeWatcher(lamdba x: print(x), ".")
    watcher.watch()

Functions
---------

    
`inotify_setup()`
:   

Classes
-------

`Event(wd, mask, cookie, len, name)`
:   Event(wd, mask, cookie, len, name)

    ### Ancestors (in MRO)

    * builtins.tuple

    ### Instance variables

    `cookie`
    :   Alias for field number 2

    `len`
    :   Alias for field number 3

    `mask`
    :   Alias for field number 1

    `name`
    :   Alias for field number 4

    `wd`
    :   Alias for field number 0

`FileWatcher(callback: Callable[[inotify_lite.Event], Any], *files: str, blocking: bool = True, watch_flags: inotify_lite.INFlags = INFlags.NO_FLAGS)`
:   Base class for TreeWatcher and FileWatcher. Wraps inotify(7).
    
    Caller must provide a callback, which will be executed for each
    observed event.
    
    Attributes:
        inotify_fd:
            file descriptor returned by call to inotify_init1 (int).
        callback:
            a callable taking one argument (Event), to be called for each event.
        watch_flags:
            flags to be passed to inotify_add_watch.
        watch_fds:
            a dict mapping watch descriptors to their associated filenames.
        files:
            a set of filenames currently being watched.

    ### Ancestors (in MRO)

    * inotify_lite.Inotify

`INFlags(value, names=None, *, module=None, qualname=None, type=None, start=1)`
:   See inotify_add_watch(2), <sys/inotify.h>, <bits/inotify.h>.

    ### Ancestors (in MRO)

    * enum.IntFlag
    * builtins.int
    * enum.Flag
    * enum.Enum

    ### Class variables

    `ACCESS`
    :

    `ALL_EVENTS`
    :

    `ATTRIB`
    :

    `CLOEXEC`
    :

    `CLOSE`
    :

    `CLOSE_NOWRITE`
    :

    `CLOSE_WRITE`
    :

    `CREATE`
    :

    `DELETE`
    :

    `DELETE_SELF`
    :

    `DONT_FOLLOW`
    :

    `EXCL_UNLINK`
    :

    `IGNORED`
    :

    `ISDIR`
    :

    `MASK_ADD`
    :

    `MASK_CREATE`
    :

    `MODIFY`
    :

    `MOVE`
    :

    `MOVED_FROM`
    :

    `MOVED_TO`
    :

    `NONBLOCK`
    :

    `NO_FLAGS`
    :

    `ONESHOT`
    :

    `ONLYDIR`
    :

    `OPEN`
    :

    `Q_OVERFLOW`
    :

    `UNMOUNT`
    :

`Inotify(callback: Callable[[inotify_lite.Event], Any], *files: str, blocking: bool = True, watch_flags: inotify_lite.INFlags = INFlags.NO_FLAGS)`
:   Base class for TreeWatcher and FileWatcher. Wraps inotify(7).
    
    Caller must provide a callback, which will be executed for each
    observed event.
    
    Attributes:
        inotify_fd:
            file descriptor returned by call to inotify_init1 (int).
        callback:
            a callable taking one argument (Event), to be called for each event.
        watch_flags:
            flags to be passed to inotify_add_watch.
        watch_fds:
            a dict mapping watch descriptors to their associated filenames.
        files:
            a set of filenames currently being watched.

    ### Descendants

    * inotify_lite.FileWatcher
    * inotify_lite.TreeWatcher

    ### Class variables

    `LEN_OFFSET`
    :

    `MAX_READ`
    :

    ### Static methods

    `get_event_struct_format(name_len: int) ‑> str`
    :

    `str_from_bytes(byte_obj: bytes) ‑> str`
    :   Convert null terminated bytes to Python string.

    ### Methods

    `watch(self)`
    :

`TreeWatcher(callback: Callable[[inotify_lite.Event], Any], *dirs: str, watch_subdirs: bool = True, blocking: bool = True, watch_flags: inotify_lite.INFlags = INFlags.ALL_EVENTS)`
:   Watch directories, and optionally all subdirectories.
    
    Attributes:
        watch_subdirs:
            a boolean, whether to include subdirectories.
        moved_to:
            a dict mapping cookies from IN_MOVED_TO events to their associated filenames.
        moved_from:
            a dict mapping event.cookie from IN_MOVED_FROM events to their associated filenames.

    ### Ancestors (in MRO)

    * inotify_lite.Inotify

    ### Methods

    `get_event_abs_path(self, event: inotify_lite.Event) ‑> str`
    :
