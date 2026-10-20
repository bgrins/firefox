import hashlib,json,shutil,subprocess,sys,tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent
SOURCE=HERE.parent/'css-flex-table-caption-cache-proof-v1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
pins={'FILES.json':'b26c6dc88281b9e7a571967a4edc308cda864446780886f3d5d3fb2d415734d0','FREEZE.json':'09e8eb00a86735a78273561f331d422e1b90f3382a19fc21bbdfa4c669b605dc','check.py':'77a2ec98548b6819920358332ccf331adedf3a80b08d25b9dc41d2f1a18f6870'}
for n,h in pins.items():assert sha(SOURCE/n)==h,n
files=json.loads((SOURCE/'FILES.json').read_text())
assert {str(p.relative_to(SOURCE)) for p in SOURCE.rglob('*') if p.is_file()}==set(files)|{'FILES.json','FREEZE.json'}
for n,h in files.items():assert sha(SOURCE/n)==h,n
(HERE/'AUTH.json').write_text(json.dumps({'capsule':str(SOURCE),'external_pins':pins,'payload_files':len(files)},indent=2)+'\n')
with tempfile.TemporaryDirectory(prefix='css-caption-root-relocation-') as tmp:
 target=Path(tmp)/'source';target.mkdir()
 for n in set(files)|{'FILES.json','FREEZE.json'}:
  dst=target/n;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(SOURCE/n,dst)
 command=[sys.executable,'-I','-S',str(target/'check.py'),'--output',str(HERE/'replay')]
 with (HERE/'replay.log').open('w') as log:result=subprocess.run(command,cwd=target,stdout=log,stderr=subprocess.STDOUT)
 (HERE/'RUN.json').write_text(json.dumps({'command':command,'exit':result.returncode,'manifest_only_relocation':True},indent=2)+'\n')
 assert result.returncode==0
print((HERE/'replay/RESULT.json').read_text())
