"""Offline adversarial tests. Fixtures stay under workspace test/scratch."""
import json
import os
from pathlib import Path
import runpy
import shutil
import unittest
from unittest.mock import patch

SAFE = runpy.run_path('line-1/tools/safe-snapshot-files/safe_files.py')
BOUNDED = runpy.run_path('line-1/tools/bounded-rpc-snapshot/snapshot.py')
ANCHORED = runpy.run_path('line-1/tools/anchored-zto-snapshot/anchored.py')

class BoundaryTests(unittest.TestCase):
    def setUp(self):
        self.area = Path('test/scratch/safe-files-' + str(os.getpid()))
        self.area.mkdir(parents=True, exist_ok=False)

    def tearDown(self):
        shutil.rmtree(self.area)

    def test_saved_real_zto_evidence(self):
        snapshot = BOUNDED['verify_snapshot']('line-1/tools/bounded-rpc-snapshot/sample-zto-supply.json')
        self.assertEqual(snapshot['request']['params'][0]['to'], BOUNDED['ZTO'])
        result = ANCHORED['verify']('line-1/tools/anchored-zto-snapshot/sample.json')
        self.assertEqual(result['zto_total_supply_raw'], 10**27)

    def test_unsafe_lexical_paths(self):
        for raw in ['', '/tmp/x', '../x', 'test/../x', './x', 'test//x', '.imd/x', 'test/.key', 'test/']:
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                SAFE['parts'](raw)

    def test_input_limit_actual_bytes(self):
        p = self.area / 'sample.json'
        p.write_bytes(b'abcd')
        self.assertEqual(SAFE['read_bytes'](p, 4), b'abcd')
        with self.assertRaises(ValueError):
            SAFE['read_bytes'](p, 3)

    def test_empty_limit(self):
        p = self.area / 'empty'
        p.write_bytes(b'')
        self.assertEqual(SAFE['read_bytes'](p, 0), b'')
        p.write_bytes(b'x')
        with self.assertRaises(ValueError):
            SAFE['read_bytes'](p, 0)

    def test_invalid_limits(self):
        for limit in [-1, True, 1.5, '2']:
            with self.subTest(limit=limit), self.assertRaises(ValueError):
                SAFE['read_bytes'](self.area / 'none', limit)

    def test_leaf_symlink_read(self):
        target = self.area / 'target'
        target.write_bytes(b'public fixture')
        link = self.area / 'link'
        link.symlink_to('target')
        with self.assertRaises(OSError):
            SAFE['read_bytes'](link, 100)

    def test_directory_symlink(self):
        target = self.area / 'target'
        target.mkdir()
        (target / 'input').write_bytes(b'fixture')
        (self.area / 'alias').symlink_to('target', target_is_directory=True)
        for operation in [lambda: SAFE['read_bytes'](self.area / 'alias/input', 100),
                          lambda: SAFE['write_bytes'](self.area / 'alias/output', b'x', 100)]:
            with self.assertRaises(OSError):
                operation()
        self.assertFalse((target / 'output').exists())

    def test_fifo_refused_without_blocking(self):
        p = self.area / 'fifo'
        os.mkfifo(p)
        with self.assertRaises(ValueError):
            SAFE['read_bytes'](p, 100)

    def test_directory_input(self):
        with self.assertRaises(ValueError):
            SAFE['read_bytes'](self.area, 100)

    def test_nested_write_and_read(self):
        p = self.area / 'new/nested/snapshot.json'
        SAFE['write_bytes'](p, b'{"public":true}', 100)
        self.assertEqual(SAFE['read_bytes'](p, 100), b'{"public":true}')
        self.assertEqual(list(p.parent.iterdir()), [p])

    def test_no_overwrite_regular(self):
        p = self.area / 'existing'
        p.write_bytes(b'ancestor')
        with self.assertRaises(FileExistsError):
            SAFE['write_bytes'](p, b'new', 100)
        self.assertEqual(p.read_bytes(), b'ancestor')
        self.assertEqual(len(list(self.area.iterdir())), 1)

    def test_no_overwrite_symlink_or_hardlink(self):
        p = self.area / 'ancestor'
        p.write_bytes(b'old')
        (self.area / 'sym').symlink_to('ancestor')
        os.link(p, self.area / 'hard')
        for name in ['sym', 'hard']:
            with self.assertRaises(FileExistsError):
                SAFE['write_bytes'](self.area / name, b'new', 100)
        self.assertEqual(p.read_bytes(), b'old')

    def test_output_bound_before_files_created(self):
        with self.assertRaises(ValueError):
            SAFE['write_bytes'](self.area / 'new/output', b'123', 2)
        self.assertFalse((self.area / 'new').exists())

    def test_parent_replacement_does_not_redirect_reader(self):
        parent = self.area / 'original'
        parent.mkdir()
        (parent / 'input').write_bytes(b'original evidence')
        decoy = self.area / 'decoy'
        decoy.mkdir()
        (decoy / 'input').write_bytes(b'wrong evidence')
        original_open = os.open
        def racing_open(name, flags, *args, **kwargs):
            if name == 'input':
                parent.rename(self.area / 'held')
                parent.symlink_to('decoy', target_is_directory=True)
            return original_open(name, flags, *args, **kwargs)
        with patch.object(os, 'open', racing_open):
            self.assertEqual(SAFE['read_bytes'](parent / 'input', 100), b'original evidence')

    def test_parent_replacement_does_not_redirect_writer(self):
        parent = self.area / 'original'
        parent.mkdir()
        decoy = self.area / 'decoy'
        decoy.mkdir()
        original_link = os.link
        def racing_link(src, dst, **kwargs):
            parent.rename(self.area / 'held')
            parent.symlink_to('decoy', target_is_directory=True)
            return original_link(src, dst, **kwargs)
        with patch.object(os, 'link', racing_link):
            SAFE['write_bytes'](parent / 'output', b'public evidence', 100)
        self.assertEqual((self.area / 'held/output').read_bytes(), b'public evidence')
        self.assertFalse((decoy / 'output').exists())

    def test_leaf_replacement_symlink_rejected(self):
        p = self.area / 'input'
        p.write_bytes(b'original')
        (self.area / 'decoy').write_bytes(b'wrong')
        original_open = os.open
        def racing_open(name, flags, *args, **kwargs):
            if name == 'input':
                p.unlink()
                p.symlink_to('decoy')
            return original_open(name, flags, *args, **kwargs)
        with patch.object(os, 'open', racing_open), self.assertRaises(OSError):
            SAFE['read_bytes'](p, 100)

    def test_real_bundle_round_trip(self):
        sample = SAFE['read_bytes']('line-1/tools/anchored-zto-snapshot/sample.json', 100000)
        p = self.area / 'roundtrip.json'
        BOUNDED['write_snapshot'](p, sample.decode())
        self.assertEqual(ANCHORED['verify'](str(p))['zto_total_supply_raw'], 10**27)

    def test_checksum_tampering_still_rejected(self):
        raw = SAFE['read_bytes']('line-1/tools/anchored-zto-snapshot/sample.json', 100000)
        value = json.loads(raw)
        value['reads'][2]['response']['result'] = '0x' + '0'*64
        p = self.area / 'tampered.json'
        SAFE['write_bytes'](p, json.dumps(value).encode(), 100000)
        with self.assertRaises(ANCHORED['BundleError']):
            ANCHORED['verify'](str(p))

    def test_snapshot_integrations_refuse_symlinks(self):
        # These are intentionally workspace-local fixture links; no outside input is read.
        for verify in [BOUNDED['verify_snapshot'], ANCHORED['verify']]:
            link = self.area / 'sample'
            link.symlink_to('missing')
            with self.assertRaises(OSError):
                verify(str(link))
            link.unlink()

if __name__ == '__main__':
    unittest.main(verbosity=2)
