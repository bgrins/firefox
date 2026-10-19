import argparse
import hashlib
import json
import os
from pathlib import Path
import sys

BASE=Path(__file__).resolve().parent

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
def safe(name):
    p=Path(name)
    assert not p.is_absolute() and '..' not in p.parts and str(p)==name,name
    path=BASE/p
    assert not any(parent.is_symlink() for parent in [path,*path.parents] if parent!=BASE.parent),name
    return path

def authenticate(source_only,freeze_sha):
    freeze_file=BASE/'FREEZE.json'
    if freeze_sha:assert digest(freeze_file)==freeze_sha,'freeze identity mismatch'
    freeze=json.loads(freeze_file.read_text())
    assert digest(BASE/'SOURCE-MANIFEST.json')==freeze['sourceManifest'],'source manifest changed'
    assert digest(BASE/'FILES.json')==freeze['filesManifest'],'files manifest changed'
    source=json.loads((BASE/'SOURCE-MANIFEST.json').read_text())
    files=json.loads((BASE/'FILES.json').read_text())
    for name,pin in source.items():assert files[name]==pin,('source/full manifest disagreement',name)
    expected=source if source_only else files
    for name,pin in expected.items():
        path=safe(name)
        assert path.is_file() and digest(path)==pin,('input authentication failed',name)
    actual={str(p.relative_to(BASE)) for p in BASE.rglob('*') if p.is_file() or p.is_symlink()}
    allowed=set(files)|{'FREEZE.json','FILES.json'}
    assert actual<=allowed,('unlisted capsule input',sorted(actual-allowed))
    if not source_only:assert actual==allowed,('missing capsule files',sorted(allowed-actual))
    assert all(name in source for name in files if name.endswith(('.py','.lean','.rs','.cpp','.h')) and not name.startswith('results/'))
    return freeze,{'authenticated':len(expected),'sourceOnly':source_only}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--source-only',action='store_true')
    parser.add_argument('--freeze-sha')
    parser.add_argument('--replay',type=Path)
    parser.add_argument('--lean',type=Path)
    args=parser.parse_args()
    freeze,receipt=authenticate(args.source_only,args.freeze_sha)
    sys.dont_write_bytecode=True
    if args.replay:
        assert args.lean is not None,'--lean is required for replay'
        sys.path.insert(0,str(BASE))
        import replay
        result=replay.run(args.replay,args.lean)
        assert result['result_sha256']==freeze['semanticResult'],'replay semantic result changed'
        receipt['replay']=result
    print(json.dumps(receipt,indent=2))
if __name__=='__main__':main()
