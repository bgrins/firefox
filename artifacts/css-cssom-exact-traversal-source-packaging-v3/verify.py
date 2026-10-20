import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise RuntimeError('Use python3 -I -S without optimization')
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
ROOT=Path(__file__).resolve().parent
sha=lambda data:hashlib.sha256(data).hexdigest()
if len(sys.argv) not in [3,4] or sys.argv[1]!='--files-sha256' or (len(sys.argv)==4 and sys.argv[3]!='--replay'):
    raise SystemExit('verify.py --files-sha256 PIN [--replay]')
raw=(ROOT/'FILES.json').read_bytes();assert sha(raw)==sys.argv[2]
files=json.loads(raw);paths=list(ROOT.rglob('*'));assert not any(f.is_symlink() for f in paths)
assert sorted(files)==sorted(str(f.relative_to(ROOT)) for f in paths if f.is_file() and str(f.relative_to(ROOT)) not in ['FILES.json','FREEZE.json'])
for name,pin in files.items():assert sha((ROOT/name).read_bytes())==pin
freeze=json.loads((ROOT/'FREEZE.json').read_text());assert freeze['files_sha256']==sys.argv[2] and freeze['payload_count']==len(files)
result=json.loads((ROOT/'NATIVE-WPT-CHECK.json').read_text())
proposal_raw=(ROOT/'PROPOSAL-FILES.json').read_bytes();assert sha(proposal_raw)=='7f38aefc3a57825eff20508e95d183ae571514f128958bb2d0033228e134d6b6'
proposal=json.loads(proposal_raw)
native=(ROOT/'native.patch').read_bytes();patch=(ROOT/'candidate-native-wpt.patch').read_bytes()
assert sha(native)==result['native_patch_sha256']==proposal['proposal.patch']=='2aa367b0531bf96a881ca62b8b89b9438f4bfcbe83bdc10fe2c3ef753dc1b9c1'
assert patch.startswith(native) and sha(patch)==result['five_file_patch_sha256']=='50dff765e3892ec22015c726be592aaa3d6f283913131c20789be46427cd2a33'
roster=[line[6:] for line in patch.decode().splitlines() if line.startswith('+++ b/')]
assert roster==result['paths'] and len(roster)==5
for path in roster[:-1]:assert sha((ROOT/'expected'/path).read_bytes())==proposal['candidate/'+Path(path).name]
assert sha((ROOT/'expected'/roster[-1]).read_bytes())==result['wpt_sha256']=='98514c1f71bd2d0e4af78a704a82b67175b1a33479bcf440de67f3e39baeb76e'
assert result['isolated_upstream_runtime']==result['main_tree_writes']==False
for base in result['results']:
    assert base['restored_exactly'] and base['new_test_absent'] and all(x['exit']==0 for x in base['stages'])
    role=base['role']
    for row in base['files']:
        path=row['path'];after=(ROOT/'applied'/role/path).read_bytes()
        assert sha(after)==row['after_sha256']
        assert (after==(ROOT/'expected'/path).read_bytes())==row['matches_reviewed_local_candidate']
        if row['before_sha256']:assert sha((ROOT/'bases'/role/path).read_bytes())==row['before_sha256']
    if len(sys.argv)==4:
        env=os.environ.copy()
        for key in ['GIT_DIR','GIT_WORK_TREE','GIT_INDEX_FILE','GIT_COMMON_DIR']:env.pop(key,None)
        with tempfile.TemporaryDirectory(prefix='traversal-v3-source-replay-') as td:
            private=Path(td);shutil.copytree(ROOT/'bases'/role,private,dirs_exist_ok=True)
            for stage,args in [('check',['--check']),('apply',[]),('reverse',['--reverse'])]:
                run=subprocess.run(['git','apply']+args+[str(ROOT/'candidate-native-wpt.patch')],cwd=private,env=env,capture_output=True,text=True)
                assert run.returncode==0,run.stderr
                expected=ROOT/'bases'/role if stage=='reverse' else ROOT/'applied'/role
                if stage!='check':
                    actual=sorted(str(f.relative_to(private)) for f in private.rglob('*') if f.is_file())
                    wanted=sorted(str(f.relative_to(expected)) for f in expected.rglob('*') if f.is_file());assert actual==wanted
                    assert all((private/name).read_bytes()==(expected/name).read_bytes() for name in wanted)
print(json.dumps({'payloads':len(files),'bases':2,'changed_files':5,'source_replay':len(sys.argv)==4,'status':'SOURCE_PACKAGING_PASS_NOT_NATIVE_ACCEPTANCE'}))
