"""Viewer serialization checks using real band proposals and isolated storage."""
from fractions import Fraction as F
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from adaptive_subedge.engine.convex_chords import propose_convex_band_preview
from smoothificator_preview.native_scene import copy_viewer_config, render_scene, _width_ticks, MAX_BYTES, ViewerSceneError
from smoothificator_preview.viewer_artifact import write_scene
from tests.unit.test_mesh_topology import cube


def fixture_config(bbl=False):
    # Synthetic parser-independent keys test filtering/count only; runtime acceptance
    # must use real Orca serialized configuration, never these fixture-only names.
    return tuple(sorted(dict(printer_model="Bambu Lab X1" if bbl else "Generic",
                             filament_diameter="1.75",extruder_offset="0x0",
                             **{f"fixture_{i}":"1" for i in range(77)}).items()))


def fixture_preview():
    request=SimpleNamespace(z_mm=0.5,axis="X",span_min_mm=0,span_max_mm=1,
                            minimum_width_mm=0.25,maximum_width_mm=0.4,
                            display_height_mm=0.2,end_trim_mm=0.125)
    preview=propose_convex_band_preview(cube(),request.z_mm,axis=request.axis,
        span_min_mm=request.span_min_mm,span_max_mm=request.span_max_mm,
        minimum_width_mm=request.minimum_width_mm,maximum_width_mm=request.maximum_width_mm,
        display_height_mm=request.display_height_mm,end_trim_mm=request.end_trim_mm,
        algorithm_version="convex_equal_bands_v1",max_chords=64,max_vertices=100,
        max_triangles=100,max_mesh_pair_checks=1000,max_section_segments=100,
        max_section_pair_checks=1000,max_ray_directions=8,cancelled=lambda:False)
    return preview,request


