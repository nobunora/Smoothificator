"""Presentation-only dedicated calibration library window."""
import json


def page(state):
    encoded=json.dumps(state).replace('<','\\u003c').replace('>','\\u003e').replace('&','\\u0026')
    return PAGE.replace('__STATE__',encoded)


PAGE=r'''<!doctype html><html lang="ja"><meta charset="utf-8"><style>
body{font:14px system-ui;margin:24px;color:#172033;background:#fff}h1{font-size:23px}.note{padding:14px;background:#fff3cc;border-radius:8px}.controls{display:flex;gap:10px;flex-wrap:wrap;margin:16px 0}button,select{font:inherit;padding:8px}table{width:100%;border-collapse:collapse}td,th{padding:7px;border:1px solid #ccd3dd;text-align:center}td button{width:100%;min-height:75px;background:#f4f7fb;border:1px solid #aab4c3;white-space:pre-line}td button.chosen{background:#c7e8ff;border:2px solid #1672ad}code{overflow-wrap:anywhere}#status{white-space:pre-line}button:disabled{opacity:.45}</style>
<h1>校正マトリクス · 準備済み実G-code</h1>
<p class="note"><strong>Bambu Studioの表示幅0.45mmは公称の表示用情報です。実際の線幅を計算・測定した値ではありません。</strong><br>吐出量・Eはセルごとに変わります。現在の形状から生成せず、同梱の固定プロファイルで検証した実G-codeをそのまま書き出します。仮の基準条件で、選択済みの最適値ではありません。自動印刷はしません。</p>
<div class="controls"><label>試験 <select id="trial"></select></label><button id="refresh">現在設定を再照合</button></div>
<p id="scope"></p><p id="compatibility"></p><p id="baseline"></p><table id="grid"></table>
<div class="controls"><button id="export">実G-code一式を書き出す</button><button id="baseline_export">基準プロジェクトだけを書き出す</button></div>
<p>設定が一致しない場合は基準プロジェクトをOrcaで手動で開き、元のプロファイルを読み込んで再照合してください。基準プロジェクトにはG-codeを含みません。実験のraw G-codeを再スライスすると実験条件が失われます。</p>
<div class="controls"><label>観察 <select id="symptom"><option value="acceptable">許容</option><option value="central_ridge">中央が過剰</option><option value="missing_center">途切れ・欠落</option><option value="end_blob">終端の塊</option><option value="start_starvation">始端の不足</option><option value="scraping">擦れ・接触</option><option value="none_acceptable">適切なセルなし</option></select></label><button id="save">選択を保存</button><button id="refine">次の範囲の提案JSONを保存</button></div>
<p>提案JSONは新しいG-codeではありません。オフラインで再検証・準備するまで、新しい試験ファイルは生成されません。セルを選んでも通常の印刷設定は変えません。</p>
<p id="status" role="status"></p><pre id="paths"></pre>
<script>
let state=__STATE__,selected=null;
const el=id=>document.getElementById(id);
const labels={h_cmd_mm:'ノズル上げ量',final_volume_mm3_per_mm:'最終吐出量/長さ',retract_mm:'リトラクション量',wipe_mm:'ワイプ長',startup_extra_e_mm:'始端追加E',start_debt_unretract_speed_mm_s:'復帰速度',ceiling_reconcile_speed_mm_s:'上空復帰速度',print_speed_mm_s:'指令描画速度',print_speed_ratio:'元スライス基準の速度倍率'};
const label=key=>labels[key]||key;
function current(){return(state.trials||[]).find(t=>t.id===el('trial').value);}
function update(message){state=message;const previous=el('trial').value;el('trial').replaceChildren();for(const t of state.trials||[]){const o=document.createElement('option');o.value=t.id;o.textContent=t.title;el('trial').append(o);}if((state.trials||[]).some(t=>t.id===previous))el('trial').value=previous;show();}
function show(){const trial=current();el('status').textContent=state.reason||'';el('scope').textContent='元ソースの指定60キーのシリアライズ文字列を照合します。全設定の同一性・実際の材料挙動を保証する照合ではありません。未照合の任意継承5キーは適用範囲外です。';el('compatibility').textContent=state.compatible?'元ソースの必須キーに一致':'書き出し不可: '+(state.mismatched_keys||[]).join(', ');el('export').disabled=!trial||!state.compatible||state.busy;el('baseline_export').disabled=!trial||state.busy;el('refresh').disabled=!!state.busy;el('save').disabled=!trial||state.busy;el('refine').disabled=!trial||state.busy;el('grid').replaceChildren();if(!trial){el('baseline').textContent='準備済みデータは同梱されていません。';return;}const saved=(state.selections||{})[trial.id];selected=saved?.selected_cell??null;if(saved)el('symptom').value=saved.symptom;el('baseline').textContent='固定・仮基準: '+Object.entries(trial.baseline).filter(([k])=>!(trial.source_speed_reference&&k==='print_speed_mm_s')).map(([k,v])=>label(k)+' '+v).join(' / ')+(trial.source_speed_reference?' / 元ソース実効基準 '+trial.source_speed_reference.resolved_reference_speed_mm_s+' mm/s（実測速度ではありません）':'')+' / source '+trial.source_sha256;const header=document.createElement('tr');for(const text of ['行: '+label(trial.axes.rows.name)+' / 列: '+label(trial.axes.columns.name)+' ('+trial.axes.rows.unit+')',...trial.axes.columns.values.map(v=>trial.axes.columns.name==='print_speed_ratio'?String(Number(v)*100)+'%':v+' '+trial.axes.columns.unit)]){const th=document.createElement('th');th.textContent=text;header.append(th);}el('grid').append(header);for(let r=0;r<5;r++){const tr=document.createElement('tr'),th=document.createElement('th');th.textContent=trial.axes.rows.values[r]+' '+trial.axes.rows.unit;tr.append(th);for(let c=0;c<5;c++){const id=String(r*5+c+1).padStart(2,'0'),cell=trial.cells.find(v=>v.id===id),td=document.createElement('td'),b=document.createElement('button');b.textContent=id+'\nE '+(cell?.actual_E_mm??'—')+' mm'+(trial.source_speed_reference?'\n指令 '+cell.print_speed_mm_s+' mm/s':'');b.className=id===selected?'chosen':'';b.onclick=()=>{selected=id;for(const node of el('grid').querySelectorAll('button'))node.className=node===b?'chosen':'';el('symptom').value='acceptable';};td.append(b);tr.append(td);}el('grid').append(tr);}}
function send(command,extra={}){const trial=current();window.orca.postMessage({command,...(trial?{trial_id:trial.id}:{}),...extra});}
el('trial').onchange=show;el('refresh').onclick=()=>window.orca.postMessage({command:'calibration_refresh'});el('export').onclick=()=>send('calibration_export');el('baseline_export').onclick=()=>send('calibration_baseline_export');
function result(command){send(command,{cell_id:el('symptom').value==='none_acceptable'?null:selected,symptom:el('symptom').value});}
el('save').onclick=()=>result('calibration_save_selection');el('refine').onclick=()=>result('calibration_save_proposal');
window.orca.onMessage(message=>{if(message.state)update(message.state);if(message.reason)el('status').textContent=message.reason;if(message.paths)el('paths').textContent=message.paths.join('\n');});update(state);
</script></html>'''
