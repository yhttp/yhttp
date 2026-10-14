import fnmatch
from glob import glob
from os import path
from queue import Empty, Queue
import time

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from .logging import logger


DEFAULT_EXCLUDEDIRECTORIES = [
    '**/__pycache__',
    '**/.*',
    '**/~*',
]
DEFAULT_EXCLUDEFILES = [
    '**/.*',
    '**/*~',
    '**/4913',
]


class _EventHandler(FileSystemEventHandler):
    def __init__(self, watcher):
        self.watcher = watcher

    def on_any_event(self, event):
        if event.event_type not in ('created', 'deleted', 'modified', 'moved'):
            return
        # Watchdog reports a directory modification when an entry inside it
        # changes. Inotify only reported the entry itself for the masks we
        # used, so directory metadata events must not become change results.
        if event.is_directory and event.event_type == 'modified':
            return
        self.watcher._events.put(event)


class FSWatcher:
    def __init__(self, directories=None, files=None, excludedirectories=None,
                 excludefiles=None):
        assert directories or files
        self.directories = directories or []
        self.files = files or []
        self._observer = Observer()
        self._events = Queue()
        self._handler = _EventHandler(self)
        self._watched_directories = set()
        self._watchfiles = set()

        self.excludedirectories = list(DEFAULT_EXCLUDEDIRECTORIES)
        if excludedirectories:
            self.excludedirectories.extend(excludedirectories)

        self.excludefiles = list(DEFAULT_EXCLUDEFILES)
        if excludefiles:
            self.excludefiles.extend(excludefiles)

    def _excludedirectory(self, node):
        return any(fnmatch.fnmatchcase(node, pattern)
                   for pattern in self.excludedirectories)

    def _excludefile(self, node):
        return any(fnmatch.fnmatchcase(node, pattern)
                   for pattern in self.excludefiles)

    def _refine_watches(self):
        self._watched_directories = set()
        self._watchfiles = set()

        for pattern in self.directories:
            for node in glob(pattern, recursive=True):
                if path.isdir(node) and not self._excludedirectory(node):
                    self._watched_directories.add(path.abspath(node))

        for pattern in self.files:
            for node in glob(pattern, recursive=True):
                if path.isfile(node) and not self._excludefile(node):
                    self._watchfiles.add(path.abspath(node))

    def start(self):
        self._refine_watches()
        directories = set(self._watched_directories)
        directories.update(path.dirname(node) for node in self._watchfiles)
        for directory in directories:
            logger.info(f'Adding watch for: {directory}')
            self._observer.schedule(self._handler, directory, recursive=False)
        self._observer.start()

    def stop(self):
        if self._observer.is_alive():
            self._observer.stop()
            self._observer.join()
        self._clear_events()

    def close(self):
        self.stop()

    def _clear_events(self):
        while True:
            try:
                self._events.get_nowait()
            except Empty:
                break

    def _event_paths(self, event):
        paths = [event.src_path]
        if event.event_type == 'moved':
            paths.append(event.dest_path)

        matching = set()
        for node in paths:
            node = path.abspath(node)
            if self._excludefile(node):
                continue
            if node in self._watchfiles:
                matching.add(node)
            if (node in self._watched_directories or path.dirname(node) in
                    self._watched_directories):
                matching.add(node)
        return matching

    def wait(self, timeout=0):
        changes = set()
        deadline = time.monotonic() + max(timeout, 0) / 1000
        # Watchdog delivers notifications asynchronously. A short initial wait
        # lets zero-debounce callers observe events caused just before wait().
        initial_wait = 0.25 if timeout <= 0 else max(timeout, 0) / 1000
        while True:
            if timeout <= 0:
                remaining = initial_wait
            else:
                remaining = max(0, deadline - time.monotonic())
            try:
                event = self._events.get(timeout=remaining)
            except Empty:
                break
            changes.update(self._event_paths(event))
            if changes and timeout > 0 and time.monotonic() >= deadline:
                break
            if changes and timeout <= 0:
                # Drain notifications already queued in this delivery batch.
                continue
        return changes
