"""Build the ordinary read-only preview wheel without third-party build tools."""
import argparse
import base64
import csv
import hashlib
import io
import json
import sys
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

VERSION = "0.3.1"
DISTRIBUTION = "smoothificator_preview"
DIST_INFO = f"{DISTRIBUTION}-{VERSION}.dist-info"
WHEEL_NAME = f"{DISTRIBUTION}-{VERSION}-py3-none-any.whl"
PACKAGES = ("adaptive_subedge", "smoothificator_preview")
AUDIT_MANIFEST = "docs/AUDIT_REVISION_2026-10-16.json"


def collect_files(root: Path, calibration_bundle: Path | None = None) -> dict[str, bytes]:
    """Allow only package Python sources and explicit distribution metadata."""
    root = root.resolve()
    files = {}
    for package in PACKAGES:
        directory = root / package
        if not (directory / "__init__.py").is_file():
            raise ValueError(f"missing package entry: {package}/__init__.py")
        for source in sorted(directory.rglob("*.py")):
            relative = source.relative_to(root)
            if "__pycache__" in relative.parts:
                continue
            if any((root.joinpath(*relative.parts[:i])).is_symlink()
                   for i in range(1, len(relative.parts)+1)):
                raise ValueError(f"symlink source is not allowed: {relative.as_posix()}")
            if not source.is_file() or not source.resolve().is_relative_to(root):
                raise ValueError(f"invalid package source: {relative.as_posix()}")
            files[relative.as_posix()] = source.read_bytes()
    files[f"{DIST_INFO}/METADATA"] = (
        "Metadata-Version: 2.4\n"
        "Name: smoothificator-preview\n"
        f"Version: {VERSION}\n"
        "Summary: Preview and frozen experimental calibration file export for pinned OrcaSlicer\n"
        "Import-Name: smoothificator_preview\n"
        "Requires-Python: >=3.12\n"
        "Requires-Dist: numpy==2.2.6\n"
        "License-File: LICENSE\n\n"
        "Preview plus byte-exact prepared experimental file export. No live G-code generation or automatic printing.\n"
    ).encode("utf-8")
    files[f"{DIST_INFO}/WHEEL"] = (
        "Wheel-Version: 1.0\nGenerator: Smoothificator stdlib preview builder\n"
        "Root-Is-Purelib: true\nTag: py3-none-any\n"
    ).encode("utf-8")
    files[f"{DIST_INFO}/licenses/LICENSE"] = (root / "LICENSE").read_bytes()
    manifest_bytes = (root / AUDIT_MANIFEST).read_bytes()
    provenance = {
        "schema_version": 1,
        "scope": "read-only preview and frozen prepared experimental export; no automatic printing",
        "audit_manifest_path": AUDIT_MANIFEST,
        "audit_manifest_sha256": hashlib.sha256(manifest_bytes).hexdigest(),
        "package_source_sha256": {
            name: hashlib.sha256(content).hexdigest()
            for name, content in sorted(files.items()) if name.endswith(".py")
        },
    }
    files[f"{DIST_INFO}/provenance.json"] = (
        json.dumps(provenance, sort_keys=True, indent=2)+"\n"
    ).encode("utf-8")
    if calibration_bundle is not None:
        from smoothificator_preview.calibration_bundle import load_bundle
        content = calibration_bundle.read_bytes()
        bundle = load_bundle(content)
        files["smoothificator_preview/_calibration_bundle.zip"] = content
        provenance["calibration_bundle_sha256"] = bundle.bundle_sha256
        provenance["calibration_manifest_sha256"] = bundle.manifest_sha256
        files[f"{DIST_INFO}/provenance.json"] = (json.dumps(provenance, sort_keys=True, indent=2)+"\n").encode("utf8")
        files["smoothificator_preview/_calibration_bundle_lock.json"] = json.dumps({"bundle_sha256": bundle.bundle_sha256, "manifest_sha256": bundle.manifest_sha256}, sort_keys=True).encode("utf8")
    record = io.StringIO(newline="")
    writer = csv.writer(record, lineterminator="\n")
    for name, content in sorted(files.items()):
        digest = base64.urlsafe_b64encode(hashlib.sha256(content).digest()).rstrip(b"=").decode("ascii")
        writer.writerow((name, f"sha256={digest}", len(content)))
    writer.writerow((f"{DIST_INFO}/RECORD", "", ""))
    files[f"{DIST_INFO}/RECORD"] = record.getvalue().encode("utf-8")
    return files


def build_wheel(root: Path, output_directory: Path, calibration_bundle: Path | None = None) -> Path:
    files = collect_files(root, calibration_bundle)
    output_directory.mkdir(parents=True, exist_ok=True)
    output = output_directory / WHEEL_NAME
    with ZipFile(output, "w", compression=ZIP_DEFLATED, compresslevel=9) as archive:
        for name, content in sorted(files.items()):
            entry = ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            entry.compress_type = ZIP_DEFLATED
            entry.create_system = 3
            entry.external_attr = 0o100644 << 16
            archive.writestr(entry, content, compresslevel=9)
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parents[1] / "dist")
    parser.add_argument("--calibration-bundle", type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    if str(root) not in sys.path:sys.path.insert(0,str(root))
    output = build_wheel(root, args.output_dir, args.calibration_bundle)
    print(f"Built {output.name}: sha256={hashlib.sha256(output.read_bytes()).hexdigest()}")


if __name__ == "__main__":
    main()
