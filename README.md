# inotify_lite

inotify_lite is a Python 3.8 wrapper around inotify (see `inotify(7)`).

## Usage
### Classes
#### IN_FLAGS
`class IN_FLAGS(enum.IntFlag)`

Wrapper around the underlying C lib flags. See `inotify_add_watch(2)`, `<sys/inotify.h>`, `<bits/inotify.h>`.

-----

#### Event

```python
namedtuple("Event", ("wd", "mask", "cookie", "len", "name"))
```

Maps the underlying `struct inotify_event`. See inotify_add_watch(2).

-----

#### Inotify

```python
Inotify(
	callback: Callable[[Sequence[Event]], Any],
	*files: str,
	blocking: bool = True,
	flags: IN_FLAGS = 0,
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
        all_events: bool = True,
        flags: IN_FLAGS = 0,
)
```

Watch directories. Extends `Inotify` and passes `IN_FLAGS.ONLYDIR` by default (raises if any of `dirs` is not a directory). The `all_events` option means to watch for all filesystem events (this can be quite noisy).

-----

#### FileWatcher

```python
FileWatcher(
        callback: Callable[[Sequence[Event]], Any],
        *files: str,
        blocking: bool = True,
        all_events: bool = True,
        flags: IN_FLAGS = 0,
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
    	print(IN_FLAGS(e.mask))

# Watch the home directory for successful writes.
watcher = TreeWatcher(my_callback, "~", all_events=False, flags=IN_FLAGS.CLOSE_WRITE)
watcher.watch()
```