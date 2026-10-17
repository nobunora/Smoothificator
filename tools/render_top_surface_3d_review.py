"""Write a self-contained, read-only 3D canvas review of the pinned coupon."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from tools.audit_layered_preview_overlap import SOURCE_SHA256, source_segments
from tools.generate_top_surface_candidates import MODEL_SHA256, ROOT


HTML = r'''<!doctype html>
<html lang="ja"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Smoothificator 上面候補 3Dレビュー</title>
<style>
*{box-sizing:border-box}body{margin:0;background:#101820;color:#e6edf2;font:15px system-ui,"Yu Gothic",sans-serif}
header{padding:15px 22px;border-bottom:1px solid #394b58}h1{font-size:21px;margin:0 0 5px}p{margin:5px 0;line-height:1.5}
main{display:grid;grid-template-columns:minmax(650px,1fr) 340px;gap:14px;padding:14px}
section,aside{background:#192530;border:1px solid #394b58;border-radius:10px;overflow:hidden}
canvas{display:block;width:100%;height:min(82vh,1000px);cursor:grab}canvas:active{cursor:grabbing}
aside{padding:16px}label{display:block;margin:15px 0}input[type=range]{width:100%}.warn{color:#ffd27a}
.sw{display:inline-block;width:13px;height:13px;border-radius:2px;margin-right:7px}
.rows{border-top:1px solid #394b58;margin-top:14px;padding-top:12px;font:13px ui-monospace,Consolas,monospace}
.rows div{padding:4px 0}small{color:#acbbc7}code{overflow-wrap:anywhere}
@media(max-width:950px){main{grid-template-columns:1fr}canvas{height:60vh}}
</style>
<header><h1>Smoothificator 上面候補の3Dレビュー</h1>
<p>傾けた3MF上面、同一Orcaスライス、異なる真のZに置いた候補を同じ座標系で表示。ドラッグで回転、ホイールで拡大できます。</p></header>
<main><section><canvas id="scene" aria-label="3D上面、Orcaスライス、候補線分"></canvas></section>
<aside><strong>表示</strong>
<label><input id="base" type="checkbox" checked> <i class="sw" style="background:#8499a8"></i>元のOrcaスライス</label>
<label><input id="face" type="checkbox" checked> <i class="sw" style="background:#52a8df"></i>変換後のモデル上面</label>
<label><input id="candidate" type="checkbox" checked> <i class="sw" style="background:#55db91"></i>現在採用できる候補</label>
<label><input id="excluded" type="checkbox" checked> <i class="sw" style="background:#ff826b"></i>浮き・上層重なりで除外した参考線</label>
<label>表示する元スライスの上限Z: <span id="limitText">3.00</span> mm
<input id="limit" type="range" min="0.2" max="3" step="0.02" value="2.2"></label>
<p class="warn">top-07 は幅0.34 mm・厚さ0.14 mmの表示仮説です。点検した位置では下面が下層に届きますが、全区間の接触・形状改善・ノズル干渉は未検証です。レビュー専用で印刷不可。</p>
<div class="rows" id="rows"></div>
<p><small>3MF SHA-256: <code id="modelSha"></code><br>Orca slice SHA-256: <code id="sliceSha"></code></small></p>
</aside></main>
<script>
const data=__DATA__;
const canvas=document.getElementById('scene'), ctx=canvas.getContext('2d');
const checks=['base','face','candidate','excluded'].map(id=>document.getElementById(id));
let yaw=-0.74,pitch=0.48,scale=33,drag=null;
function resize(){const ratio=devicePixelRatio||1;canvas.width=Math.round(canvas.clientWidth*ratio);canvas.height=Math.round(canvas.clientHeight*ratio);draw()}
function project(point){let [x,y,z]=point; x-=125;y-=125;z-=1.5;
 const cy=Math.cos(yaw),sy=Math.sin(yaw),cp=Math.cos(pitch),sp=Math.sin(pitch);
 const side=cy*x-sy*y, depth=sy*x+cy*y;
 return [canvas.width/2+side*scale*(devicePixelRatio||1),canvas.height/2+(sp*depth-cp*z)*scale*(devicePixelRatio||1)];}
function stroke(a,b,color,width,dashed=false){const p=project(a),q=project(b);ctx.beginPath();ctx.setLineDash(dashed?[8,5]:[]);ctx.moveTo(...p);ctx.lineTo(...q);ctx.strokeStyle=color;ctx.lineWidth=width*(devicePixelRatio||1);ctx.lineCap='round';ctx.stroke();ctx.setLineDash([])}
function draw(){ctx.clearRect(0,0,canvas.width,canvas.height);const limit=Number(document.getElementById('limit').value);
 document.getElementById('limitText').textContent=limit.toFixed(2);
 if(checks[0].checked){for(const s of data.base){if(s[0]<=limit+1e-7)stroke([s[1],s[2],s[0]],[s[3],s[4],s[0]],'#8499a8',Math.max(.8,s[5]*scale*.12))}}
 if(checks[1].checked){for(let i=0;i<4;i++)stroke(data.top[i],data.top[(i+1)%4],'#52a8df',3)}
 for(const s of data.candidates){const bad=s.review_status!=='candidate-for-review';if(checks[bad?3:2].checked)stroke(s.start_mm,s.end_mm,bad?(s.review_status==='below-minimum-height'?'#ffd27a':'#ff826b'):'#55db91',bad?4:5,bad)}
}
canvas.addEventListener('pointerdown',e=>{drag=[e.clientX,e.clientY,yaw,pitch];canvas.setPointerCapture(e.pointerId)});
canvas.addEventListener('pointermove',e=>{if(!drag)return;yaw=drag[2]+(e.clientX-drag[0])*.008;pitch=Math.max(-1.2,Math.min(1.2,drag[3]+(e.clientY-drag[1])*.008));draw()});
canvas.addEventListener('pointerup',()=>drag=null);
canvas.addEventListener('wheel',e=>{e.preventDefault();scale=Math.max(10,Math.min(130,scale*Math.exp(-e.deltaY*.001)));draw()},{passive:false});
for(const node of [...checks,document.getElementById('limit')])node.addEventListener('input',draw);
document.getElementById('rows').innerHTML=data.candidates.map(s=>`<div style="color:${s.review_status==='below-minimum-height'?'#ffd27a':s.review_status==='candidate-for-review'?'#55db91':'#ff826b'}">${s.id}　Z=${s.start_mm[2].toFixed(2)} mm　Y=${s.start_mm[1].toFixed(3)} mm<br>幅 ${s.width_mm.toFixed(2)} / 有効厚 ${s.sampled_effective_height_mm.toFixed(2)} mm / 上層XY余裕 ${s.nearest_higher_footprint_clearance_mm.toFixed(3)} mm<br>${s.review_status}${s.sampled_nominal_minimum_top_z_mm===null?'':` / 下層最小上面 Z=${s.sampled_nominal_minimum_top_z_mm.toFixed(3)} mm`}</div>`).join('');
document.getElementById('modelSha').textContent=data.model_sha;
document.getElementById('sliceSha').textContent=data.slice_sha;
new ResizeObserver(resize).observe(canvas);
</script></html>'''


def top_corners(plan: dict) -> list[list[float]]:
    matrix = plan["frame"]["transform_3mf"]
    offset_x, offset_y = plan["frame"]["plate_offset_xy_mm"]
    z = plan["frame"]["top_local_z_mm"]
    return [[matrix[0]*x+matrix[3]*y+matrix[6]*z+matrix[9]+offset_x,
             matrix[1]*x+matrix[4]*y+matrix[7]*z+matrix[10]+offset_y,
             matrix[2]*x+matrix[5]*y+matrix[8]*z+matrix[11]]
            for x, y in ((-5,-5),(5,-5),(5,5),(-5,5))]


def build_html(source: bytes, plan: dict) -> str:
    if (hashlib.sha256(source).hexdigest() != SOURCE_SHA256
            or plan.get("source_slice_sha256") != SOURCE_SHA256
            or plan.get("source_3mf_sha256") != MODEL_SHA256
            or plan.get("scope") != "3d-review-only"
            or plan.get("printable_authorized") is not False):
        raise ValueError("review fixture identity mismatch")
    baseline = source_segments(source)
    if len(baseline) != 669 or len(plan.get("segments", [])) != 7:
        raise ValueError("unexpected review segment counts")
    payload = {"base": [row[:6] for row in baseline], "top": top_corners(plan),
               "candidates": plan["segments"], "model_sha": MODEL_SHA256,
               "slice_sha": SOURCE_SHA256}
    return HTML.replace("__DATA__", json.dumps(payload, separators=(",", ":")))


def main() -> None:
    source = (ROOT / "artifacts/cli-midpoint-slice/plate_1.gcode").read_bytes()
    plan = json.loads((ROOT / "artifacts/geometry-review/top-surface-candidates.json").read_text(encoding="utf-8"))
    output = ROOT / "artifacts/geometry-review/top-surface-3d-review.html"
    output.write_text(build_html(source, plan), encoding="utf-8")
    print(output)


if __name__ == "__main__":
    main()
