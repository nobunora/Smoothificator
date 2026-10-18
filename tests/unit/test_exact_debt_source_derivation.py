"""Exact source repayment is explicit, pinned, bounded and separately published."""
from dataclasses import replace
from fractions import Fraction as F
from hashlib import md5, sha256
from io import BytesIO
import json
from pathlib import Path
import tempfile
import unittest
from zipfile import ZipFile

from tests.unit.test_conditional_nominal_copy import conditional_fixture
from tests.unit.test_conditional_nominal_actual import actual_inputs
from tools.conditional_nominal_body import pin_nominal_producer, interpret_nominal_body
from tools.derive_exact_debt_source import ExactDebtDerivationPolicy, derive_exact_debt_source, write_exact_debt_source
from tools.derive_exact_debt_source import ReviewedOrdinaryRestoreFamily, ReviewedOrdinaryRestore, ReviewedNegativeRetraction


POLICY = ExactDebtDerivationPolicy(4000000, 3000000, 1000000, 30000000, 100000, 1000, 4096, 5)
BODY = (b'M624 AQAAAAAAAAA=\r\nG1 X1 Y2 Z3 F6000\n'
        b'G1 E-.8 F1800\r\nG1 E.8 F1800 ; ordinary restore\n'
        b'G1 X2 Y2 E.1 F6000\r\nM625\n')


def fixture(body=BODY, *, settings_changes=None, checksum=None, entry_debt=F(0)):
    source, project, producer, descriptor, entry, motion = conditional_fixture(body)
    with ZipFile(BytesIO(project)) as archive:
        settings = json.loads(archive.read('Metadata/project_settings.config'))
        settings.update(retraction_length=['0.8'], retraction_speed=['30'], deretraction_speed=['30'],
            retract_restart_extra_toolchange=['0'], filament_retract_restart_extra_toolchange=['nil'])
        settings.update(settings_changes or {})
        lines = source.splitlines(keepends=True)
        config = False
        consumed = set()
        for i, raw in enumerate(lines):
            if raw.strip() == b'; CONFIG_BLOCK_START':
                config = True
            elif raw.strip() == b'; CONFIG_BLOCK_END':
                extra = b''.join(('; '+k+' = '+(','.join(v) if type(v) is list else v)+'\n').encode()
                                 for k, v in settings.items() if k not in consumed)
                lines[i] = extra+raw
                config = False
            elif config and raw.startswith(b'; ') and b' = ' in raw:
                key = raw[2:].split(b' = ', 1)[0].decode()
                if key in settings:
                    v = settings[key]
                    lines[i] = ('; '+key+' = '+(','.join(v) if type(v) is list else v)+'\n').encode()
                    consumed.add(key)
        source = b''.join(lines)
        output = BytesIO()
        with ZipFile(output, 'w') as target:
            for info in archive.infolist():
                content = archive.read(info.filename)
                if info.filename == 'Metadata/plate_1.gcode':
                    content = source
                elif info.filename == 'Metadata/project_settings.config':
                    content = json.dumps(settings).encode()
                target.writestr(info, content)
            target.writestr('Metadata/plate_1.gcode.md5', md5(source).hexdigest().upper().encode() if checksum is None else checksum)
    project = output.getvalue()
    start = source.index(body)
    descriptor = pin_nominal_producer(source, project, producer, expected_source_sha256=sha256(source).hexdigest(),
        expected_project_sha256=sha256(project).hexdigest(), expected_producer_sha256=descriptor.producer_sha256,
        body_start_offset=start, body_end_offset=start+len(body), expected_object_token=descriptor.expected_object_token,
        fan_channels=descriptor.fan_channels)
    entry = replace(entry, state=replace(entry.state, retraction_debt_mm=entry_debt))
    motion = replace(motion, source_sha256=descriptor.source_sha256, project_sha256=descriptor.project_sha256,
                     profile_identity=descriptor.profile_identity, entry_witness_sha256=descriptor.prefix_sha256)
    return source, project, producer, descriptor, entry, motion


def reviewed_fixture_family(inputs):
    chain, restores = [], []
    for event in interpret_nominal_body(*inputs).events:
        amount = dict(event.parameters).get('E', F(0))
        if amount < 0:
            chain.append(ReviewedNegativeRetraction(event.line_number, sha256(event.raw).hexdigest(), amount))
        elif amount > 0:
            if event.before.xyz_mm == event.after.xyz_mm:
                restores.append(ReviewedOrdinaryRestore(event.line_number, sha256(event.raw).hexdigest(),
                    event.scope_before.occurrence, event.before.retraction_debt_mm, event.before.retraction_debt_mm, tuple(chain)))
            chain = []
    return ReviewedOrdinaryRestoreFamily(*tuple(sha256(b).hexdigest() for b in inputs[:3]), '0'*64,
        'Explicit synthetic reviewed fixture family; no actual printer authority.', F('.8'), F(1800), F(1800), 5, tuple(restores))


