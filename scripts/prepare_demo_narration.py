"""Generate local macOS TTS narration for the final rubric-aligned script."""
from pathlib import Path
import subprocess,json
ROOT=Path(__file__).resolve().parents[1];out=ROOT/'presentation/extensions/video';out.mkdir(exist_ok=True)
s=(ROOT/'presentation/extensions/three-minute-script.md').read_text()
paras=[line[2:].strip('“”') for line in s.splitlines() if line.startswith('> ')]
assert len(paras)==4
chap=[]
for i,(para,duration,title) in enumerate(zip(paras,[40,45,50,45],['The challenge','A better investment decision','Working technology','From pilot to scale'])):
 spoken=para.replace('U-Net','you net').replace('Sentinel-2','Sentinel two').replace('RGB','R G B').replace('GPU','G P U').replace('TotalEnergies','Total Energies').replace('FlareWise','Flare Wise')
 (out/f'narration-{i}.txt').write_text(spoken)
 subprocess.run(['say','-v','Samantha','-r','145','-f',str(out/f'narration-{i}.txt'),'-o',str(out/f'narration-{i}.aiff')],check=True)
 chap.append({'title':title,'duration':duration,'text':para,'audio':f'narration-{i}.aiff'})
(out/'chapters.json').write_text(json.dumps(chap,indent=2)+'\n')
