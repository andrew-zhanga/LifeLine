"""Download public Zenodo imagery in 8 verified resumable ranges; check published MD5."""
from pathlib import Path
import concurrent.futures, hashlib, time, requests
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'data/experiments/industrial-smoke'; OUT.mkdir(parents=True,exist_ok=True)
URL='https://zenodo.org/records/4250706/files/images.tar.gz'
SIZE=6359411128
N=8

def part(i):
 start=SIZE*i//N; end=SIZE*(i+1)//N-1; path=OUT/f'images.part{i}'
 for attempt in range(5):
  have=path.stat().st_size if path.exists() else 0
  if have==end-start+1:return path
  try:
   with requests.get(URL,headers={'Range':f'bytes={start+have}-{end}'},stream=True,timeout=(30,120)) as r:
    r.raise_for_status(); assert r.status_code==206
    assert r.headers['Content-Range'].startswith(f'bytes {start+have}-{end}/')
    with path.open('ab') as f:
     for b in r.iter_content(1024*1024):f.write(b)
   assert path.stat().st_size==end-start+1
   print(f'part {i+1}/{N} complete',flush=True);return path
  except Exception as e:
   print(f'part {i}: {e}',flush=True);time.sleep(min(60,5*2**attempt))
 raise RuntimeError(f'part {i} failed')

if __name__=='__main__':
 started=time.monotonic()
 with concurrent.futures.ThreadPoolExecutor(max_workers=N) as pool: parts=list(pool.map(part,range(N)))
 digest=hashlib.md5()
 with (OUT/'images.tar.gz').open('wb') as out:
  for p in parts:
   with p.open('rb') as f:
    while b:=f.read(8*1024*1024):out.write(b);digest.update(b)
 assert digest.hexdigest()=='d87992cf622920dc0135e16bac9e2cfd',digest.hexdigest()
 print({'md5':digest.hexdigest(),'seconds':time.monotonic()-started},flush=True)
