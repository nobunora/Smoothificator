"""Inspect sliced settings and a strict execution prefix; emits JSON only."""
import argparse
from collections import Counter
from dataclasses import asdict
from fractions import Fraction
import json
from pathlib import Path
import re

from orca_plugin.gcode.linear_trace import trace_linear_execution
from orca_plugin.gcode.source_profile import read_sliced_profile, SourceProfileError


def inspect_source(project, source, *, plate=1):
    profile = read_sliced_profile(project, source, plate=plate)
    trace = trace_linear_execution(source)
    commands = Counter()
    for raw in source.decode("ascii").splitlines():
        match = re.match(r"\s*([GM][0-9]+)", raw.split(";", 1)[0])
        if match:
            commands[match[1]] += 1
    unresolved = ["chronological whole-path support and downstream tool-body clearance",
                  "converged bidirectional surface-error and improvement acceptance",
                  "immutable executable Plan and final anchor/state restoration",
                  "validated firmware-specific formatter and motion/time model",
                  "physical startup/homing and measured nozzle/hotend envelope"]
    if profile.setting("travel_speed_z").number() == 0:
        unresolved.append("travel_speed_z=0: effective Orca travel-Z semantics unresolved")
    if trace.failure is not None:
        unresolved.append("linear execution grammar incomplete for this source")
    if trace.final_state.retraction_debt_mm is None:
        unresolved.append("initial physical retraction debt unknown; G92 E cannot establish it")
    if profile.unconsumed_duplicate_config_keys:
        unresolved.append("duplicate unconsumed configuration keys require full fingerprint review")
    return {"scope": "read-only-print-source-inspection", "printable_authorized": False,
            "project_sha256": profile.project_sha256,
            "source_sha256": profile.source_sha256, "plate_member": profile.plate_member,
            "settings": [asdict(s) for s in profile.settings],
            "unconsumed_duplicate_config_keys": profile.unconsumed_duplicate_config_keys,
            "source_command_counts": dict(sorted(commands.items())),
            "interpreted_prefix_command_count": len(trace.records),
            "trace_failure": None if trace.failure is None else asdict(trace.failure),
            "prefix_final_state": asdict(trace.final_state),
            "unresolved": unresolved}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--plate", type=int, default=1)
    args = parser.parse_args()
    project, source = args.project.read_bytes(), args.source.read_bytes()
    try:
        report = inspect_source(project, source, plate=args.plate)
    except SourceProfileError as exc:
        report = {"scope": "read-only-print-source-inspection", "printable_authorized": False,
                  "unresolved": [str(exc)]}
    # stdout only: the input G-code is never opened for writing or transformed.
    print(json.dumps(report, indent=2, ensure_ascii=False,
                     default=lambda v: str(v) if isinstance(v, Fraction) else v))
    return 2 if report["unresolved"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
