import sys
sys.dont_write_bytecode=True
import hashlib,json,stat
from pathlib import Path

def seal(root):
    files=[]
    for p in sorted(root.rglob('*')):
        mode=p.lstat().st_mode
        if stat.S_ISDIR(mode):continue
        if not stat.S_ISREG(mode):raise RuntimeError('nonregular '+str(p))
        name=str(p.relative_to(root))
        if name in ['FILES.json','FREEZE.json']:continue
        files.append({'path':name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
    (root/'FILES.json').write_text(json.dumps({'files':files},indent=2)+'\n')
    pin=hashlib.sha256((root/'FILES.json').read_bytes()).hexdigest()
    (root/'FREEZE.json').write_text(json.dumps({'files_sha256':pin,'files':len(files),'status':'frozen'},indent=2)+'\n')
    return pin
if __name__=='__main__':print(seal(Path(sys.argv[1]).resolve()))
