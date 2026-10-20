import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise RuntimeError('Use python3 -I -S without optimization')
sys.dont_write_bytecode=True
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
ROOT=Path(__file__).resolve().parent

def closed(root,pin):
    raw=(root/'FILES.json').read_bytes()
    assert hashlib.sha256(raw).hexdigest()==pin
    files=json.loads(raw)
    paths=list(root.rglob('*'))
    assert not any(f.is_symlink() for f in paths)
    allowed_dirs={str(parent) for name in files for parent in Path(name).parents if str(parent)!='.'}
    assert all(str(f.relative_to(root)) in allowed_dirs for f in paths if f.is_dir())
    assert sorted(files)==sorted(str(f.relative_to(root)) for f in paths if f.is_file() and str(f.relative_to(root)) not in ['FILES.json','FREEZE.json'])
    for name,pin in files.items():assert hashlib.sha256((root/name).read_bytes()).hexdigest()==pin
    return len(files)

if len(sys.argv)!=4 or sys.argv[1]!='--files-sha256':
    raise SystemExit('replay.py --files-sha256 PIN NEW_ABSOLUTE_OUTPUT')
closed(ROOT,sys.argv[2])
closed(ROOT/'producer','6af2a8ca93ea6129c2c37384e373bd1a9e65aa50ac0f8aa16dfbca4e99dfdfc5')
out=Path(sys.argv[3]);assert out.is_absolute() and not out.exists() and not out.is_symlink()
out=out.resolve();assert out!=ROOT and ROOT not in out.parents
chain=json.loads((ROOT/'producer/TOOLCHAIN.json').read_text());lean=Path(chain['lean'])
assert hashlib.sha256(lean.read_bytes()).hexdigest()==chain['sha256']
out.mkdir(parents=True)
receipts=[]
with tempfile.TemporaryDirectory(prefix='primary-callback-review-kernel-') as td:
    work=Path(td);env=os.environ.copy();env['LEAN_PATH']=str(work);env.pop('LEAN_OPTS',None)
    for name in ['Deletion','PropertyPhase','Witnesses','Challenges']:
        src=ROOT/'Challenges.lean' if name=='Challenges' else ROOT/'producer/lean'/(name+'.lean')
        command=[str(lean),'-o',str(work/(name+'.olean')),str(src)]
        ran=subprocess.run(command,cwd=src.parent,env=env,capture_output=True,text=True)
        (out/(name+'.stdout')).write_text(ran.stdout);(out/(name+'.stderr')).write_text(ran.stderr)
        receipts.append({'module':name,'exit':ran.returncode,'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'command':command})
        (out/'COMMANDS.json').write_text(json.dumps(receipts,indent=2)+'\n')
        assert ran.returncode==0 and not ran.stderr,(name,ran.stdout,ran.stderr)
    expected=['sample_has_nonempty_unbuffered_items','incomplete_buffer_encoding_is_admitted','other_owner_survives_with_freed_shared_cache','second_owner_cleanup_rejects_freed_shared_cache']
    audit=(out/'Challenges.stdout').read_text()
    for name in expected:
        assert "'IndependentReview."+name+"' does not depend on any axioms" in audit
    assert len(audit.splitlines())==4
closed(ROOT,sys.argv[2])
result={'status':'PASS','independent_kernel_boundary_witnesses':4,'axioms':[],'source_admissions':'decoder completeness and global ownership are not discharged','compiler_products_removed':True}
(out/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
