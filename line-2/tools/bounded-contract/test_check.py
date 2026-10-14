"""Meaningful reader-boundary and CLI regressions; fixtures stay in test/scratch."""
import contextlib
import importlib.util
import io
import json
import os
import unittest
from pathlib import Path
from unittest.mock import patch

HERE = Path(__file__).absolute().parent
spec = importlib.util.spec_from_file_location('bounded_contract', HERE / 'check.py')
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


class Boundary(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import tempfile
        Path('test/scratch').mkdir(parents=True, exist_ok=True)
        cls.tmp = tempfile.TemporaryDirectory(prefix='bounded-', dir='test/scratch')
        cls.root = Path(cls.tmp.name).relative_to(Path.cwd()) if Path(cls.tmp.name).is_absolute() else Path(cls.tmp.name)
        (cls.root / 'good.json').write_text('{"ok":true}')
        (cls.root / 'bad.json').write_text('{"ok":"yes","extra":1}')
        (cls.root / 'contract.json').write_text(json.dumps({
            'type': 'object', 'required': ['ok'], 'additionalProperties': False,
            'properties': {'ok': {'type': 'boolean'}}}))

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def file(self, name):
        return (self.root / name).as_posix()

    def run_cli(self, *documents):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = checker.main([self.file('contract.json'), *documents])
        return code, json.loads(output.getvalue())

    def test_real_records(self):
        engine = checker.engine_module()
        contract = engine.prepare(checker.load(
            'line-2/tools/ordered-deliverables/record.strict.contract.json'))
        for number in ('01', '22', '23'):
            self.assertEqual(engine.validate(checker.load(f'dist/line-2/{number}.json'), contract), [])

    def test_exact_limit_and_over_limit(self):
        (self.root / 'bytes').write_bytes(b'a' * 8)
        self.assertEqual(checker.read_bytes(self.file('bytes'), 8), b'a' * 8)
        with self.assertRaises(ValueError):
            checker.read_bytes(self.file('bytes'), 7)
        (self.root / 'empty').write_bytes(b'')
        self.assertEqual(checker.read_bytes(self.file('empty'), 0), b'')

    def test_growth_after_fstat_is_bounded(self):
        # A reader cannot rely on the earlier file size: emulate a growing file.
        requested = []
        def growing(fd, count):
            requested.append(count)
            return b'x' * count
        with patch.object(checker.os, 'read', side_effect=growing):
            with self.assertRaises(ValueError):
                checker.read_bytes(self.file('good.json'), 100)
        self.assertEqual(sum(requested), 101)

    def test_short_reads_are_joined(self):
        with patch.object(checker.os, 'read', side_effect=[b'{', b'}', b'']):
            self.assertEqual(checker.read_bytes(self.file('good.json'), 100), b'{}')

    def test_paths_refused_without_open(self):
        for name in ('/etc/passwd', '../x', '.git/config', 'a/../b',
                     'a/.hidden/b', 'a//b', './a', 'a/', ''):
            with self.subTest(name=name), patch.object(checker.os, 'open') as opening:
                with self.assertRaises(ValueError):
                    checker.read_bytes(name)
                opening.assert_not_called()

    def test_symlink_leaf_refused(self):
        (self.root / 'leaf').symlink_to('good.json')
        with self.assertRaises(OSError):
            checker.load(self.file('leaf'))

    def test_symlink_directory_refused(self):
        (self.root / 'linkdir').symlink_to('.', target_is_directory=True)
        with self.assertRaises(OSError):
            checker.load(self.file('linkdir/good.json'))

    def test_fifo_does_not_block(self):
        os.mkfifo(self.root / 'pipe')
        with self.assertRaises(ValueError):
            checker.read_bytes(self.file('pipe'))

    def test_directory_refused(self):
        with self.assertRaises(ValueError):
            checker.read_bytes(self.root.as_posix())

    def test_descriptor_keeps_original_directory(self):
        branch = self.root / 'branch'
        branch.mkdir()
        (branch / 'value').write_bytes(b'original')
        original_open = os.open
        moved = False
        def swapping(path, flags, **kwargs):
            nonlocal moved
            fd = original_open(path, flags, **kwargs)
            if path == 'branch' and not moved:
                moved = True
                branch.rename(self.root / 'oldbranch')
                branch.mkdir()
                (branch / 'value').write_bytes(b'replacement')
            return fd
        with patch.object(checker.os, 'open', side_effect=swapping):
            self.assertEqual(checker.read_bytes(self.file('branch/value')), b'original')

    def test_duplicate_nonfinite_and_utf8(self):
        for i, data in enumerate((b'{"a":1,"a":2}', b'NaN', b'1e999', b'\xff')):
            name = f'malformed{i}'
            (self.root / name).write_bytes(data)
            with self.subTest(data=data), self.assertRaises(ValueError):
                checker.load(self.file(name))

    def test_cli_exit_precedence_and_continuation(self):
        good, bad = self.file('good.json'), self.file('bad.json')
        code, report = self.run_cli(good)
        self.assertEqual(code, 0)
        self.assertTrue(report['valid'])
        code, report = self.run_cli(bad)
        self.assertEqual(code, 1)
        self.assertEqual({e['path'] for e in report['files'][0]['errors']}, {'/ok', '/extra'})
        code, report = self.run_cli(self.file('missing'), bad, good)
        self.assertEqual(code, 2)
        self.assertEqual(report['summary'], {'checked': 3, 'passed': 1, 'failed': 1, 'unreadable': 1})
        self.assertEqual([r['file'] for r in report['files']], [self.file('missing'), bad, good])

    def test_invalid_contract_and_document_count(self):
        (self.root / 'invalid').write_text('{"type":"boolean","minLength":1}')
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(checker.main([self.file('invalid'), self.file('good.json')]), 2)
            self.assertEqual(checker.main([self.file('contract.json')] + ['absent'] * 257), 2)

    def test_fd_cleanup_on_success_and_failure(self):
        original_close = os.close
        for name in (self.file('good.json'), self.file('missing')):
            closed = []
            def close(fd):
                closed.append(fd)
                original_close(fd)
            with patch.object(checker.os, 'close', side_effect=close):
                try:
                    checker.read_bytes(name)
                except OSError:
                    pass
            # Root and each directory descriptor close, even when leaf open fails.
            self.assertGreaterEqual(len(closed), len(name.split('/')))


if __name__ == '__main__':
    unittest.main(verbosity=2)
