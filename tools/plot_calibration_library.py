"""Render actual frozen conditions, never a deposited-width prediction."""
from pathlib import Path
import json,sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
if len(sys.argv)!=2:raise SystemExit('Usage: python tools/plot_calibration_library.py PREPARED_DIRECTORY (requires matplotlib)')
folder=Path(sys.argv[1])
for stage in ('h_volume','retract_wipe','startup_extra_speed','volume_speed'):
 manifest=json.loads((folder/stage/'frozen-manifest.json').read_text())
 fig,ax=plt.subplots(figsize=(9,8));ax.set_aspect('equal');ax.set_xlim(56,124);ax.set_ylim(56,126)
 for cell in manifest['cells']:
  x=float(cell['start_x_mm']);y=float(cell['y_mm']);ax.plot([x,x+10],[y,y],lw=1.5,color='#146a85');ax.text(x+5,y+3,cell['id'],ha='center',fontsize=9)
  if stage=='h_volume':s=f"h={cell['h_cmd_mm']} A={cell['final_volume_mm3_per_mm']}"
  elif stage=='retract_wipe':s=f"R={cell['retract_mm']} W={cell['wipe_mm']}"
  elif stage=='startup_extra_speed':s=f"extraE={cell['startup_extra_e_mm']} v={cell['start_debt_unretract_speed_mm_s']}"
  else:
   s=f"A={cell['final_volume_mm3_per_mm']} v={cell['print_speed_mm_s']}"
   if 'print_speed_ratio' in cell:s+=f" ({100*float(cell['print_speed_ratio']):g}%)"
  ax.text(x+5,y-1.8,s,ha='center',fontsize=5.1)
 title=stage+' — 25 prepared lines; provisional baseline'
 if 'source_speed_reference' in manifest:title+='\nCommanded feed; source reference '+manifest['source_speed_reference']['resolved_reference_speed_mm_s']+' mm/s'
 ax.set_title(title,fontsize=12)
 ax.set_xlabel('World X (mm) — schematic line width, not physical width');ax.set_ylabel('World Y (mm)')
 fig.text(.5,.02,'Each line 10 mm; central 6 mm + 2 mm ends. Raw commanded E is authoritative. No print performed.',ha='center',fontsize=8)
 fig.savefig(folder/stage/'overview.png',dpi=150);plt.close(fig)
