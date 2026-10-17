"""Check pinned Git blobs; this is integrity evidence, never review approval."""
import argparse
import json
from pathlib import Path, PurePosixPath
import re
import subprocess


def git(root, *args):
    return subprocess.check_output(
        ["git", "-C", str(root), *args], text=True, stderr=subprocess.PIPE
    ).strip()


def check(root, manifest_path, handoff_path):
    manifest = json.loads((root / manifest_path).read_text(encoding="utf-8"))
    if set(manifest) != {"schema_version", "scope", "review_status", "blobs"}:
        raise ValueError("invalid manifest fields")
    if manifest["schema_version"] != 1 or type(manifest["schema_version"]) is not int:
        raise ValueError("unsupported manifest schema")
    if manifest["review_status"] != "integrity_only_not_implementation_authority":
        raise ValueError("manifest must not assert implementation approval")
    entries = manifest["blobs"]
    if type(entries) is not list or not entries:
        raise ValueError("nonempty blob entries required")
    seen = set()
    failures = []
    for entry in entries:
        if type(entry) is not dict or set(entry) != {"path", "git_blob"}:
            raise ValueError("invalid blob entry")
        path, expected = entry["path"], entry["git_blob"]
        if type(path) is not str or type(expected) is not str:
            raise ValueError("string path/blob required")
        relative = PurePosixPath(path)
        if (relative.is_absolute() or ".." in relative.parts or "\\" in path
                or ":" in path or path in seen or path in (manifest_path, handoff_path)):
            raise ValueError("duplicate, unsafe or self-referential path")
        if not re.fullmatch(r"[0-9a-f]{40}", expected):
            raise ValueError("invalid Git blob ID")
        seen.add(path)
        git(root, "ls-files", "--error-unmatch", "--", path)
        actual = git(root, "hash-object", "--path=" + path, "--", path)
        if actual != expected:
            failures.append(path)
    actual_adrs = set(git(root, "ls-files", "docs/adr/[0-9]*.md").splitlines())
    if {p for p in seen if p.startswith("docs/adr/")} != actual_adrs:
        raise ValueError("ADR manifest coverage differs from tracked ADRs")
    numbers = sorted(int(PurePosixPath(p).name[:4]) for p in actual_adrs)
    if numbers != list(range(1, len(numbers) + 1)):
        raise ValueError("ADR IDs must be unique and contiguous")
    handoff = (root / handoff_path).read_text(encoding="utf-8")
    manifest_blob = git(root, "hash-object", "--path=" + manifest_path, "--", manifest_path)
    if f"Manifest Git blob: `{manifest_blob}`" not in handoff:
        raise ValueError("handoff does not pin actual manifest blob")
    if failures:
        raise ValueError("changed canonical blobs: " + ", ".join(failures))
    return len(entries)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", default="docs/AUDIT_REVISION_2026-10-16.json")
    parser.add_argument("--handoff", default="docs/specs/phase05-settings-v2.md")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    try:
        count = check(root, args.manifest, args.handoff)
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        parser.exit(1, f"FAIL: {error}\n")
    print(f"PASS: {count} canonical Git blobs; integrity only, not review approval")
