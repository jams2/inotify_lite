"""inotify_lite: a wrapper around Linux's inotify functionality.

Exposes functionality for watching files or directories, and performing
actions on reported events.

    Typical usage:

    watcher = TreeWatcher(lamdba x: print(x), ".")
    watcher.watch()
"""
from __future__ import annotations
import os
import enum
import sys
from ctypes import (
    CDLL,
    CFUNCTYPE,
    c_int,
    c_char_p,
    c_uint32,
    c_ssize_t,
    c_void_p,
    c_size_t,
    sizeof,
    get_errno,
    create_string_buffer,
)
from typing import Callable, Any, Dict, Set, List, Tuple
from struct import unpack, calcsize


def inotify_setup() -> Tuple:
    """Define prototypes and return ctypes function pointers. We use the clib
    read function as it reads into a buffer and returns the number of bytes read.

    Returns:
        A tuple of ctypes._FuncPointer instances; inotify_init1, inotify_add_watch,
        inotify_rm_watch and read.
    """
    libc = CDLL("libc.so.6")

    prototype = CFUNCTYPE(c_int, c_int, use_errno=True)
    init1 = prototype(("inotify_init1", libc), ((1, "flags", 0),))

    prototype = CFUNCTYPE(c_int, c_int, c_char_p, c_uint32, use_errno=True)
    add_watch = prototype(
        ("inotify_add_watch", libc), ((1, "fd"), (1, "pathname"), (1, "mask")),
    )

    prototype = CFUNCTYPE(c_int, c_int, c_int, use_errno=True)
    rm_watch = prototype(("inotify_rm_watch", libc), ((1, "fd"), (1, "wd")))

    prototype = CFUNCTYPE(c_ssize_t, c_int, c_void_p, c_size_t, use_errno=True)
    c_read = prototype(("read", libc), ((1, "fd"), (1, "buf"), (1, "count")))
    return init1, add_watch, rm_watch, c_read


(inotify_init1, inotify_add_watch, inotify_rm_watch, read) = inotify_setup()


class INFlags(enum.IntFlag):
    """ Flags defined in <sys/inotify.h>, <bits/inotify.h>.
    """

    NO_FLAGS = 0x0
    CLOEXEC = 0x00080000
    NONBLOCK = 0x00000800

    # Supported events suitable for MASK parameter of INOTIFY_ADD_WATCH.
    ACCESS = 0x00000001  # File was accessed.
    MODIFY = 0x00000002  # File was modified.
    ATTRIB = 0x00000004  # Metadata changed.
    CLOSE_WRITE = 0x00000008  # Writable file was closed.
    CLOSE_NOWRITE = 0x00000010  # Unwritable file closed.
    OPEN = 0x00000020  # File was opened.
    MOVED_FROM = 0x00000040  # File was moved from X.
    MOVED_TO = 0x00000080  # File was moved to Y.
    CREATE = 0x00000100  # Subfile was created.
    DELETE = 0x00000200  # Subfile was deleted.
    DELETE_SELF = 0x00000400  # Self was deleted.
    MOVE_SELF = 0x00000800  # Self was moved.

    # Events sent by the kernel.
    UNMOUNT = 0x00002000  # Backing fs was unmounted.
    Q_OVERFLOW = 0x00004000  # Event queued overflowed.
    IGNORED = 0x00008000  # File was ignored.

    # Helper events.
    CLOSE = CLOSE_WRITE | CLOSE_NOWRITE  # Close.
    MOVE = MOVED_FROM | MOVED_TO  # Moves.

    # Special flags.
    ONLYDIR = 0x01000000  # Only watch the path if it is a directory.
    DONT_FOLLOW = 0x02000000  # Do not follow a sym link.
    EXCL_UNLINK = 0x04000000  # Exclude events on unlinked objects.
    MASK_CREATE = 0x10000000  # Only create watches.
    MASK_ADD = 0x20000000  # Add to the mask of an already existing watch.
    ISDIR = 0x40000000  # Event occurred against dir.
    ONESHOT = 0x80000000  # Only send event once.

    # All events which a program can wait on.
    ALL_EVENTS = (
        ACCESS
        | MODIFY
        | ATTRIB
        | CLOSE_WRITE
        | CLOSE_NOWRITE
        | OPEN
        | MOVED_FROM
        | MOVED_TO
        | CREATE
        | DELETE
        | DELETE_SELF
        | MOVE_SELF
    )


