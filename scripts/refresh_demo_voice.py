"""Replace only the narration track, preserving the original video bitstream."""
from pathlib import Path
import asyncio,json,subprocess,re,hashlib,shutil
import edge_tts,imageio_ffmpeg
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'presentation/extensions/video';FF=imageio_ffmpeg.get_ffmpeg_exe()
VOICE='en-US-AndrewMultilingualNeural'
def run(args):return subprocess.run([FF,'-hide_banner','-loglevel','error','-y',*args],check=True,capture_output=True,text=True)
def duration(p):
 s=subprocess.run([FF,'-i',str(p)],capture_output=True,text=True).stderr
 h,m,sec=map(float,re.search(r'Duration: (\d+):(\d+):([\d.]+)',s).groups());return h*3600+m*60+sec
async def main():
 chapters=json.loads((OUT/'chapters.json').read_text())
 async def render(i,c):
  spoken=c['text'].replace('U-Net','you net').replace('Sentinel-2','Sentinel two').replace('RGB','R G B').replace('GPU','G P U').replace('TotalEnergies','Total Energies').replace('FlareWise','Flare Wise')
  await edge_tts.Communicate(spoken,VOICE,rate=f'+{[4,16,8,27][i]}%').save(str(OUT/f'andrew-{i}.mp3'))
 await asyncio.gather(*(render(i,c) for i,c in enumerate(chapters)))
 info=[]
 for i,c in enumerate(chapters):
  d=duration(OUT/f'andrew-{i}.mp3');tempo=d/(c['duration']-1.2)
  run(['-i',str(OUT/f'andrew-{i}.mp3'),'-af',f'atempo={tempo},adelay=350|350,apad,atrim=0:{c["duration"]}', '-ar','48000','-ac','2',str(OUT/f'andrew-{i}.wav')])
  info.append({'chapter':i,'native_seconds':d,'tempo_adjustment':tempo,'timeline_seconds':c['duration']})
 (OUT/'andrew-list.txt').write_text(''.join(f"file 'andrew-{i}.wav'\n" for i in range(4)))
 run(['-f','concat','-safe','0','-i',str(OUT/'andrew-list.txt'),'-c:a','pcm_s16le',str(OUT/'narration-andrew.wav')])
 original=OUT/'FlareWise-3-minute-demo.mp4';backup=OUT/'previous-samantha.mp4'
 if not backup.exists():shutil.copy2(original,backup)
 run(['-i',str(original),'-i',str(OUT/'narration-andrew.wav'),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','192k','-t','179.967','-movflags','+faststart',str(OUT/'updated-voice.mp4')])
 def video_hash(path):return run(['-i',str(path),'-map','0:v:0','-c:v','copy','-f','hash','-hash','sha256','-']).stdout.strip()
 before=video_hash(original);after=video_hash(OUT/'updated-voice.mp4');assert before==after,(before,after)
 run(['-i',str(OUT/'updated-voice.mp4'),'-f','null','-'])
 (OUT/'updated-voice.mp4').replace(original)
 report=json.loads((OUT/'verification.json').read_text());report.update({'tts_voice':VOICE,'tts_provider':'Microsoft neural speech via edge-tts','sha256':hashlib.sha256(original.read_bytes()).hexdigest(),'bytes':original.stat().st_size,'visual_stream_unchanged':True,'visual_stream_hash':after,'voice_chapter_timing':info})
 for k in ['audio_mean_db','audio_peak_db']:report.pop(k,None)
 (OUT/'verification.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps({'voice':VOICE,'visual_stream_unchanged':True,'chapters':info},indent=2))
asyncio.run(main())
