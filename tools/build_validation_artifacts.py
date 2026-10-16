"""Build a non-installable research ZIP and a separate diagnostic .py package."""

import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo


def main():
    root = Path(__file__).resolve().parents[1]
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
    paths = sorted(path for package in ("adaptive_subedge", "orca_plugin")
                   for path in (root / package).rglob("*.py"))
    if [path.relative_to(root).as_posix() for path in paths if path.is_relative_to(root / "orca_plugin")] != ["orca_plugin/__init__.py"]:
        raise RuntimeError("Phase 0.5 must not contain runnable Orca capabilities")
    dist = root / "dist"
    dist.mkdir(exist_ok=True)
    archive_path = dist / "phase05-research-only.zip"
    disclaimer = ("NOT an installable OrcaSlicer plugin. No callbacks or injection.\n"
                  f"Source checkout HEAD: {commit}\n")
    members = {"RESEARCH-ONLY.txt": disclaimer.encode()}
    members.update({path.relative_to(root).as_posix(): path.read_bytes() for path in paths})
    with ZipFile(archive_path, "w") as archive:
        for name, content in sorted(members.items()):
            info = ZipInfo(name, date_time=(2026, 1, 1, 0, 0, 0))
            info.compress_type = ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            archive.writestr(info, content)
    with tempfile.TemporaryDirectory() as temporary:
        with ZipFile(archive_path) as archive:
            assert archive.testzip() is None
            assert len(archive.namelist()) == len(set(archive.namelist()))
            for name, content in members.items():
                assert archive.read(name) == content
            archive.extractall(temporary)
        # A new isolated interpreter cannot accidentally import the checkout.
        subprocess.run([sys.executable, "-I", "-c",
                        "import sys,pathlib; sys.path.insert(0,sys.argv[1]); "
                        "import adaptive_subedge.application.serialization as s; import orca_plugin; "
                        "import adaptive_subedge.engine.support_cell as support; "
                        "import adaptive_subedge.engine.support_coverage as coverage; "
                        "import adaptive_subedge.engine.mesh_topology as topology; "
                        "assert pathlib.Path(s.__file__).is_relative_to(sys.argv[1]); "
                        "assert pathlib.Path(support.__file__).is_relative_to(sys.argv[1]); "
                        "assert pathlib.Path(coverage.__file__).is_relative_to(sys.argv[1]); "
                        "assert pathlib.Path(topology.__file__).is_relative_to(sys.argv[1]); "
                        "assert pathlib.Path(orca_plugin.__file__).is_relative_to(sys.argv[1])",
                        temporary], cwd=temporary, check=True)
    probe = root / "diagnostics/smoothificator_readonly_probe.py"
    probe_output = dist / probe.name
    probe_output.write_bytes(probe.read_bytes())
    manifest = {"source_checkout_head": commit,
                "research_zip_is_installable_plugin": False,
                "probe_is_analysis_engine": False,
                "probe_target_source": "86905a8a20d5887f3b13017e66cd897766334bd3",
                "artifacts": {path.name: {"sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                                         "bytes": path.stat().st_size}
                              for path in (archive_path, probe_output)}}
    (dist / "validation-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
