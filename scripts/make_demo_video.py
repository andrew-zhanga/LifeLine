"""Build a 180-second narrated demo from verified UI captures and recorded WebGL footage."""
from pathlib import Path
import subprocess,json,re,textwrap
from PIL import Image,ImageDraw,ImageFont,ImageOps
import imageio_ffmpeg
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'presentation/extensions/video';OUT.mkdir(exist_ok=True)
FF=imageio_ffmpeg.get_ffmpeg_exe(); FONT='/System/Library/Fonts/Supplemental/Arial.ttf';BOLD='/System/Library/Fonts/Supplemental/Arial Bold.ttf'
BG='#101d27';INK='#e7eef3';MUTED='#a8becb';MINT='#b8e3c6';AMBER='#efbd82'
def font(n,bold=False):return ImageFont.truetype(BOLD if bold else FONT,n)
def txt(d,xy,s,size=36,color=INK,bold=False):d.text(xy,s,font=font(size,bold),fill=color)
def base(kicker,title):
 im=Image.new('RGB',(1920,1080),BG);d=ImageDraw.Draw(im)
 txt(d,(80,42),'flarewise.',36,MINT,True);txt(d,(1450,52),'CLIMATE & HEALTH',21,MUTED)
 d.line((80,104,1840,104),fill='#34505d',width=2)
 txt(d,(90,165),kicker.upper(),25,AMBER,True);txt(d,(90,225),title,66,INK,True)
 return im,d
def card(name,kicker,title,rows,footer):
 im,d=base(kicker,title)
 y=355
 for big,small in rows:
  txt(d,(90,y),big,76,MINT,True);txt(d,(96,y+100),small,30,MUTED);y+=220
 txt(d,(90,1005),footer,22,MUTED);im.save(OUT/name)
