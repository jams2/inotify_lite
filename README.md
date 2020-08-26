Module inotify_lite
===================

Sub-modules
-----------
* inotify_lite.inotify_lite

Classes
-------

`FileWatcher(callback: Callable[[inotify_lite.inotify_lite.InotifyEvent], Any], *files: str, blocking: bool = True, watch_flags: inotify_lite.inotify_lite.INFlags = INFlags.NO_FLAGS)`
:   Base class for TreeWatcher and FileWatcher. Wraps inotify(7).
    
    Caller must provide a callback, which will be executed for each
    observed event.
    
    Attributes:
        inotify_fd:
            file descriptor returned by call to inotify_init1 (int).
        callback:
            a callable taking one argument (InotifyEvent), to be called for each event.
        watch_flags:
            flags to be passed to inotify_add_watch.
        watch_fds:
            a dict mapping watch descriptors to their associated filenames.
        files:
            a set of filenames currently being watched.
        LEN_OFFSET:
            we need to read the length of the name before unpacking the bytes
            to the struct format. See the underlying struct_event.
        MAX_READ:
            int, maximum bytes to read into buffer.

    ### Ancestors (in MRO)

    * inotify_lite.inotify_lite.Inotify

`INFlags(value, names=None, *, module=None, qualname=None, type=None, start=1)`
:   See inotify_add_watch(2), sys/inotify.h, bits/inotify.h.

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

`Inotify(callback: Callable[[inotify_lite.inotify_lite.InotifyEvent], Any], *files: str, blocking: bool = True, watch_flags: inotify_lite.inotify_lite.INFlags = INFlags.NO_FLAGS)`
:   Base class for TreeWatcher and FileWatcher. Wraps inotify(7).
    
    Caller must provide a callback, which will be executed for each
    observed event.
    
    Attributes:
        inotify_fd:
            file descriptor returned by call to inotify_init1 (int).
        callback:
            a callable taking one argument (InotifyEvent), to be called for each event.
        watch_flags:
            flags to be passed to inotify_add_watch.
        watch_fds:
            a dict mapping watch descriptors to their associated filenames.
        files:
            a set of filenames currently being watched.
        LEN_OFFSET:
            we need to read the length of the name before unpacking the bytes
            to the struct format. See the underlying struct_event.
        MAX_READ:
            int, maximum bytes to read into buffer.

    ### Descendants

    * inotify_lite.inotify_lite.FileWatcher
    * inotify_lite.inotify_lite.TreeWatcher

    ### Class variables

    `LEN_OFFSET`
    :

    `MAX_READ`
    :

    ### Static methods

    `get_event_struct_format(name_len: int) ‑> str`
    :

    ### Methods

    `watch(self)`
    :

`InotifyEvent(wd: int, mask: int, cookie: int, name_len: int, name: bytes)`
:   Equivalent to struct_event from inotify.h.
    
    Attributes:
        wd: watch descriptor (int).
    
        mask: int event mask (check against INFlags).
    
        cookie: int associating IN_MOVED_FROM events with corresponding IN_MOVED_TO.
    
        name_len: int, length of name string (len in underlying struct).
    
        name: string, name of watched file that event refers to.

    ### Static methods

    `str_from_bytes(byte_obj: bytes) ‑> str`
    :   Convert null terminated bytes to Python string.
        
        Args:
            byte_obj: bytes representing a null-terminated string.
        
        Returns:
            a Python string.

`TreeWatcher(callback: Callable[[inotify_lite.inotify_lite.InotifyEvent], Any], *dirs: str, watch_subdirs: bool = True, blocking: bool = True, watch_flags: inotify_lite.inotify_lite.INFlags = INFlags.ALL_EVENTS)`
:   Watch directories, and optionally all subdirectories.
    
    Attributes:
        watch_subdirs:
            a boolean, whether to include subdirectories.
        moved_to:
            a dict mapping cookies from IN_MOVED_TO events to their associated filenames.
        moved_from:
            a dict mapping event.cookie from IN_MOVED_FROM events to their associated filenames.

    ### Ancestors (in MRO)

    * inotify_lite.inotify_lite.Inotify

    ### Methods

    `get_event_abs_path(self, event: inotify_lite.inotify_lite.InotifyEvent) ‑> str`
    :