class InotifyEvent:
    """Maps to struct_event from inotify.h. The from_struct classmethod is provided
    for convenience.

    Attributes:
        wd (int): watch descriptor.
        mask (int): event mask (check against INFlags).
        cookie (int): unique id associating IN_MOVED_FROM events with corresponding IN_MOVED_TO.
        name_len (int): length of name string (len in underlying struct).
        name (string): name of watched file that event refers to.
    """

    def __init__(self, wd: int, mask: int, cookie: int, name_len: int, name: bytes):
        self.wd = wd
        self.mask = mask
        self.cookie = cookie
        self.name_len = name_len
        self.name = self.str_from_bytes(name)

    @classmethod
    def from_struct(cls, struct_tuple: Tuple) -> InotifyEvent:
        """ Returns a new InotifyEvent instance from (tuple) result
        of calling struct.unpack on bytes, with struct_event format.

        Arguments:
            struct_tuple (tuple): tuple returned from struct.unpack.
                Expects members wd (int), mask (int), cookie (int), name_len (int),
                name (bytes).

        Returns:
            A new InotifyEvent instance.
        """
        if len(struct_tuple) != 5:
            raise ValueError("")
        for i, t in enumerate(InotifyEvent._get_struct_types()):
            if not isinstance(struct_tuple[i], t):
                raise TypeError()
        return cls(*struct_tuple)

    @staticmethod
    def _get_struct_types():
        return (int, int, int, int, bytes)

    @staticmethod
    def str_from_bytes(byte_obj: bytes) -> str:
        """ Convert null terminated bytes to Python string.

        Args:
            byte_obj (bytes): bytes representing a null-terminated string.

        Returns:
            a Python string.
        """
        return byte_obj.decode().split("\x00")[0]


class Inotify:
    """Base class for TreeWatcher. Interfaces with inotify(7).

    Caller must provide a callback, which will be executed for each
    observed event.

    Attributes:
        inotify_fd (int): file descriptor returned by call to inotify_init1 (int).
        callback (callable): a callable taking one argument (InotifyEvent),
            to be called for each event.
        watch_flags (INFlags): flags to be passed to inotify_add_watch.
        watch_fds (dict): a dict mapping watch descriptors to their associated filenames.
        files (set): a set of filenames currently being watched.
        LEN_OFFSET:
            we need to read the length of the name before unpacking the bytes
            to the struct format. See the underlying struct_event.
        MAX_READ:
            int, maximum bytes to read into buffer.
    """

    LEN_OFFSET = sizeof(c_int) + sizeof(c_uint32) * 2
    MAX_READ = 4096

    def __init__(
        self,
        callback: Callable[[InotifyEvent], Any],
        *files: str,
        blocking: bool = True,
        watch_flags: INFlags = INFlags.NO_FLAGS,
    ):
        self.inotify_fd = inotify_init1(
            INFlags.NO_FLAGS if blocking else INFlags.NONBLOCK
        )
        if self.inotify_fd < 0:
            raise OSError(os.strerror(get_errno()))
        self.callback = callback
        self.watch_flags = watch_flags
        self.watch_fds: Dict[int, str] = {}
        self.files: Set[str] = set()
        for fname in files:
            self._add_watch(os.path.abspath(fname))

    def _add_watch(self, fname: str, add_flags: INFlags = INFlags.MASK_CREATE) -> None:
        """Add an inotify watch for given file and update instance helper records.

        Args:
            fname: string, file to watch.
            add_flags: INFlags to pass to inotify_add_watch.
        """
        if not os.path.exists(fname):
            raise FileNotFoundError(fname)
        watch_fd = inotify_add_watch(
            c_int(self.inotify_fd),
            c_char_p(fname.encode("utf-8")),
            c_uint32(self.watch_flags | add_flags),
        )
        if watch_fd < 0:
            err = os.strerror(get_errno())
            raise OSError(err)
        self.files.add(fname)
        self.watch_fds[watch_fd] = fname

    def _rm_watch(self, fd: int) -> None:
        if inotify_rm_watch(c_int(self.inotify_fd), c_int(fd)) < 0:
            print(
                f"Inotify: got error removing watch fd {fd} ({self.watch_fds[fd]}):",
                file=sys.stderr,
            )
            print(os.strerror(get_errno()), file=sys.stderr)

    def _handle_event(self, event: InotifyEvent) -> None:
        self.callback(event)

    @staticmethod
    def get_event_struct_format(name_len: int) -> str:
        return f"iIII{name_len}s"

    def _watch(self):
        buf = create_string_buffer(self.MAX_READ)
        while (bytes_read := read(self.inotify_fd, buf, self.MAX_READ)) > 0:
            offset = 0
            while offset < bytes_read:
                name_len = c_uint32.from_buffer(buf, offset + self.LEN_OFFSET)
                fmt = self.get_event_struct_format(name_len.value)
                obj_size = calcsize(fmt)
                self._handle_event(
                    InotifyEvent.from_struct(
                        unpack(fmt, buf[offset : offset + obj_size])
                    )
                )
                offset += obj_size

    def _teardown(self):
        for fd in self.watch_fds:
            self._rm_watch(fd)
        os.close(self.inotify_fd)
        self.inotify_fd = -1
        self.files = set()
        self.watch_fds = {}

    def watch(self):
        try:
            self._watch()
        except KeyboardInterrupt:
            pass
        finally:
            self._teardown()


