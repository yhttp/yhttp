from yhttp.core.fswatcher import FSWatcher


def _modify(fn):
    with open(fn, 'w+') as f:
        f.write('\n')


def test_watcher(mockupfs, changedir):
    fs = mockupfs(foo={
        'bar.txt': 'bar bar bar',
        'baz': {
            'qux.txt': 'qux',
            'quux.txt': 'quux',
            'thud': {
                'corge.txt': 'corge',
                'foo.md': 'foo',
            },
        },
    })

    with changedir(fs):
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
