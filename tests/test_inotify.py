import unittest
import os
from functools import wraps
from typing import Callable
from tempfile import NamedTemporaryFile
from inotify_lite import Inotify, INFlags


def with_tempfile(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(instance, *args, **kwargs):
        with NamedTemporaryFile() as fd:
            instance.tmpfile = fd
            return func(instance, *args, **kwargs)

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
    def setUpClass(cls):
        cls.tmpfile = None

    @with_tempfile
    def test_exclusive_event_handled(self):
        handler = CallCountWrapper(stub_func)
        watcher = Inotify(self.tmpfile.name, watch_flags=INFlags.ALL_EVENTS)
        watcher.register_handler(INFlags.OPEN, handler)

        fd = os.open(self.tmpfile.name, os.O_RDONLY)
        os.close(fd)
        watcher.read()
        self.assertEqual(1, handler.counter)
        watcher.teardown()

    @with_tempfile
    def test_inclusive_event_handled(self):
        handler = CallCountWrapper(stub_func)
        watcher = Inotify(self.tmpfile.name, watch_flags=INFlags.OPEN)
        watcher.register_handler(INFlags.ALL_EVENTS, handler, exclusive=False)

        fd = os.open(self.tmpfile.name, os.O_RDONLY)
        os.close(fd)
        watcher.read()
        self.assertEqual(1, handler.counter)
        watcher.teardown()
