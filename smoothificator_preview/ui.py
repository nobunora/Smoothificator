"""Presentation of copied research data; no optimizer or live-model access."""
from html import escape
import json
from math import isfinite
from .limits import FRAME, MAX_HTML_BYTES


def _number(value):
    value = float(value)
    if not isfinite(value):
        raise ValueError("nonfinite-render-coordinate")
    return format(value, ".12g")


def render_result(snapshot, request, preview):
    proposals = preview.proposals
    rows = "".join(f"<tr><td>{escape(str(row.position_mm))}</td><td>{escape(row.state)}</td>"
                   f"<td>{escape(row.reason)}</td></tr>" for row in proposals.proposals)
    svg = ""
    if preview.section is not None:
        points = [(v.x_mm, v.y_mm) for v in preview.section.vertices]
        xmin, xmax = min(p[0] for p in points), max(p[0] for p in points)
        ymin, ymax = min(p[1] for p in points), max(p[1] for p in points)
        span = max(xmax-xmin, ymax-ymin)
        def xy(point):
            return _number(40+520*(point[0]-xmin)/span), _number(560-520*(point[1]-ymin)/span)
        polygon = " ".join(",".join(xy(p)) for p in points)
        lines = []
        for row in proposals.proposals:
            if row.state == "proposed":
                x1, y1 = xy(row.start_xy_mm)
                x2, y2 = xy(row.end_xy_mm)
                lines.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"/>')
        svg = (f'<svg viewBox="0 0 620 600" role="img" aria-label="元断面と未評価候補">'
               f'<polygon points="{polygon}" fill="#dbeafe" stroke="#2563eb" stroke-width="2"/>'
               '<g stroke="#d97706" stroke-width="3">'+"".join(lines)+ '</g>'
               '<text x="15" y="25">Y ↑</text><text x="550" y="590">X →</text></svg>')
        svg += f'<p>X {_number(xmin)} … {_number(xmax)} mm / Y {_number(ymin)} … {_number(ymax)} mm</p>'
    output = (f'<h2>{escape(snapshot.name)}</h2><p>未評価の候補 · {escape(FRAME)}</p>'
              f'<p>Z={_number(request.z_mm)} mm / {escape(request.axis)} / 幅={_number(request.width_mm)} mm '
              f'/ 端部trim={_number(request.end_trim_mm)} mm</p>'
              '<p>青：元モデルの断面　橙：候補中心線。改善量・支持・印刷可否は未評価。</p>'
              f'{svg}<table><thead><tr><th>位置 mm</th><th>状態</th><th>理由</th></tr></thead>'
              f'<tbody>{rows}</tbody></table>')
    if len(output.encode("utf-8")) > MAX_HTML_BYTES:
        raise ValueError("render-limit")
    return output


def page(snapshot):
    vertices = snapshot.mesh.vertices
    lowz, highz = min(p.z_mm for p in vertices), max(p.z_mm for p in vertices)
    lowy, highy = min(p.y_mm for p in vertices), max(p.y_mm for p in vertices)
    xs = [p.x_mm for p in vertices]
    span = min(max(xs)-min(xs), highy-lowy)
    defaults = {"z": lowz/2+highz/2, "width": span/40, "trim": span/40,
                "positions": ", ".join(_number(lowy+(highy-lowy)*i/4) for i in (1, 2, 3))}
    for key in ("z", "width", "trim"):
        defaults[key] = _number(defaults[key])
    encoded = json.dumps(defaults).replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    return PAGE.replace("__DEFAULTS__", encoded)


PAGE = '''<!doctype html><html lang="ja"><meta charset="utf-8">
<style>
body{font:14px system-ui;margin:24px;color:var(--orca-text-color,#172033);background:var(--orca-background-color,#fff)}
h1{font-size:23px} .note{padding:12px;background:#fff4d6;color:#523900;border-radius:8px}
form{display:flex;gap:12px;flex-wrap:wrap;margin:20px 0}label{display:grid;gap:5px}input,select,button{font:inherit;padding:7px}
input{width:100px}#positions{width:270px}button{cursor:pointer}#status{font-weight:bold}svg{width:100%;max-height:480px}
table{border-collapse:collapse;width:100%}td,th{text-align:left;padding:7px;border-bottom:1px solid #aaa}
</style><h1>Smoothificator · 候補経路プレビュー</h1>
<p class="note">未評価の研究候補です。改善結果・印刷可能な経路ではありません。G-codeは変更しません。<br>
モデルworld座標（mm）。初期値はモデル寸法から作る研究例です。設定を確認して生成してください。<br>
表示は生成時点のスナップショットです。Orcaでモデルを変更したら再生成してください。</p>
<form id="form"><label>Z (mm)<input id="z" required></label><label>方向<select id="axis"><option>X</option><option>Y</option></select></label>
<label>幅 (mm)<input id="width" required></label><label>端部trim (mm)<input id="trim" required></label>
<label>直交軸上の位置 (mm, カンマ区切り)<input id="positions" required></label>
<button id="generate">候補を生成</button><button type="button" id="cancel">中止</button></form>
<p id="status" role="status">idle — 入力確認後に候補を生成</p><div id="result"></div>
<script>
const defaults=__DEFAULTS__;for(const [key,value] of Object.entries(defaults))document.getElementById(key).value=value;
let generation=-1;
document.getElementById('form').addEventListener('submit',event=>{event.preventDefault();
 document.getElementById('result').replaceChildren();document.getElementById('status').textContent='copying';
 const msg={command:'generate'};for(const key of ['z','axis','width','trim','positions'])msg[key]=document.getElementById(key).value;
 window.orca.postMessage(msg);
});
document.getElementById('cancel').onclick=()=>window.orca.postMessage({command:'cancel'});
window.orca.onMessage(msg=>{if(msg.generation<generation)return;generation=msg.generation;
 document.getElementById('status').textContent=msg.state+' — '+msg.reason;
 document.getElementById('generate').disabled=['running','copying'].includes(msg.state);
 document.getElementById('result').innerHTML=msg.html||'';
});
</script></html>'''
