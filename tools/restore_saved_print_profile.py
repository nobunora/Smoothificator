"""Restore pinned saved machine programs into a separate offline research slice."""
import argparse
from dataclasses import dataclass
from decimal import Decimal
from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path
import re
import subprocess
from zipfile import BadZipFile, ZipFile

from tools.exponential_top_fixture import ROOT, MODEL_SHA256


SETTINGS_MEMBER = 'Metadata/project_settings.config'
REVOLVED_MODEL_SHA256 = 'b22af0e25a9e29a95e7a3c0f6aa93cf058d5119fa456205c05d62d3c1f89295f'
ORCA_SHA256 = '480b64a3a5e95e3b43ed5ff93f7490af4e57f4e3cf6f19d8c9a4e4b2c9906aba'
OUTPUT_FOLDER = ROOT / 'artifacts/revolved-exponential-execution'


class ProfileRestorationError(ValueError):
    """Saved inputs or execution prerequisites are not the pinned contract."""


@dataclass(frozen=True)
class RestoredSetting:
    key: str
    old_value_sha256: str
    new_value_sha256: str


@dataclass(frozen=True)
class RestoredProfile:
    project_bytes: bytes
    model_sha256: str
    seed_sha256: str
    restored_keys: tuple[str, ...]
    changes: tuple[RestoredSetting, ...]


def _json_bytes(value):
    if type(value) is Decimal:
        if not value.is_finite():
            raise ProfileRestorationError('finite exact JSON number required')
        token = str(value)
        if '.' not in token and 'e' not in token.lower():
            token += '.0'
        return token.encode('ascii')
    if type(value) is dict:
        return b'{'+b','.join(_json_bytes(key)+b':'+_json_bytes(value[key]) for key in sorted(value))+b'}'
    if type(value) in (list, tuple):
        return b'['+b','.join(_json_bytes(member) for member in value)+b']'
    return json.dumps(value, sort_keys=True, ensure_ascii=True, allow_nan=False,
                      separators=(',', ':')).encode('ascii')


def _unique_keys(pairs):
    settings = {}
    for key, value in pairs:
        if key in settings:
            raise ProfileRestorationError(f'duplicate JSON key: {key}')
        settings[key] = value
    return settings


def _reject_constant(value):
    raise ProfileRestorationError(f'nonfinite JSON constant: {value}')


