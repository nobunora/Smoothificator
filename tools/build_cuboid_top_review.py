"""Prepare a cuboid, slice offline, and overlay full-top VIEW_ONLY hypotheses."""
from __future__ import annotations

import argparse
from collections import defaultdict
from fractions import Fraction as F
import hashlib
from io import BytesIO
import json
import math
from pathlib import Path
import subprocess
from uuid import uuid4
from zipfile import ZipFile, ZIP_DEFLATED

from smoothificator_preview.native_scene import _config
from tools.audit_layered_preview_overlap import source_segments
from tools.generate_top_surface_candidates import MODEL_SHA256, ROOT, _pinned


SIZE_MM = (20, 12, 3)
TOP_LIFT_MM = F("0.08")
WIDTH_MM = F("0.34")
HEIGHT_MM = F("0.19")
FACES = ((0,2,1),(0,3,2),(4,5,6),(4,6,7),(0,1,5),(0,5,4),
         (1,2,6),(1,6,5),(2,3,7),(2,7,6),(3,0,4),(3,4,7))


def prepare_fixture(destination: Path, *, tilt_degrees: float = 0) -> tuple[Path, Path]:
    if not math.isfinite(tilt_degrees) or not 0 <= tilt_degrees <= 30:
        raise ValueError("fixture X tilt must be finite and within 0..30 degrees")
    destination.mkdir(parents=True, exist_ok=True)
    length, width, height = SIZE_MM
    vertices = ((0,0,0),(length,0,0),(length,width,0),(0,width,0),
                (0,0,height),(length,0,height),(length,width,height),(0,width,height))
    angle = math.radians(tilt_degrees)
    vertices = tuple((x, y*math.cos(angle)-z*math.sin(angle),
                      y*math.sin(angle)+z*math.cos(angle)) for x,y,z in vertices)
    stl = ["solid cuboid_20x12x3"]
    for face in FACES:
        stl.extend(("facet normal 0 0 0", "outer loop"))
        stl.extend("vertex " + " ".join(map(str, vertices[i])) for i in face)
        stl.extend(("endloop", "endfacet"))
    stl.append("endsolid cuboid_20x12x3")
    stl_path = destination / "cuboid-20x12x3.stl"
    stl_path.write_text("\n".join(stl)+"\n", encoding="ascii")
    vertex_xml = "".join(f'<vertex x="{x}" y="{y}" z="{z}"/>' for x,y,z in vertices)
    triangle_xml = "".join(f'<triangle v1="{a}" v2="{b}" v3="{c}"/>' for a,b,c in FACES)
    model = ('<?xml version="1.0" encoding="UTF-8"?>'
        '<model unit="millimeter" xml:lang="en-US" xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02">'
        '<resources><object id="1" type="model" name="Cuboid 20x12x3"><mesh><vertices>'
        +vertex_xml+'</vertices><triangles>'+triangle_xml+'</triangles></mesh></object></resources>'
        '<build><item objectid="1" transform="1 0 0 0 1 0 0 0 1 80 84 0"/></build></model>')
    with ZipFile(BytesIO(_pinned(ROOT / "artifacts/fixtures/offline-coupon.3mf", MODEL_SHA256))) as original:
        settings = json.loads(original.read("Metadata/project_settings.config"))
    # This is an offline geometry fixture. Keep slicer geometry/profile data,
    # disable arc fitting and remove machine/filament template programs.
    settings["enable_arc_fitting"] = "0"
    for key,value in tuple(settings.items()):
        if key.endswith("_gcode"):
            settings[key] = [""]*len(value) if isinstance(value,list) else ""
    settings["machine_start_gcode"] = "G90\nM83\nG92 E0"
    project_path = destination / "cuboid-20x12x3.3mf"
    with ZipFile(project_path,"w",compression=ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", '<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/><Default Extension="config" ContentType="application/octet-stream"/></Types>')
        archive.writestr("_rels/.rels", '<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>')
        archive.writestr("3D/3dmodel.model",model)
        archive.writestr("Metadata/project_settings.config",json.dumps(settings))
    return project_path, stl_path


def top_hatch(bounds: tuple[F,F,F,F], top_z: F):
    x0,x1,y0,y1 = bounds
    if not x1>x0 or not y1-y0>WIDTH_MM:
        raise ValueError("invalid cuboid face bounds")
    count = math.ceil((y1-y0)/WIDTH_MM)
    pitch = (y1-y0-WIDTH_MM)/(count-1)
    return tuple((x0,y0+WIDTH_MM/2+i*pitch,x1,top_z+TOP_LIFT_MM) for i in range(count))


def build_scene(source: bytes, source_digest: str) -> tuple[str,dict]:
    original = source_segments(source,expected_sha256=source_digest)
    if not original:
        raise ValueError("empty cuboid baseline")
    lines = source.decode("ascii").splitlines()
    metadata = {}
    role, height = "", None
    for number,line in enumerate(lines,1):
        if line.startswith(";TYPE:"):
            role = line[6:]
        if line.startswith("; FEATURE: "):
            role = line[11:]
        if line.startswith(";HEIGHT:"):
            height = F(line[8:])
        if line.startswith("; LAYER_HEIGHT:"):
            height = F(line.split(":",1)[1].strip())
        metadata[number] = (role,height)
    top = max(F(str(s[0])) for s in original)
    walls = [s for s in original if F(str(s[0])) == top and metadata[s[6]][0] == "Outer wall"]
    if not walls or top != SIZE_MM[2]:
        raise ValueError("unexpected cuboid slice top")
    x0 = min(F(str(min(s[1],s[3])))-F(str(s[5]))/2 for s in walls)
    x1 = max(F(str(max(s[1],s[3])))+F(str(s[5]))/2 for s in walls)
    y0 = min(F(str(min(s[2],s[4])))-F(str(s[5]))/2 for s in walls)
    y1 = max(F(str(max(s[2],s[4])))+F(str(s[5]))/2 for s in walls)
    observed = (x1-x0,y1-y0)
    orientations = ((F(SIZE_MM[0]),F(SIZE_MM[1])),(F(SIZE_MM[1]),F(SIZE_MM[0])))
    matches = [pair for pair in orientations if all(abs(a-b)<=F("0.002") for a,b in zip(observed,pair))]
    if len(matches)!=1:
        raise ValueError("cuboid slice dimension mismatch")
    # Slicer coordinates are rounded; bind the known box dimensions to its
    # observed center rather than accumulating those display-rounding errors.
    cx,cy = (x0+x1)/2,(y0+y1)/2
    span_x,span_y = matches[0]
    bounds = (cx-span_x/2,cx+span_x/2,cy-span_y/2,cy+span_y/2)
    hatch = top_hatch(bounds,top)
    start,end = lines.index("; CONFIG_BLOCK_START"),lines.index("; CONFIG_BLOCK_END")
    config,diameter = _config(tuple(
        tuple(line[2:].split(" = ",1)) for line in lines[start+1:end]
        if line.startswith("; ") and " = " in line
        and line[2:].split(" = ",1)[0] not in ("wipe_tower_x","wipe_tower_y")))
    bed = [tuple(F(v) for v in point.split("x"))
           for point in dict(config)["printable_area"].split(",")]
    if len(bed)!=4 or any(len(point)!=2 for point in bed):
        raise ValueError("review requires the fixture's rectangular bed")
    shift_x = (min(p[0] for p in bed)+max(p[0] for p in bed))/2-cx
    shift_y = (min(p[1] for p in bed)+max(p[1] for p in bed))/2-cy
    area_filament = math.pi*(diameter/2)**2
    by_z = defaultdict(list)
    for z,ax,ay,bx,by,width,number in original:
        feature,h = metadata[number]
        if h is None or not 0<h<=F(str(width)):
            raise ValueError("invalid baseline bead metadata")
        by_z[F(str(z))].append((F(str(ax)),F(str(ay)),F(str(bx)),F(str(by)),F(str(width)),h,feature))
    for ax,y,bx,z in hatch:
        by_z[z].append((ax,y,bx,y,WIDTH_MM,HEIGHT_MM,"Custom"))
    def n(value):
        return f"{float(value):.9f}".rstrip("0").rstrip(".")
    output = ["; generated by OrcaSlicer compatible Smoothificator viewer representation",
              "; UNVERIFIED VIEW ONLY - FULL TOP COVERAGE PROBE - DO NOT PRINT",
              "; Original model top 3.0 mm; added hypothesis top 3.08 mm",
              f"; VIEWER XY translation only: X{n(shift_x)} Y{n(shift_y)}; Z unchanged",
              "; CONFIG_BLOCK_START"]
    output.extend(f"; {key} = {value}" for key,value in config)
    output.extend(("; CONFIG_BLOCK_END","G21","G90","M83","G92 E0"))
    for z,segments in sorted(by_z.items()):
        output.extend(("; CHANGE_LAYER",f"; Z_HEIGHT: {n(z)}"))
        for ax,ay,bx,by,w,h,feature in segments:
            length = math.hypot(float(bx-ax),float(by-ay))
            area = float(w*h)+(math.pi/4-1)*float(h*h)
            output.extend((f"G1 X{n(ax+shift_x)} Y{n(ay+shift_y)} Z{n(z)} F1200",f"; FEATURE: {feature}",
                           f"; LINE_WIDTH: {n(w)}",f"; LAYER_HEIGHT: {n(h)}",
                           f"G1 X{n(bx+shift_x)} Y{n(by+shift_y)} E{n(length*area/area_filament)} F1200"))
    content = "\n".join(output)+"\n"
    if len(content)>2_097_152 or not content.isascii():
        raise ValueError("bounded viewer size exceeded")
    return content,{"scope":"cuboid-full-top-display-only", "source_slice_sha256":source_digest,
        "model_dimensions_mm":SIZE_MM,"top_face_bounds_exact_mm":[str(v) for v in bounds],
        "source_top_z_mm":float(top),"candidate_top_z_mm":float(top+TOP_LIFT_MM),
        "candidate_height_mm":float(HEIGHT_MM),"candidate_width_mm":float(WIDTH_MM),
        "candidate_count":len(hatch),"original_segment_count":len(original),
        "layer_count":len(by_z),"nominal_rectangular_footprint_coverage":"entire 20 x 12 mm top face",
        "viewer_xy_translation_exact_mm":[str(shift_x),str(shift_y)],
        "viewer_translation_applied_to":"all baseline and candidate paths equally; Z and relative geometry unchanged",
        "pitch_exact_mm":str(hatch[1][1]-hatch[0][1]),
        "candidate_segments":[{"start_mm":[float(a),float(y),float(z)],"end_mm":[float(b),float(y),float(z)]} for a,y,b,z in hatch],
        "nominal_axial_caps":"flat; Orca pointed caps may visually extend outside the box",
        "continuous_contact_verified":False,"shape_improvement_verified":False,
        "printable_authorized":False,"validation":"coverage display only; raises nominal top by 0.08 mm"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepare-only",action="store_true")
    args = parser.parse_args()
    folder = ROOT / "artifacts/cuboid-top-review"
    project,stl = prepare_fixture(folder)
    if args.prepare_only:
        print(project)
        return
    executable = ROOT / "artifacts/runtime/orca-nightly/OrcaSlicer/orca-slicer.exe"
    command = [str(executable),"--slice","0","--datadir",str(folder/"cli-profile"),
               "--outputdir",str(folder/"original-slice"),str(project)]
    (folder/"original-slice").mkdir(exist_ok=True)
    result = subprocess.run(command,cwd=folder,capture_output=True,timeout=120)
    (folder/"slice-stdout.log").write_bytes(result.stdout)
    (folder/"slice-stderr.log").write_bytes(result.stderr)
    if result.returncode:
        raise RuntimeError(f"offline slice failed: {result.returncode}; inspect slice logs")
    source_path = folder/"original-slice/plate_1.gcode"
    source = source_path.read_bytes()
    digest = hashlib.sha256(source).hexdigest()
    content,receipt = build_scene(source,digest)
    target = folder/f"cuboid-full-top-{uuid4().hex}.UNVERIFIED_VIEW_ONLY.gcode"
    target.write_text(content,encoding="ascii")
    receipt.update(viewer_file=str(target),viewer_sha256=hashlib.sha256(content.encode("ascii")).hexdigest(),
                   model_3mf_sha256=hashlib.sha256(project.read_bytes()).hexdigest(),
                   model_stl_sha256=hashlib.sha256(stl.read_bytes()).hexdigest())
    target.with_suffix(".json").write_text(json.dumps(receipt,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(receipt,indent=2))


if __name__ == "__main__":
    main()
