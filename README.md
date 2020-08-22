# inotify_lite

inotify_lite is a Python 3.8 wrapper around inotify (see [inotify(7)](https://man7.org/linux/man-pages/man7/inotify.7.html)).

## Usage

`pip install inotify_lite`

### Classes
#### INFlags
```python
class INFlags(enum.IntFlag)
```

Wrapper around the underlying C lib flags. See [inotify_add_watch(2)](https://man7.org/linux/man-pages/man2/inotify_add_watch.2.html), `<sys/inotify.h>`, `<bits/inotify.h>`.

-----

#### Event

```python
namedtuple("Event", ("wd", "mask", "cookie", "len", "name"))
```

Maps the underlying `struct inotify_event`. See [inotify_add_watch(2)](https://man7.org/linux/man-pages/man2/inotify_add_watch.2.html).

-----

#### Inotify

```python
Inotify(
	callback: Callable[[Sequence[Event]], Any],
	*files: str,
	blocking: bool = True,
	flags: INFlags = 0,
)
```

Base class for `TreeWatcher` and `FileWatcher`.

-----

#### TreeWatcher

```python
TreeWatcher(
        callback: Callable[[Sequence[Event]], Any],
        *dirs: str,
        blocking: bool = True,
        flags: INFlags = 0,
)
```

Watch directories. Extends `Inotify` and passes `INFlags.ONLYDIR` by default (raises if any of `dirs` is not a directory).

-----

#### FileWatcher

```python
FileWatcher(
        callback: Callable[[Sequence[Event]], Any],
        *files: str,
        blocking: bool = True,
        flags: INFlags = 0,
)
```

Watch files.

-----

### Examples

To watch a directory:

```python
def my_callback(events):
    # Just show me the event mask.
    for e in events:
    	print(INFlags(e.mask))

# Watch the home directory for successful writes.
watcher = TreeWatcher(my_callback, "~", flags=INFlags.CLOSE_WRITE)
watcher.watch()
```