class NativeSceneTests(unittest.TestCase):
    def test_key_diagnostics_distinguish_causes_without_key_or_value(self):
        preview,request=fixture_preview()
        for extra,code in (((1,"private-value"),"invalid-config-key-type"),
                           (("_private","private-value"),"invalid-config-key-grammar-len8-index0-ord95"),
                           (("fixture_0","private-value"),"invalid-config-key-duplicate")):
            with self.assertRaises(ViewerSceneError) as caught:
                render_scene(preview,request,fixture_config()+(extra,))
            self.assertEqual(str(caught.exception),code)
            self.assertNotIn("private",str(caught.exception))

    def test_native_uppercase_setting_keys_are_preserved(self):
        rows = dict(fixture_config()) | {"required_nozzle_HRC": "0", "machine_max_force_Y": "0",
                                        "machine_bed_mass_Y": "0"}
        bundle = SimpleNamespace(full_config_keys=lambda: rows.keys(), full_config_value=rows.get)
        self.assertEqual(dict(copy_viewer_config(bundle)), rows)

    def test_both_config_tag_modes_and_command_allowlist(self):
        preview,request=fixture_preview()
        self.assertEqual(preview.state,"complete")
        for bbl in (False,True):
            content=render_scene(preview,request,fixture_config(bbl))
            self.assertTrue(content.isascii())
            self.assertIn("PRINT UNVALIDATED",content)
            lines=content.splitlines()
            role="; FEATURE: Custom" if bbl else ";TYPE:Custom"
            self.assertIn(role,lines)
            self.assertLess(next(i for i,line in enumerate(lines) if line.startswith("G1 ")),lines.index(role))
            self.assertIn(("; LINE_WIDTH: " if bbl else ";WIDTH:")+"0.333333333333",lines)
            commands=[line for line in lines if not line.startswith(";")]
            self.assertTrue(all(line.split()[0] in {"G21","G90","M83","G92","G1"} for line in commands))
            extrusion=[line for line in commands if line.startswith("G1 ") and " E" in line]
            self.assertEqual(len(extrusion),3)
            self.assertTrue(all(float(line.split(" E")[1].split()[0])>0 for line in extrusion))
            self.assertEqual(content,render_scene(preview,request,fixture_config(bbl)))

    def test_filter_before_value_read_and_no_secret_serialization(self):
        rows=dict(fixture_config())|{"api_token":"DO_NOT_READ","machine_start_gcode":"M104 S999","notes":"private","unicode_label":"日本語"}
        class Bundle:
            def full_config_keys(self): return rows.keys()
            def full_config_value(self,key):
                if key in ("api_token","machine_start_gcode","notes"):
                    raise AssertionError("excluded values must not be fetched")
                return rows[key]
        copied=copy_viewer_config(Bundle())
        self.assertEqual(copied,fixture_config())

    def test_config_malformed_required_and_minimum_count(self):
        preview,request=fixture_preview()
        base=dict(fixture_config())
        variants=[tuple(list(fixture_config())[:-1]),tuple(base.items())+(("bad-key","1"),),
                  tuple((base|{"fixture_0":"line\nG28"}).items()),
                  tuple((base|{"fixture_0":"raw\rtext"}).items()),
                  tuple((base|{"filament_diameter":"0"}).items()),
                  tuple((base|{"extruder_offset":"1x0"}).items()),
                  tuple((base|{"extruder_offset":"nanx0"}).items()),
                  tuple((base|{"printer_model":""}).items())]
        for config in variants:
            with self.subTest(config_index=variants.index(config)):
                with self.assertRaises(ValueError): render_scene(preview,request,config)

    def test_width_grid_exact_bounds_and_tie_lower(self):
        self.assertEqual(_width_ticks(F(1,3),0.25,0.4,0.2),333333333333)
        self.assertEqual(_width_ticks(F(2000000000001,2*10**12),1,2,0.2),10**12)
        with self.assertRaisesRegex(ValueError,"width-grid-infeasible"):
            _width_ticks(F(1,3),F(1,3),F(1,3),F(1,10))
        self.assertEqual(_width_ticks(F(1,3),F(333333333334,10**12),F(1,2),F(1,5)),333333333334)

    def test_mismatch_and_collapsed_geometry_refused(self):
        preview,request=fixture_preview()
        request.axis="Y"
        with self.assertRaisesRegex(ValueError,"preview-request-mismatch"):
            render_scene(preview,request,fixture_config())

    def test_output_limit(self):
        preview,request=fixture_preview()
        config=tuple((dict(fixture_config())|{"fixture_0":"a"*MAX_BYTES}).items())
        with self.assertRaisesRegex(ValueError,"viewer-output-limit"):
            render_scene(preview,request,config)

    def test_unique_exclusive_artifacts_and_no_overwrite(self):
        with TemporaryDirectory() as folder:
            root=Path(folder)
            first=write_scene(root,"; VIEW ONLY\n",lambda:False)
            second=write_scene(root,"; VIEW ONLY\n",lambda:False)
            self.assertNotEqual(first,second)
            self.assertEqual(first.parent,root.resolve())
            self.assertTrue(first.name.endswith(".VIEW_ONLY.gcode"))
            with patch("smoothificator_preview.viewer_artifact.uuid4",return_value=SimpleNamespace(hex="fixed")):
                target=write_scene(root,"first",lambda:False)
                with self.assertRaises(FileExistsError): write_scene(root,"second",lambda:False)
                self.assertEqual(target.read_text(),"first")

    def test_cancellation_before_and_after_write_leaves_no_file(self):
        for cancel_at in range(1,5):
            with TemporaryDirectory() as folder:
                count=0
                def cancelled():
                    nonlocal count
                    count+=1
                    return count==cancel_at
                with self.assertRaises(InterruptedError): write_scene(folder,"; view\n",cancelled)
                self.assertEqual(list(Path(folder).iterdir()),[])

    def test_nonascii_oversized_or_invalid_callback_rejected(self):
        with TemporaryDirectory() as folder:
            for content,callback in (("日本語",lambda:False),("a"*(MAX_BYTES+1),lambda:False),("abc",lambda:1)):
                with self.assertRaises(ValueError): write_scene(folder,content,callback)
            self.assertEqual(list(Path(folder).iterdir()),[])


if __name__=="__main__":
    unittest.main()