def derive(inputs, **changes):
    return derive_exact_debt_source(inputs, **dict(dict(family=reviewed_fixture_family(inputs), policy=POLICY, cancelled=lambda: False), **changes))


class ExactDebtDerivationTests(unittest.TestCase):
    def test_exact_noop_and_wipe_under_surplus_preserve_all_other_bytes(self):
        exact = derive(fixture())
        self.assertFalse(exact.changed_lines)
        self.assertEqual(exact.source_bytes, fixture()[0])
        for amount in (b'.29999', b'.30001'):
            body = BODY.replace(b'G1 E-.8 F1800\r\n', b'G1 E-.5 F1800\r\n; WIPE_START\nG1 X1.1 Y2 E-'+amount+b'\r\n; WIPE_END\n')
            inputs = fixture(body)
            result = derive(inputs)
            self.assertEqual(len(result.changed_lines), 1)
            self.assertEqual(result.restores[0].negative_chain_amounts_mm, (F('-.5'), -F(amount.decode())))
            self.assertEqual(result.archive_changed_members, ('Metadata/plate_1.gcode', 'Metadata/plate_1.gcode.md5'))
            old, new = inputs[0].splitlines(keepends=True), result.source_bytes.splitlines(keepends=True)
            self.assertEqual(len(old), len(new))
            for line, (a, b) in enumerate(zip(old, new), 1):
                if line not in result.changed_lines:
                    self.assertEqual(a, b)
            current = (result.source_bytes, result.project_bytes, inputs[2], result.current_descriptor, inputs[4], result.current_motion)
            self.assertFalse(any(e.deposited_filament_mm for e in interpret_nominal_body(*current).events
                if e.before.xyz_mm == e.after.xyz_mm))
            self.assertFalse(result.physical_authority)

    def test_unknown_custom_profile_checksum_precision_and_resources_reject(self):
        cases = (fixture(entry_debt=None), fixture(entry_debt=F('.1')),
            fixture(BODY.replace(b'G1 E.8 F1800', b'G1 E.9 F1800')),
            fixture(BODY.replace(b'G1 E.8 F1800', b'G1 E.8 F1700')),
            fixture(BODY.replace(b'G1 E.8 F1800', b'G1 E.8 F1800 X1')),
            fixture(BODY.replace(b'G1 X2 Y2 E.1 F6000', b'G1 Z3.1 E.1 F6000')),
            fixture(settings_changes={'retract_restart_extra_toolchange': ['.1']}),
            fixture(checksum=b'0'*32), fixture(checksum=b'lowercase-invalid'),
            fixture(BODY.replace(b'G1 E-.8 F1800', b'G1 X1.1 E-.8 F1800')))
        for inputs in cases:
            with self.subTest(source=inputs[3].source_sha256), self.assertRaises(ValueError):
                derive(inputs)
        for changes in (dict(cancelled=lambda: True), dict(cancelled=lambda: 1),
                        dict(policy=replace(POLICY, max_events=1)), dict(policy=replace(POLICY, max_number_bits=1))):
            with self.assertRaises(ValueError):
                derive(fixture(), **changes)
        with self.assertRaisesRegex(ValueError, 'budget'):
            derive(fixture(), policy=replace(POLICY, max_producer_bytes=1))
        body = BODY.replace(b'G1 E-.8 F1800', b'G1 E-.799999 F1800')
        with self.assertRaisesRegex(ValueError, 'precision'):
            derive(fixture(body))

    def test_fresh_writer_nooverwrite_stale_forged_and_archive_preservation(self):
        inputs = fixture()
        result = derive(inputs)
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source, project = root/'original.gcode', root/'original.3mf'
            source.write_bytes(inputs[0]); project.write_bytes(inputs[1])
            kwargs = dict(source_path=source, project_path=project, producer=inputs[2], descriptor=inputs[3],
                entry=inputs[4], motion=inputs[5], family=reviewed_fixture_family(inputs), policy=POLICY, cancelled=lambda: False)
            target = root/'derived.UNVERIFIED'
            with self.assertRaises(ValueError):
                write_exact_debt_source(replace(result, changed_lines=(1,)), target, **kwargs)
            write_exact_debt_source(result, target, **kwargs)
            self.assertEqual((target/'source.UNVERIFIED.gcode').read_bytes(), result.source_bytes)
            with self.assertRaises(ValueError):
                write_exact_debt_source(result, target, **kwargs)
            source.write_bytes(inputs[0]+b'changed')
            with self.assertRaises(ValueError):
                write_exact_debt_source(result, root/'stale.UNVERIFIED', **kwargs)
        with ZipFile(BytesIO(inputs[1])) as old, ZipFile(BytesIO(result.project_bytes)) as new:
            for info in old.infolist():
                self.assertEqual(old.read(info.filename), new.read(info.filename))
                self.assertEqual(info.external_attr, new.getinfo(info.filename).external_attr)

    def test_nondefault_reserved_zip_metadata_is_preserved(self):
        inputs = fixture()
        output = BytesIO()
        with ZipFile(BytesIO(inputs[1])) as old, ZipFile(output, 'w') as new:
            for info in old.infolist():
                info.reserved = 7
                new.writestr(info, old.read(info.filename))
        project = output.getvalue()
        descriptor = replace(inputs[3], project_sha256=sha256(project).hexdigest())
        motion = replace(inputs[5], project_sha256=descriptor.project_sha256)
        current = (inputs[0], project, inputs[2], descriptor, inputs[4], motion)
        result = derive(current)
        with ZipFile(BytesIO(result.project_bytes)) as archive:
            self.assertTrue(all(i.reserved == 7 for i in archive.infolist()))

    def test_reviewed_family_omission_addition_order_raw_chain_and_pins_reject(self):
        body = BODY.replace(b'G1 X2 Y2 E.1 F6000\r\n',
            b'G1 X2 Y2 E.1 F6000\r\nG1 E-.8 F1800\nG1 E.8 F1800\n')
        inputs = fixture(body)
        family = reviewed_fixture_family(inputs)
        first = family.restores[0]
        mutations = (replace(family, restores=family.restores[:1]),
            replace(family, restores=family.restores+(first,)),
            replace(family, restores=tuple(reversed(family.restores))),
            replace(family, original_source_sha256='0'*64),
            replace(family, restores=(replace(first, raw_sha256='0'*64), family.restores[1])),
            replace(family, restores=(replace(first, negative_chain=(replace(first.negative_chain[0], relative_e_mm=F('-.2')),)), family.restores[1])))
        for altered in mutations:
            with self.assertRaises(ValueError):
                derive(inputs, family=altered)
        stale = list(inputs)
        stale[2] += b'forged'
        with self.assertRaises(ValueError):
            derive(tuple(stale), family=family)

    def test_custom_equal_identity_objects_do_not_masquerade_as_immutable_hashes(self):
        class EqualToAnything:
            def __eq__(self, other):
                return True
            def __str__(self):
                return '0'*64
        inputs = fixture()
        family = reviewed_fixture_family(inputs)
        for name in ('original_source_sha256', 'original_project_sha256', 'producer_sha256', 'evidence_sha256'):
            with self.assertRaisesRegex(ValueError, 'identity'):
                derive(inputs, family=replace(family, **{name: EqualToAnything()}))
        restore = family.restores[0]
        for changed in (replace(restore, raw_sha256=EqualToAnything()),
                        replace(restore, negative_chain=(replace(restore.negative_chain[0], raw_sha256=EqualToAnything()),))):
            with self.assertRaisesRegex(ValueError, 'identity'):
                derive(inputs, family=replace(family, restores=(changed,)))

    def test_missing_duplicate_unknown_archive_dependency_and_late_cancellation_reject(self):
        inputs = fixture()
        for mode in ('missing-md5', 'duplicate', 'unknown-checksum'):
            output = BytesIO()
            with ZipFile(BytesIO(inputs[1])) as old, ZipFile(output, 'w') as new:
                for info in old.infolist():
                    if mode != 'missing-md5' or not info.filename.endswith('.md5'):
                        new.writestr(info, old.read(info.filename))
                if mode == 'duplicate':
                    import warnings
                    with warnings.catch_warnings():
                        warnings.simplefilter('ignore', UserWarning)
                        new.writestr('Metadata/plate_1.gcode', inputs[0])
                elif mode == 'unknown-checksum':
                    new.writestr('Metadata/plate_1.gcode.sha256', b'0'*64)
            altered = (inputs[0], output.getvalue(), *inputs[2:])
            with self.assertRaises(ValueError):
                derive(altered, family=reviewed_fixture_family(inputs))
        calls = 0
        def cancel_later():
            nonlocal calls
            calls += 1
            return calls > 5
        with self.assertRaisesRegex(ValueError, 'cancelled'):
            derive(inputs, cancelled=cancel_later)

    def test_actual48_tokens_exact_known_research_pins_and_zero_residual_ledger(self):
        import runpy
        from tools.exponential_top_fixture import ROOT
        inputs = actual_inputs()
        family = runpy.run_path(str(ROOT/'artifacts/exact-debt-derived-review/reproduce.py'))['reviewed_actual_family'](inputs)
        result = derive(inputs, family=family)
        self.assertEqual(len(result.restores), 106)
        self.assertEqual(len(result.changed_lines), 48)
        self.assertEqual(result.moving_event_count, 14985)
        self.assertEqual(result.source_sha256, '2aa69c3ebabc86442456486ee616d3caac2e30850142e670cd8d77937779f374')
        self.assertEqual(result.project_sha256, 'ea5639da549ddc8d4f49029b46561164c4edfa292885cb5e05c4753903a4c1c0')
        self.assertEqual(result.final_logical_e_delta_mm, F('-.00007'))
        self.assertEqual(result.final_debt_mm, F('.79999'))


if __name__ == '__main__':
    unittest.main()
