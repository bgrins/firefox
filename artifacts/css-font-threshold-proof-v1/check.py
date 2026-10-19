import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

BASE=Path(__file__).resolve().parent


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--manifest-sha256',required=True)
    parser.add_argument('--out',required=True)
    parser.add_argument('--source-only-replay',action='store_true')
    args=parser.parse_args()
    manifest=BASE/'INPUTS-v1.json'
    assert sha(manifest)==args.manifest_sha256,'input manifest identity differs'
    records=json.loads(manifest.read_text())
    for rel,expected in records['files'].items():
        path=Path(rel)
        assert not path.is_absolute() and '..' not in path.parts
        target=BASE/path
        assert target.resolve().is_relative_to(BASE) and not target.is_symlink(),rel
        assert sha(target)==expected,rel
    out=Path(args.out).resolve()
    assert out!=BASE and not BASE.is_relative_to(out),'output must not contain authenticated input root'
    out.mkdir(parents=True,exist_ok=True)
    print('Authenticated',len(records['files']),'source-only inputs',flush=True)
    if args.source_only_replay:
        isolated=Path(tempfile.mkdtemp(prefix='font-B-inputs-',dir=out))
        for rel in list(records['files'])+['INPUTS-v1.json','check.py']:
            target=isolated/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(BASE/rel,target)
        command=[sys.executable,'-I',str(isolated/'check.py'),'--manifest-sha256',args.manifest_sha256,'--out',str(out/'isolated-results')]
        env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1');env.pop('PYTHONPATH',None)
        with (out/'source-only.log').open('w') as log:
            result=subprocess.run(command,cwd=isolated,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=1800)
        receipt=dict(status='PASS' if result.returncode==0 else 'FAIL',exit=result.returncode,input_manifest_sha256=args.manifest_sha256,input_count=len(records['files']),checker_sha256=sha(BASE/'check.py'),isolated_input_path=str(isolated),excluded=['historical receipts','development logs and binaries','live Gecko checkout sources','design sibling artifacts'],external_dependencies=['pinned Lean executable and its standard library','pinned clang executable and SDK','Python standard library'])
        (out/'SOURCE-ONLY-v1.json').write_text(json.dumps(receipt,indent=2)+'\n')
        assert result.returncode==0,'source-only replay failed; see source-only.log'
        print(json.dumps(receipt,indent=2));return
    sys.path.insert(0,str(BASE))
    import run
    import mutations
    sys.argv=['run.py','--out',str(out/'native-lean')];run.main()
    sys.argv=['mutations.py','--out',str(out/'mutations')];mutations.main()
    result=dict(status='PASS',input_manifest_sha256=args.manifest_sha256,input_count=len(records['files']),checker_sha256=sha(BASE/'check.py'),python=sys.version,python_executable=sys.executable)
    (out/'REPLAY-v1.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
