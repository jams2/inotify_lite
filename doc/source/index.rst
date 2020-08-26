.. inotify_lite documentation master file, created by
   sphinx-quickstart on Sun Aug 23 11:21:34 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

inotify_lite
========================================

``inotify_lite`` is an interface to the ``inotify(7)`` C calls, for watching filesystem events. It provides the ``Inotify`` base class, and a ``TreeWatcher`` class for watching directories.

Usage Examples
==============

.. code-block:: python

      def my_callback(inotify_instance, event):
	print(event.name)
	print(INFlags(event.mask))

      flags = INFlags.CREATE | INFlags.DELETE
      watcher = TreeWatcher("/home/", watch_flags=flags)
      watcher.register_handler(INFlags.ALL_FLAGS, my_callback, exclusive=False)
      watcher.watch()

This will watch for all create and delete events in ``/home/`` and its subdirectories, printing the name of the relative file and the event mask.

API
===

.. toctree::
   :maxdepth: 2

.. automodule:: inotify_lite
   :members:
