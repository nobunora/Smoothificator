"""Integrity gate detects stale, omitted and self-referential canonical inputs."""
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

from tools.check_canonical_manifest import check, git


class ManifestTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        subprocess.run(["git", "init", "-q", str(self.root)], check=True)
        git(self.root, "config", "core.autocrlf", "false")
        self.path = "docs/adr/0001-contract.md"
        self.write(self.path, "contract\n")
        git(self.root, "add", self.path)
        self.manifest = {
            "schema_version": 1, "scope": "test",
            "review_status": "integrity_only_not_implementation_authority",
            "blobs": [{"path": self.path, "git_blob": git(self.root, "hash-object", self.path)}],
        }
        self.stamp()

    def write(self, path, content):
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")

    def stamp(self):
        self.write("manifest.json", json.dumps(self.manifest))
        blob = git(self.root, "hash-object", "manifest.json")
        self.write("handoff.md", f"Manifest Git blob: `{blob}`\n")

    def verify(self):
        return check(self.root, "manifest.json", "handoff.md")

    def test_current_blobs_pass_without_claiming_approval(self):
        self.assertEqual(self.verify(), 1)

    def test_changed_content_rejects_even_when_manifest_reference_matches(self):
        self.write(self.path, "changed contract\n")
        with self.assertRaisesRegex(ValueError, "changed canonical blobs"):
            self.verify()

    def test_wrong_handoff_reference_rejects(self):
        self.write("handoff.md", "Manifest Git blob: `" + "0" * 40 + "`\n")
        with self.assertRaisesRegex(ValueError, "handoff"):
            self.verify()

    def test_added_adr_requires_explicit_manifest_coverage(self):
        self.write("docs/adr/0002-new.md", "new contract\n")
        git(self.root, "add", "docs/adr/0002-new.md")
        with self.assertRaisesRegex(ValueError, "coverage"):
            self.verify()

    def test_duplicate_unsafe_and_recursive_entries_reject(self):
        original = self.manifest["blobs"][0].copy()
        for path in (self.path, "../escape", "manifest.json", "handoff.md", "C:/x"):
            with self.subTest(path=path):
                self.manifest["blobs"] = [original, {"path": path, "git_blob": "0" * 40}]
                self.stamp()
                with self.assertRaisesRegex(ValueError, "duplicate, unsafe or self-referential"):
                    self.verify()

    def test_integrity_manifest_cannot_assert_review_approval(self):
        self.manifest["review_status"] = "SPEC_VALIDATED"
        self.stamp()
        with self.assertRaisesRegex(ValueError, "approval"):
            self.verify()


if __name__ == "__main__":
    unittest.main()