def _read_project(project):
    try:
        with ZipFile(BytesIO(project)) as archive:
            names = archive.namelist()
            if len(names) != len(set(names)):
                raise ProfileRestorationError('duplicate ZIP member')
            if any(name.lower().endswith('.gcode') for name in names):
                raise ProfileRestorationError('already-sliced project contains G-code')
            if SETTINGS_MEMBER not in names:
                raise ProfileRestorationError('missing saved project settings')
            settings = json.loads(archive.read(SETTINGS_MEMBER), object_pairs_hook=_unique_keys,
                                  parse_constant=_reject_constant, parse_float=Decimal)
            if type(settings) is not dict:
                raise ProfileRestorationError('saved settings object required')
            for key, value in settings.items():
                if 'postprocess' in key.lower().replace('_', '').replace('-', ''):
                    if not (type(value) is str and value == '' or type(value) is list and value == []):
                        raise ProfileRestorationError(f'external postprocessing unsupported: {key}')
            return settings
    except (BadZipFile, json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise ProfileRestorationError('malformed saved project') from exc


def restore_saved_profile(model: bytes, seed: bytes, *, expected_model_sha256: str,
                          expected_seed_sha256: str) -> RestoredProfile:
    """Pure bytes transformation; transfer every saved *_gcode JSON value/type."""
    if type(model) is not bytes or type(seed) is not bytes:
        raise ProfileRestorationError('exact project bytes required')
    model_hash, seed_hash = sha256(model).hexdigest(), sha256(seed).hexdigest()
    if model_hash != expected_model_sha256 or seed_hash != expected_seed_sha256:
        raise ProfileRestorationError('stale model/seed hash pin')
    settings, saved = _read_project(model), _read_project(seed)
    keys = tuple(sorted(key for key in saved if key.endswith('_gcode')))
    if not keys or set(key for key in settings if key.endswith('_gcode')) != set(keys):
        raise ProfileRestorationError('saved/model machine-program key sets differ')
    changes = []
    for key in keys:
        old, new = _json_bytes(settings[key]), _json_bytes(saved[key])
        if old != new:
            changes.append(RestoredSetting(key, sha256(old).hexdigest(), sha256(new).hexdigest()))
        settings[key] = saved[key]
    output = BytesIO()
    with ZipFile(BytesIO(model)) as original, ZipFile(output, 'w') as restored:
        restored.comment = original.comment
        for entry in original.infolist():
            restored.writestr(entry, _json_bytes(settings) if entry.filename == SETTINGS_MEMBER
                              else original.read(entry.filename))
    content = output.getvalue()
    with ZipFile(BytesIO(model)) as original, ZipFile(BytesIO(content)) as restored:
        for name in original.namelist():
            if name != SETTINGS_MEMBER and original.read(name) != restored.read(name):
                raise ProfileRestorationError('non-settings member changed')
    return RestoredProfile(content, model_hash, seed_hash, keys, tuple(changes))


def validate_output_paths(model_path: Path, seed_path: Path, output_path: Path):
    """No input/output aliases, including resolved symlinks and hardlinks."""
    for original in (model_path, seed_path):
        if output_path.resolve() == original.resolve() or (
                output_path.exists() and original.exists() and output_path.samefile(original)):
            raise ProfileRestorationError('input/output path alias')


def _hashes(paths):
    return {str(path.relative_to(ROOT)): sha256(path.read_bytes()).hexdigest() for path in paths}


def command_inventory(source: bytes):
    """Count lexical opcodes including manufacturer decimal subcommands.

    This does not interpret parameters or certify any command's semantics.
    """
    inventory = {}
    for raw in source.splitlines():
        text = raw.decode('ascii').split(';', 1)[0].strip()
        if not text:
            continue
        match = re.match(r'([GMT][0-9]+(?:\.[0-9]+)?)(?=\s|[A-Z]|$)', text)
        opcode = match[1] if match else 'UNRECOGNIZED'
        inventory[opcode] = inventory.get(opcode, 0) + 1
    return inventory


def run_offline_baseline():
    """One new research folder only; pinned offline slice, never send/connect."""
    model_path = ROOT / 'artifacts/revolved-exponential-review/revolved-exponential.3mf'
    seed_path = ROOT / 'artifacts/fixtures/offline-coupon.3mf'
    executable = ROOT / 'artifacts/runtime/orca-nightly/OrcaSlicer/orca-slicer.exe'
    target = OUTPUT_FOLDER / 'restored-unsliced.3mf'
    validate_output_paths(model_path, seed_path, target)
    executable_hash = sha256(executable.read_bytes()).hexdigest()
    if executable_hash != ORCA_SHA256:
        raise ProfileRestorationError('stale offline Orca executable pin')
    restored = restore_saved_profile(model_path.read_bytes(), seed_path.read_bytes(),
        expected_model_sha256=REVOLVED_MODEL_SHA256, expected_seed_sha256=MODEL_SHA256)
    review = model_path.parent
    preserved_paths = [model_path, seed_path, executable, review / 'current-review.json',
                       review / 'original-slice/plate_1.gcode', review / 'original-slice/sliced.3mf']
    preserved_paths.extend(sorted(review.glob('*.UNVERIFIED_VIEW_ONLY.gcode')))
    preserved_before = _hashes(preserved_paths)
    OUTPUT_FOLDER.mkdir(exist_ok=False)
    target.write_bytes(restored.project_bytes)
    sliced = OUTPUT_FOLDER / 'original-slice'
    sliced.mkdir()
    command = [str(executable), '--slice', '0', '--orient', '0', '--arrange', '0',
               '--export-3mf', 'sliced.3mf', '--datadir', str(OUTPUT_FOLDER / 'cli-profile'),
               '--outputdir', str(sliced), str(target)]
    receipt = {'printable_authorized': False, 'physical_print_authorized': False,
        'execution_verified': False, 'executable_sha256': executable_hash,
        'input_model_sha256': restored.model_sha256, 'seed_sha256': restored.seed_sha256,
        'restored_unsliced_sha256': sha256(restored.project_bytes).hexdigest(),
        'restored_keys': restored.restored_keys,
        'changed_keys': [change.__dict__ for change in restored.changes],
        'command': command, 'preserved_inputs_before': preserved_before}
    receipt_path = OUTPUT_FOLDER / 'restoration-receipt.json'
    receipt_path.write_bytes(_json_bytes(receipt) + b'\n')
    try:
        run = subprocess.run(command, cwd=OUTPUT_FOLDER, capture_output=True, timeout=180)
    except subprocess.TimeoutExpired as exc:
        (OUTPUT_FOLDER / 'slice-stdout.log').write_bytes(exc.stdout or b'')
        (OUTPUT_FOLDER / 'slice-stderr.log').write_bytes(exc.stderr or b'')
        receipt.update(slice_timed_out=True, preserved_inputs_after=_hashes(preserved_paths))
        receipt['inputs_unchanged'] = receipt['preserved_inputs_after'] == preserved_before
        receipt_path.write_bytes(_json_bytes(receipt) + b'\n')
        raise ProfileRestorationError('offline slicing timed out') from exc
    (OUTPUT_FOLDER / 'slice-stdout.log').write_bytes(run.stdout)
    (OUTPUT_FOLDER / 'slice-stderr.log').write_bytes(run.stderr)
    receipt['slice_returncode'] = run.returncode
    receipt['preserved_inputs_after'] = _hashes(preserved_paths)
    receipt['inputs_unchanged'] = receipt['preserved_inputs_after'] == preserved_before
    receipt_path.write_bytes(_json_bytes(receipt) + b'\n')
    if run.returncode != 0 or not receipt['inputs_unchanged']:
        raise ProfileRestorationError('offline slicing failed or original inputs changed')
    source = (sliced / 'plate_1.gcode').read_bytes()
    with ZipFile(sliced / 'sliced.3mf') as archive:
        names = archive.namelist()
        if len(names) != len(set(names)) or archive.read('Metadata/plate_1.gcode') != source:
            raise ProfileRestorationError('sliced embedded/separate G-code association failed')
    header = source.splitlines()[:40]
    receipt.update(source_slice_sha256=sha256(source).hexdigest(),
        sliced_project_sha256=sha256((sliced / 'sliced.3mf').read_bytes()).hexdigest(),
        embedded_source_matches=True, generated_header=[raw.decode('ascii') for raw in header],
        command_inventory=command_inventory(source), non_settings_members_unchanged=True,
        unresolved='Expanded command inventory is not firmware execution/support/clearance proof.')
    receipt_path.write_bytes(_json_bytes(receipt) + b'\n')
    return receipt


def main():
    argparse.ArgumentParser(description=__doc__).parse_args()
    receipt = run_offline_baseline()
    print(json.dumps({'receipt': str(OUTPUT_FOLDER / 'restoration-receipt.json'),
                      'printable_authorized': False,
                      'source_slice_sha256': receipt['source_slice_sha256']}))


if __name__ == '__main__':
    main()
