.. image:: https://readthedocs.org/projects/inotify-lite/badge/?version=latest
  :target: https://inotify-lite.readthedocs.io/en/latest/?badge=latest
  :alt: Documentation Status

inotify_lite
=============

``inotify_lite`` provides a Python 3 wrapper around the Linux ``inotify`` API. This lets you monitor filesystem events, and execute callbacks. See ``inotify(7)``.

* homepage_
* documentation_
* `issue tracker`_

Requires
--------

* Linux >= 2.6.13 (or glibc >= 2.5)
* Python >= 3.6

Installation
------------

Install ``inotify_lite`` by running:

    pip install inotify_lite

Usage
-----

To use ``inotify_lite``:

- Create an ``Inotify`` instance, passing the name of the files (or directories) you wish to watch;
- Register a handler (or many), a callable of two arguments:

  + an ``Inotify`` instance; and
  + an ``InotifyEvent`` instance.

- call ``Inotify.read`` to read once, or ``Inotify.watch`` to watch until a keyboard interrupt is received.

Examples:

.. code-block:: python

    def my_callback(_, event):
        print(event.name)
        print(event.mask)

    flags = INFlags.CREATE | INFlags.DELETE
    watcher = Inotify("/home/", watch_flags=flags)
    watcher.register_handler(INFlags.ALL_FLAGS, my_callback, exclusive=False)
    watcher.watch()

.. code-block:: python

    def my_callback(_, event):
        print(event.name)
        print(event.mask)

    watcher = TreeWatcher("/home/", watch_flags=INFlags.OPEN, timeout=10)
    # Watch the home directory for OPEN events with a 10 second timeout.

    watcher.register_handler(INFlags.ALL_FLAGS, my_callback, exclusive=False)
    watcher.read_once()

The ``TreeWatcher`` class is provided to recursively watch directories.

See the documentation_ for details and options.

Contribute
----------

Contributions are welcome. Open an issue_ for visibility.

To install the dev requirements run ``python setup.py -e .[dev]``.

To run the tests run ``make test``.

Code should be formatted with black.

* Issue Tracker: https://github.com/jams2/inotify_lite/issues
* Source Code: https://github.com/jams2/inotify_lite.git

Support
-------

Open an issue_.


License
-------

The project is licensed under GPLv3.

.. _inotify_lite: https://github.com/jams2/inotify_lite
.. _homepage: https://github.com/jams2/inotify_lite
.. _documentation: https://inotify-lite.readthedocs.io
.. _`issue tracker`: https://github.com/jams2/inotify_lite/issues
.. _issue : https://github.com/jams2/inotify_lite/issues
