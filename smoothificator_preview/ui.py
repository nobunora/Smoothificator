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


def render_artifact_path(path):
    return ('<p class="note">標準プレビュー用ファイル（候補のみ・印刷禁止）</p>'
            f'<p><code>{escape(str(path))}</code></p>'
            '<p>別のOrcaウィンドウでこのファイルを開き、線の種類「Custom」を選んでください。'
            '作業中のウィンドウで開くと現在のプロジェクトが置き換わる場合があります。'
            '元スライスとの重ね合わせではありません。座標と幅は表示用に丸めています。</p>')


def render_result(snapshot, request, preview):
    bands = type(preview.proposals) is tuple
    proposals = preview.proposals if bands else preview.proposals.proposals
    width = preview.width_mm if bands else request.width_mm
    rows = "".join(f"<tr><td>{_number(row.position_mm)}</td><td>{escape(row.state)}</td>"
                   f"<td>{escape(row.reason)}</td></tr>" for row in proposals)
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
        for row in proposals:
            if row.state == "proposed":
                x1, y1 = xy(row.start_xy_mm)
                x2, y2 = xy(row.end_xy_mm)
                lines.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"/>')
        svg = (f'<svg viewBox="0 0 620 600" role="img" aria-label="元断面と未評価候補">'
               f'<polygon points="{polygon}" fill="#dbeafe" stroke="#2563eb" stroke-width="2"/>'
               f'<g stroke="#d97706" stroke-width="{_number(width*520/span)}">'+"".join(lines)+ '</g>'
               '<text x="15" y="25">Y ↑</text><text x="550" y="590">X →</text></svg>')
        svg += f'<p>X {_number(xmin)} … {_number(xmax)} mm / Y {_number(ymin)} … {_number(ymax)} mm</p>'
    output = (f'<h2>{escape(snapshot.name)}</h2><p>未評価の候補 · {escape(FRAME)}</p>'
              f'<p>Z={_number(request.z_mm)} mm / {escape(request.axis)} / 幅={_number(width) if width is not None else "—"} mm '
              f'/ 端部trim={_number(request.end_trim_mm)} mm</p>'
              '<p>青：元モデルの断面　橙：候補の公称幅。改善量・支持・印刷可否は未評価。</p>'
              f'{svg}<table><thead><tr><th>位置 mm</th><th>状態</th><th>理由</th></tr></thead>'
              f'<tbody>{rows}</tbody></table>')
    if bands and preview.common_running_interval is not None:
        low, high = preview.common_running_interval
        output = (f'<p>本数：{len(proposals)} / 幅制約：{_number(request.minimum_width_mm)} … '
                  f'{_number(request.maximum_width_mm)} mm / 表示高さ：{_number(request.display_height_mm)} mm</p>'
                  f'<p>平面上の共通被覆範囲：走行軸 {_number(low)} … {_number(high)} mm × '
                  f'直交軸 {_number(request.span_min_mm)} … {_number(request.span_max_mm)} mm。'
                  '表面の改善量を保証するものではありません。</p>') + output
    if len(output.encode("utf-8")) > MAX_HTML_BYTES:
        raise ValueError("render-limit")
    return output


def page(snapshot):
    vertices = snapshot.mesh.vertices
    lowz, highz = min(p.z_mm for p in vertices), max(p.z_mm for p in vertices)
    lowy, highy = min(p.y_mm for p in vertices), max(p.y_mm for p in vertices)
    xs = [p.x_mm for p in vertices]
    span = min(max(xs)-min(xs), highy-lowy)
    defaults = {"z": lowz/2+highz/2, "minimum_width": .3, "maximum_width": .6,
                "display_height": .2, "trim": span/40,
                "span_min": lowy+(highy-lowy)/4, "span_max": highy-(highy-lowy)/4}
    for key in defaults:
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
<p class="note">未評価の研究候補です。改善結果・印刷可能な経路ではありません。元のG-codeは変更しません。<br>
Custom分類の候補のみを標準ビュー用の別ファイルに保存します。印刷しないでください。<br>
モデルworld座標（mm）。幅0.3〜0.6 mm・高さ0.2 mmは研究例で、プリンタの保証値ではありません。<br>
表示は生成時点のスナップショットです。Orcaでモデルを変更したら再生成してください。</p>
<form id="form"><label>Z (mm)<input id="z" required></label><label>方向<select id="axis"><option>X</option><option>Y</option></select></label>
<label>最小幅 (mm)<input id="minimum_width" required></label><label>最大幅 (mm)<input id="maximum_width" required></label>
<label>表示高さ (mm)<input id="display_height" required></label><label>端部trim (mm)<input id="trim" required></label>
<label>直交軸の開始 (mm)<input id="span_min" required></label><label>直交軸の終了 (mm)<input id="span_max" required></label>
<button id="generate">候補と標準ビュー用ファイルを生成</button><button type="button" id="cancel">中止</button></form>
<p id="status" role="status">idle — 入力確認後に候補を生成</p><div id="result"></div>
<script>
const defaults=__DEFAULTS__;for(const [key,value] of Object.entries(defaults))document.getElementById(key).value=value;
let generation=-1;
document.getElementById('form').addEventListener('submit',event=>{event.preventDefault();
 document.getElementById('result').replaceChildren();document.getElementById('status').textContent='copying';
 const msg={command:'generate_band'};for(const key of ['z','axis','minimum_width','maximum_width','display_height','trim','span_min','span_max'])msg[key]=document.getElementById(key).value;
 window.orca.postMessage(msg);
});
document.getElementById('cancel').onclick=()=>window.orca.postMessage({command:'cancel'});
window.orca.onMessage(msg=>{if(msg.generation<generation)return;generation=msg.generation;
 document.getElementById('status').textContent=msg.state+' — '+msg.reason;
 document.getElementById('generate').disabled=['running','copying'].includes(msg.state);
 document.getElementById('result').innerHTML=msg.html||'';
});
</script></html>'''
