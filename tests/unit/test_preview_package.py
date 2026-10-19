"""Inspect real wheel bytes built from a small isolated source tree."""
import base64
import csv
from email.parser import BytesParser
import hashlib
import io
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from zipfile import ZipFile

from tools.build_preview_plugin import AUDIT_MANIFEST, DIST_INFO, WHEEL_NAME, build_wheel


class PreviewPackageTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        sources = {
            "adaptive_subedge/__init__.py": b"",
            "adaptive_subedge/engine/example.py": b"VALUE = 1\n",
            "smoothificator_preview/__init__.py": b"from . import plugin\n",
            "smoothificator_preview/plugin.py": b"# fixture entry\n",
            "adaptive_subedge/__pycache__/excluded.py": b"# cache\n",
            "adaptive_subedge/private.json": b"{}",
            "tests/private_test.py": b"# not distributable\n",
            "diagnostics/private.py": b"# not distributable\n",
            ".env": b"PRIVATE=fixture\n",
            "LICENSE": b"Fixture license\n",
            AUDIT_MANIFEST: b'{"fixture":true}\n',
        }
        for relative, content in sources.items():
            target = self.root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(content)

    def wheel(self):
        return build_wheel(self.root, self.root / "output")

    def test_metadata_and_explicit_import_name(self):
        wheel = self.wheel()
        self.assertEqual(wheel.name, WHEEL_NAME)
        with ZipFile(wheel) as archive:
            metadata = BytesParser().parsebytes(archive.read(f"{DIST_INFO}/METADATA"))
            for field, expected in (("Name", "smoothificator-preview"),("Version", "0.3.1"),
                                    ("Import-Name", "smoothificator_preview"),("Requires-Python", ">=3.12"),
                                    ("Requires-Dist", "numpy==2.2.6"),("License-File", "LICENSE")):
                self.assertEqual(metadata[field], expected)
            self.assertIn(b"Tag: py3-none-any", archive.read(f"{DIST_INFO}/WHEEL"))
            self.assertEqual(archive.read(f"{DIST_INFO}/licenses/LICENSE"), b"Fixture license\n")

    def test_allowlist_and_deterministic_bytes(self):
        first = self.wheel().read_bytes()
        second = self.wheel().read_bytes()
        self.assertEqual(first, second)
        with ZipFile(io.BytesIO(first)) as archive:
            expected_sources = {"adaptive_subedge/__init__.py", "adaptive_subedge/engine/example.py",
                                "smoothificator_preview/__init__.py", "smoothificator_preview/plugin.py"}
            expected_metadata = {f"{DIST_INFO}/{name}" for name in
                                 ("METADATA", "WHEEL", "RECORD", "provenance.json", "licenses/LICENSE")}
            self.assertEqual(set(archive.namelist()), expected_sources | expected_metadata)
            self.assertEqual(archive.namelist(), sorted(archive.namelist()))
            self.assertTrue(all(entry.date_time == (1980,1,1,0,0,0) for entry in archive.infolist()))

    def test_record_hashes_lengths_and_manifest_provenance(self):
        with ZipFile(self.wheel()) as archive:
            record_name = f"{DIST_INFO}/RECORD"
            rows = list(csv.reader(io.StringIO(archive.read(record_name).decode())))
            self.assertEqual({row[0] for row in rows}, set(archive.namelist()))
            self.assertEqual(len(rows), len(archive.namelist()))
            for name, digest, size in rows:
                if name == record_name:
                    self.assertEqual((digest,size),("",""))
                    continue
                content = archive.read(name)
                encoded = base64.urlsafe_b64encode(hashlib.sha256(content).digest()).rstrip(b"=").decode()
                self.assertEqual(digest, "sha256="+encoded)
                self.assertEqual(int(size), len(content))
            provenance = json.loads(archive.read(f"{DIST_INFO}/provenance.json"))
            self.assertEqual(provenance["audit_manifest_sha256"], hashlib.sha256((self.root/AUDIT_MANIFEST).read_bytes()).hexdigest())
            for name, digest in provenance["package_source_sha256"].items():
                self.assertEqual(digest, hashlib.sha256(archive.read(name)).hexdigest())

    def test_missing_entry_fails_before_output_creation(self):
        (self.root / "smoothificator_preview/__init__.py").unlink()
        with self.assertRaisesRegex(ValueError,"missing package entry"):
            self.wheel()
        self.assertFalse((self.root / "output").exists())


if __name__ == "__main__":
    unittest.main()
