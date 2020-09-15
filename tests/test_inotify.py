import os
import unittest
from functools import wraps
from typing import Callable
from tempfile import NamedTemporaryFile, TemporaryDirectory
from inotify_lite import Inotify, TreeWatcher, INFlags


def with_tempfile(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(instance, *args, **kwargs):
        with NamedTemporaryFile() as fd:
            instance.tmpfile = fd
            result = func(instance, *args, **kwargs)
        return result

    return wrapper


def with_tempdir(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(instance, *args, **kwargs):
        with TemporaryDirectory() as dirname:
            instance.tmpdir_name = dirname
            result = func(instance, *args, **kwargs)
        return result

    return wrapper


def stub_func(*_):
    pass


class CallCountWrapper:
    def __init__(self, func: Callable):
        self.func = func
        self.counter = 0

    def __call__(self, *args, **kwargs):
        self.counter += 1
        self.func(*args, **kwargs)


class TestInotify(unittest.TestCase):
    @classmethod
    def setupClass(cls):
        cls.tmpfile = None
        cls.tmpdir_name = None

    @with_tempfile
    def test_exclusive_event_handled(self):
        handler = CallCountWrapper(stub_func)
        watcher = Inotify(self.tmpfile.name, watch_flags=INFlags.ALL_EVENTS)
        watcher.register_handler(INFlags.OPEN, handler)

        fd = os.open(self.tmpfile.name, os.O_RDONLY)
        os.close(fd)
        watcher.read_once()
        self.assertEqual(1, handler.counter)
        watcher.teardown()

    @with_tempfile
    def test_inclusive_event_handled(self):
        handler = CallCountWrapper(stub_func)
        watcher = Inotify(self.tmpfile.name, watch_flags=INFlags.OPEN)
        watcher.register_handler(INFlags.ALL_EVENTS, handler, exclusive=False)

        fd = os.open(self.tmpfile.name, os.O_RDONLY)
        os.close(fd)
        watcher.read_once()
        self.assertEqual(1, handler.counter)
        watcher.teardown()

    @with_tempdir
    def test_inclusive_directory_event(self):
        handler = CallCountWrapper(stub_func)
        watcher = TreeWatcher(self.tmpdir_name, watch_subdirs=False)
        watcher.register_handler(INFlags.ISDIR | INFlags.OPEN, handler, exclusive=True)
        fd = os.open(self.tmpdir_name, os.O_RDONLY)
        os.close(fd)
        watcher.read_once()
        self.assertEqual(1, handler.counter)
        watcher.teardown()

    @with_tempfile
    def test_timeout(self):
        watcher = Inotify(self.tmpfile.name, watch_flags=INFlags.OPEN, timeout=0.1)
        bytes_read = watcher.read_once()
        self.assertEqual(0, bytes_read)
        watcher.teardown()