def ui(name,source,title,sub):
 im=Image.new('RGB',(1920,1080),BG);d=ImageDraw.Draw(im)
 txt(d,(48,20),'flarewise.',30,MINT,True);txt(d,(280,22),title,30,INK,True)
 shot=Image.open(ROOT/source).convert('RGB');shot=ImageOps.contain(shot,(1824,922),Image.Resampling.LANCZOS)
 im.paste(shot,((1920-shot.width)//2,76+(922-shot.height)//2));txt(d,(48,1025),sub,24,MUTED);im.save(OUT/name)
card('01-problem.png','01 / Sustainability challenge','A valuable resource. Burned away.',[('$54 billion','Estimated value of gas flared worldwide in 2025'),('167 billion m³','Global flaring volume in 2025')],'Source: World Bank · Global Gas Flaring Tracker 2026 · Global context, not app impact')
card('02-health.png','01 / Climate and health','The people downwind matter.',[('50% higher odds','Preterm birth associated with high flaring exposure'),('Eagle Ford, South Texas','Published cohort study · 23,487 births · 2012–2015')],'Source: Cushing et al., Environmental Health Perspectives (2020) · Association, not causal attribution')
card('09-scale.png','04 / Pathways for scale','From one asset team to many basins.',[('Pilot → measure → expand','Operator costs + infrastructure constraints + local environmental validation'),('Gas recovered. Returns. Emissions.','Measure outcomes, then extend regional weather and population coverage.')],'Proposed adoption path · TotalEnergies routine-flaring commitment: 2030 · No partnership implied')
card('10-close.png','04 / The opportunity','Make every capture dollar count.',[('95.5% financial value retained','Balanced portfolio versus Financial · $10m budget'),('More than 2× index improvement','Population-weighted exposure index · 5.25% → 10.61%')],'FlareWise · Recover value. Put communities into the investment decision.')
ui('03-home.png','presentation/extensions/rehearsal/01-home.png','From global waste to local investment','Global discovery: 8,783 satellite-estimated sites across 77 countries · 2023 inventory')
ui('04-financial.png','presentation/screenshots/06-financial.png','Start with the financial case','$10m budget · Financial portfolio · Seven-year NPV and population-weighted index')
ui('05-balanced.png','presentation/extensions/rehearsal/06-closing-result.png','Retain value. Improve the community objective.','$32.13m seven-year NPV · 95.51% of Financial NPV · 10.61% index reduction')
ui('06-community.png','presentation/extensions/rehearsal/03-community.png','Choose whose exposure you prioritize','Real Census counts · Selected source locations · Tract-level attribution')
ui('07-satellite.png','presentation/extensions/screenshots/10-satellite-lab.png','A trained segmentation model, with held-out results','12-band Sentinel-2 U-Net · 374 held-out images · 47.1% foreground IoU')
ui('08-predictions.png','presentation/extensions/rehearsal/05-satellite-predictions.png','Inspect the actual predictions','Human masks and U-Net predictions · Labeled examples; aggregate test IoU is 47.1%')
chap=json.loads((OUT/'chapters.json').read_text())
def run(args):subprocess.run([FF,'-hide_banner','-loglevel','error','-y',*args],check=True)
def duration(p):
 s=subprocess.run([FF,'-i',str(p)],capture_output=True,text=True).stderr
 h,m,sec=map(float,re.search(r'Duration: (\d+):(\d+):([\d.]+)',s).groups());return h*3600+m*60+sec
for i,c in enumerate(chap):
 dur=duration(OUT/c['audio']);target=c['duration'];tempo=max(1,dur/(target-1.2))
 run(['-i',str(OUT/c['audio']),'-af',f'atempo={tempo},adelay=350|350,apad,atrim=0:{target}', '-ar','48000','-ac','2',str(OUT/f'audio-{i}.wav')])
(OUT/'audio-list.txt').write_text(''.join(f"file 'audio-{i}.wav'\n" for i in range(4)))
run(['-f','concat','-safe','0','-i',str(OUT/'audio-list.txt'),'-c:a','pcm_s16le',str(OUT/'narration.wav')])
# Chapters and scene durations exactly sum to 180 seconds.
shots=[('01-problem.png',13),('02-health.png',12),('03-home.png',15),('06-community.png',17),('04-financial.png',12),('05-balanced.png',10),('06-community.png',6),('scene',30),('07-satellite.png',12),('08-predictions.png',8),('05-balanced.png',15),('09-scale.png',18),('10-close.png',12)]
assert sum(d for _,d in shots)==180
if not (OUT/'flarewise-scene.webm').exists():print('Cards and narration ready; waiting for recorded scene.');raise SystemExit(0)
for i,(name,seconds) in enumerate(shots):
 dest=OUT/f'clip-{i:02}.mp4'
 if name=='scene':
  vf="scale=1800:920:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:color=0x101d27,setsar=1,drawtext=fontfile="+FONT+":text='Historical wind replay | Actual application capture':fontsize=32:fontcolor=0xe7eef3:x=60:y=25,drawtext=fontfile="+FONT+":text='Time-dependent puff transport | GPU-instanced rendering':fontsize=25:fontcolor=0xa8becb:x=60:y=1020"
  args=['-ss','5','-i',str(OUT/'flarewise-scene.webm'),'-vf',vf]
 else:args=['-loop','1','-i',str(OUT/name),'-vf','setsar=1']
 run([*args,'-t',str(seconds),'-an','-r','30','-c:v','libx264','-preset','veryfast','-crf','20','-pix_fmt','yuv420p',str(dest)])
(OUT/'video-list.txt').write_text(''.join(f"file 'clip-{i:02}.mp4'\n" for i in range(len(shots))))
run(['-f','concat','-safe','0','-i',str(OUT/'video-list.txt'),'-i',str(OUT/'narration.wav'),'-t','180','-c:v','copy','-c:a','aac','-b:a','192k','-movflags','+faststart',str(OUT/'FlareWise-3-minute-demo.mp4')])
# Optional subtitles: segment by sentence within each chapter, proportional to spoken words.
subs=[];num=1;start=0
for c in chap:
 sentences=re.split(r'(?<=[.!?])\s+',c['text']);total=sum(len(s.split()) for s in sentences);t=start+.35
 for sentence in sentences:
  length=(c['duration']-1.2)*len(sentence.split())/total
  def ts(v):
   ms=round(v*1000);return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02},{ms%1000:03}'
  subs.append(f'{num}\n{ts(t)} --> {ts(t+length)}\n'+textwrap.fill(sentence,95)+'\n');num+=1;t+=length
 start+=c['duration']
(OUT/'FlareWise-3-minute-demo.srt').write_text('\n'.join(subs))
print('Created',OUT/'FlareWise-3-minute-demo.mp4')
