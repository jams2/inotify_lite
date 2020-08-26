[![Documentation Status](https://readthedocs.org/projects/inotify-lite/badge/?version=latest)](https://inotify-lite.readthedocs.io/en/latest/?badge=latest)


# inotify_lite


`inotify_lite` is an interface to the `inotify(7)` C calls, for watching filesystem events. It provides the `Inotify` base class, and a `TreeWatcher` class for watching directories.


## Usage Examples

```python
def my_callback(inotify_instance, event):
print(event.name)
print(INFlags(event.mask))

flags = INFlags.CREATE | INFlags.DELETE
watcher = TreeWatcher("/home/", watch_flags=flags)
watcher.register_handler(INFlags.ALL_FLAGS, my_callback, exclusive=False)
watcher.watch()
```

This will watch for all create and delete events in `/home/` and its subdirectories, printing the name of the relative file and the event mask.
