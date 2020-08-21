""" Joshua Munn, 2020 (public@elysee-munn.family). With observations of
Kovid Goyal's 2013 calibre implementation (kovid at kovidgoyal.net).
Requires Python >= 3.8
"""
import os
import enum
import sys
from string import Template
from typing import Callable, Sequence, Any
from ctypes import *
from struct import unpack, calcsize
from collections import namedtuple


libc = CDLL("libc.so.6")

prototype = CFUNCTYPE(c_int, use_errno=True)
inotify_init = prototype(("inotify_init", libc))

prototype = CFUNCTYPE(c_int, c_int, use_errno=True)
inotify_init1 = prototype(("inotify_init1", libc), ((1, "flags", 0),))

prototype = CFUNCTYPE(c_int, c_int, c_char_p, c_uint32, use_errno=True)
inotify_add_watch = prototype(
    ("inotify_add_watch", libc), ((1, "fd"), (1, "pathname"), (1, "mask")),
)

prototype = CFUNCTYPE(c_int, c_int, c_int, use_errno=True)
inotify_rm_watch = prototype(("inotify_rm_watch", libc), ((1, "fd"), (1, "wd")))

prototype = CFUNCTYPE(c_ssize_t, c_int, c_void_p, c_size_t, use_errno=True)
read = prototype(("read", libc), ((1, "fd"), (1, "buf"), (1, "count")))


class IN_FLAGS(enum.IntFlag):
    """ See inotify_add_watch(2), <sys/inotify.h>, <bits/inotify.h>.
    """

    NONBLOCK = 0x800
    CLOEXEC = 0x80000
    ACCESS = 0x00000001
    MODIFY = 0x00000002
    ATTRIB = 0x00000004
    CLOSE_WRITE = 0x00000008
    CLOSE_NOWRITE = 0x00000010
    OPEN = 0x00000020
    MOVED_FROM = 0x00000040
    MOVED_TO = 0x00000080
    CREATE = 0x00000100
    DELETE = 0x00000200
    DELETE_SELF = 0x00000400
    MOVE_SELF = 0x00000800
    UNMOUNT = 0x00002000
    Q_OVERFLOW = 0x00004000
    IGNORED = 0x00008000
    CLOSE = CLOSE_WRITE | CLOSE_NOWRITE
    MOVE = MOVED_FROM | MOVED_TO
    ONLYDIR = 0x01000000
    DONT_FOLLOW = 0x02000000
    EXCL_UNLINK = 0x04000000
    MASK_ADD = 0x20000000
    ISDIR = 0x40000000
    ONESHOT = 0x80000000
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


Event = namedtuple("Event", ("wd", "mask", "cookie", "len", "name"))


class Inotify:
    EVENT_FORMAT = "iIIIs"
    LEN_OFFSET = sizeof(c_int) + sizeof(c_uint32) * 2
    EVENT_SIZE = sizeof(c_int) + (sizeof(c_uint32) * 2) + sizeof(c_char_p)
    MAX_READ = 4096
    EVENT_STRUCT_FMT = Template("iIII${name_len}s")

    def __init__(
        self,
        callback: Callable[[Sequence[Event]], Any],
        *files: str,
        blocking: bool = True,
        flags: IN_FLAGS = 0,
    ):
        self.inotify_fd = self._blocking() if blocking else self._non_blocking()
        if self.inotify_fd < 0:
            raise OSError(os.strerror(get_errno()))
        self.callback = callback
        self.flags = flags
        self.watch_fds = {}
        self.files = files
        self._add_watches()

    def _add_watches(self):
        for fname in map(lambda x: os.path.expanduser(x), self.files):
            if not os.path.exists(fname):
                raise FileNotFoundError(fname)
            as_bytes = fname.encode("utf-8")
            watch_fd = inotify_add_watch(
                c_int(self.inotify_fd), c_char_p(as_bytes), c_uint32(self.flags),
            )
            if watch_fd < 0:
                err = os.strerror(get_errno())
                raise OSError(err)
            self.watch_fds[watch_fd] = fname

    def _blocking(self):
        return inotify_init()

    def _non_blocking(self):
        return inotify_init1(self.NONBLOCK)

    def _watch(self):
        buf = create_string_buffer(self.MAX_READ)
        while (n := read(self.inotify_fd, buf, self.MAX_READ)) > 0:
            events = []
            offset = 0
            while offset < n:
                name_len = c_uint32.from_buffer(buf, offset + self.LEN_OFFSET)
                fmt = self.EVENT_STRUCT_FMT.substitute(name_len=name_len.value)
                obj_size = calcsize(fmt)
                events.append(Event(*(unpack(fmt, buf[offset : offset + obj_size]))))
                offset += obj_size
            self.callback(events)

    def _teardown(self):
        for fd, filename in self.watch_fds.items():
            if inotify_rm_watch(self.inotify_fd, fd) < 0:
                print(
                    f"Inotify: got error removing watch fd {fd} ({filename}):",
                    file=sys.stderr,
                )
                print(f">>> {os.strerror(get_errno())}", file=sys.stderr)
        os.close(self.inotify_fd)

    def watch(self):
        try:
            self._watch()
        except KeyboardInterrupt:
            pass
        except Exception as err:
            print("Inotify got unexpected exception:", file=sys.stderr)
            print(err, file=sys.stderr)
        finally:
            self._teardown()


class TreeWatcher(Inotify):
    def __init__(
        self,
        callback: Callable[[Sequence[Event]], Any],
        *dirs: str,
        blocking: bool = True,
        flags: IN_FLAGS = IN_FLAGS.ALL_EVENTS,
    ):
        super().__init__(
            callback, *dirs, blocking=blocking, flags=flags | IN_FLAGS.ONLYDIR
        )


class FileWatcher(Inotify):
    def __init__(
        self,
        callback: Callable[[Sequence[Event]], Any],
        *files: str,
        blocking: bool = True,
        flags: IN_FLAGS = IN_FLAGS.ALL_EVENTS,
    ):
        super().__init__(callback, *files, blocking=blocking, flags=flags)