class TreeWatcher(Inotify):
    """Watch directories, and optionally all subdirectories.

    Attributes:
        watch_subdirs (bool): watch subdirectories?
        moved_to (dict): maps event.cookie from IN_MOVED_TO events to their
            associated filenames.
        moved_from (dict): maps event.cookie from IN_MOVED_FROM events to their
            associated filenames.
    """

    def __init__(
        self,
        callback: Callable[[InotifyEvent], Any],
        *dirs: str,
        watch_subdirs: bool = True,
        blocking: bool = True,
        watch_flags: INFlags = INFlags.ALL_EVENTS,
    ):
        self.watch_subdirs = watch_subdirs
        self.moved_to: Dict[int, str] = {}
        self.moved_from: Dict[int, str] = {}
        dir_paths = [os.path.abspath(os.path.expanduser(x)) for x in dirs]
        all_dirs = self._walk_subdirs(dir_paths) if watch_subdirs else dir_paths
        super().__init__(
            callback,
            *all_dirs,
            blocking=blocking,
            watch_flags=watch_flags | INFlags.ONLYDIR,
        )

    def _walk_subdirs(self, dirs: List[str]) -> List[str]:
        if not dirs:
            return []
        subdirs = []
        for dirname in dirs:
            subdirs += [
                os.path.join(dirname, x)
                for x in os.listdir(dirname)
                if os.path.isdir(x)
            ]
        return dirs + self._walk_subdirs(subdirs)

    def get_event_abs_path(self, event: InotifyEvent) -> str:
        return f"{self.watch_fds[event.wd]}/{event.name}"

    def _handle_event(self, event: InotifyEvent) -> None:
        """ As we may be watching for changes in all subdirectories,
        there are a few special cases to watch out for; new subdirectories,
        deleted subdirectories, and moved subdirectories.
        """
        if self.watch_subdirs and (event.mask & INFlags.ISDIR):
            if event.mask & INFlags.CREATE:
                new_dir_name = self.get_event_abs_path(event)
                self._add_watch(new_dir_name)
                print("Added watch: {0}".format(new_dir_name))
            elif event.mask & INFlags.DELETE:
                self._rm_watch(event.wd)
                self.files.remove(self.get_event_abs_path(event))
                del self.watch_fds[event.wd]
                print("Removed watch: {0}".format(event.name))
            elif event.mask & INFlags.MOVE:
                print("Subdirectory moved: ", end="")
                print(self.watch_fds[event.wd] + "/" + event.name)
        if event.mask & INFlags.DELETE_SELF:
            # A watched directory was deleted.
            # Delete the watch and all its watched subdirectories
            pass
        if event.mask & INFlags.MOVE_SELF:
            # A watched directory was moved.
            pass
        self.callback(event)
