from types import SimpleNamespace

from yhttp.core.fswatcher import FSWatcher


def _modify(fn):
    with open(fn, 'w+') as f:
        f.write('\n')


def test_watcher(mktmptree, chdir):
    fs = mktmptree({
        'foo': {
            'bar.txt': 'bar bar bar',
            'baz': {
                'qux.txt': 'qux',
                'quux.txt': 'quux',
                'thud': {
                    'corge.txt': 'corge',
                    'foo.md': 'foo',
                },
            },
        }
    })

    with chdir(fs):
        w = FSWatcher(
            directories=['foo/**', 'notexists'],
            files=['**/thud/*.md'],
            excludefiles=['**/quux.txt'],
            excludedirectories=['**/thud'],
        )
        w.start()
        _modify(f'{fs}/foo/bar.txt')
        assert w.wait()
        assert not w.wait()

        _modify(f'{fs}/foo/baz/qux.txt')
        assert w.wait()

        _modify(f'{fs}/foo/baz/quux.txt')
        assert not w.wait()

        _modify(f'{fs}/foo/baz/thud/corge.txt')
        assert not w.wait()

        _modify(f'{fs}/foo/baz/thud/foo.md')
        assert w.wait()

        w.stop()
        _modify(f'{fs}/foo/baz/qux.txt')
        assert not w.wait()

        w.close()


def test_moved_event_reports_watched_destination(tmp_path):
    watched_file = tmp_path / 'watched.txt'
    w = FSWatcher(files=[str(watched_file)])
    w._watchfiles.add(str(watched_file))
    event = SimpleNamespace(
        event_type='moved', src_path=str(tmp_path / 'old.txt'),
        dest_path=str(watched_file),
    )

    assert w._event_paths(event) == {str(watched_file)}


def test_wait_collects_event_until_timeout(monkeypatch, tmp_path):
    watched_file = tmp_path / 'watched.txt'
    w = FSWatcher(files=[str(watched_file)])
    w._watchfiles.add(str(watched_file))
    w._events.put(SimpleNamespace(
        event_type='modified', src_path=str(watched_file),
    ))
    # Start before the deadline, then report that the event arrived after it.
    ticks = iter((0, 0.001, 0.006))
    monkeypatch.setattr(
        'yhttp.core.fswatcher.time.monotonic',
        lambda: next(ticks)
    )

    assert w.wait(timeout=5) == {str(watched_file)}
