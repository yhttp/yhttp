import time
from os import path
from glob import glob
import fnmatch

from inotify_simple import INotify, flags


DEFAULT_EXCLUDEDIRECTORIES = [
    '**/__pycache__',
]
DEFAULT_EXCLUDEFILES = [
    '**/.*',
    '**/*~',
    '**/4913',
]


class FSWatcher(INotify):
    def __init__(self, directories=None, files=None, excludedirectories=None,
                 excludefiles=None):
        assert directories or files
        super().__init__(closefd=False)
        self._directorymask = flags.CREATE \
            | flags.DELETE \
            | flags.DELETE_SELF \
            | flags.MOVE_SELF \
            | flags.MOVED_FROM \
            | flags.MOVED_TO \
            | flags.MODIFY

        self._filemask = flags.MODIFY | flags.DELETE_SELF | flags.MOVE_SELF
        self.directories = directories or []
        self.files = files or []
        self._wds = {}

        self.excludedirectories = []
        self.excludedirectories.extend(DEFAULT_EXCLUDEDIRECTORIES)
        if excludedirectories:
            self.excludedirectories.extend(excludedirectories)

        self.excludefiles = []
        self.excludefiles.extend(DEFAULT_EXCLUDEFILES)
        if excludefiles:
            self.excludefiles.extend(excludefiles)

    def _excludedirectory(self, node):
        for pattern in self.excludedirectories:
            if fnmatch.fnmatchcase(node, pattern):
                return True

        return False

    def _excludefile(self, node):
        for pattern in self.excludefiles:
            if fnmatch.fnmatchcase(node, pattern):
                return True

        return False

    def _refine_watches(self):
        self._watchdirectories = set()
        self._watchfiles = set()

        for pattern in self.directories:
            matches = glob(pattern, recursive=True)
            for node in matches:
                if path.isdir(node) and not self._excludedirectory(node):
                    self._watchdirectories.add(node)

        for pattern in self.files:
            matches = glob(pattern, recursive=True)
            for node in matches:
                if path.isfile(node) and not self._excludefile(node):
                    self._watchfiles.add(node)

    def watch(self, node, mask):
        print(f'Adding watch for: {node}')
        wd = self.add_watch(node, mask)
        self._wds[wd] = node

    def start(self):
        self._refine_watches()
        for node in self._watchdirectories:
            self.watch(node, self._directorymask)

        for node in self._watchfiles:
            self.watch(node, self._filemask)

    def stop(self):
        self._readall()
        for wd in self._wds:
            self.rm_watch(wd)

        self._wds = {}

    def close(self):
        self._poller.unregister(self.fileno())
        super().close()

    def wait(self, timeout=0):
        changes = set()
        starttime = None
        while True:
            for e in self.read(timeout):
                # cannot simulate this situation, but I think it's enough to
                # raise error
                if e.wd == -1:  # pragma: no cover
                    raise OSError('INotify event queue overflow')

                # uncomment to debug masks(flags)
                # fl = [f.name for f in flags.from_mask(e.mask)]
                if e.mask & flags.IGNORED:
                    continue

                if not (e.mask & flags.ISDIR) and e.name:
                    fn = path.join(self._wds[e.wd], e.name)
                    if e.name and self._excludefile(fn):
                        continue
                else:
                    fn = self._wds[e.wd]

                changes.add(fn)

            if changes:
                if starttime is None:
                    starttime = time.perf_counter()
                    continue
                timeout -= (time.perf_counter() - starttime) * 1000

            if timeout <= 0:
                break

        return changes
