import difflib
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = 'e63fc6b1892bc13f4d0f6583e4efc4b58d1e54db'
sha = lambda b: hashlib.sha256(b).hexdigest()
env = dict(os.environ, GIT_OPTIONAL_LOCKS='0')
def git(*args):
    return subprocess.check_output(['git', '-c', 'core.fsmonitor=false', *args], cwd=ROOT, env=env)
scope = json.loads((ROOT / 'artifacts/css-revert-rule-c-delivery-prerequisites-v1/DELIVERY-SCOPE.json').read_text())
sources = {
    'servo/components/style/properties/cascade.rs': 'artifacts/css-revert-rule-owner-map-dedup-candidate-v1/candidate/servo/components/style/properties/cascade.rs',
    'servo/components/style/stylist.rs': 'artifacts/css-revert-rule-cold-membership-diagnostic-v1/candidate/servo/components/style/stylist.rs',
}
sources.update({n:r['source'] for n,r in scope['tests'].items()})
expected = {
    'servo/components/style/properties/cascade.rs': 'cac13ba7ff2bbdfd54b906d7854a8ba703c2b013770ed4d121eb6b16af1bed6e',
    'servo/components/style/stylist.rs': 'fd5ded7d96e15b16caacd03bc758da255333bdbed9b99bb4bc65bc6a1900b9b3',
}
expected.update({n:r['candidate_sha256'] for n,r in scope['tests'].items()})
base, candidate, probes, patch = {}, {}, {}, []
for name, source in sources.items():
    body = (ROOT/source).read_bytes()
    assert sha(body) == expected[name]
    candidate[name] = body
    tracked = bool(git('ls-tree', '--name-only', BASE, '--', name).strip())
    base[name] = git('show', BASE+':'+name) if tracked else None
    output = HERE/'candidate'/name
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(body)
    patch.extend(difflib.unified_diff((base[name] or b'').decode().splitlines(True), body.decode().splitlines(True), fromfile='a/'+name if tracked else '/dev/null', tofile='b/'+name))
    if name in scope['tests']:
        live = ROOT/name
        current = live.read_bytes() if live.exists() else None
        row = {'exists':current is not None, 'tracked_at_HEAD':bool(git('ls-tree','--name-only','HEAD','--',name).strip()), 'sha256':sha(current) if current is not None else None, 'matches_delivery':current == body}
        if current is not None and current != body:
            saved=HERE/'preserved-working-tests'/name
            saved.parent.mkdir(parents=True,exist_ok=True)
            saved.write_bytes(current)
            row['preserved_copy']=str(saved.relative_to(ROOT))
        probes[name]=row
(HERE/'C-after-163.patch').write_text(''.join(patch))
with (HERE/'CHECK.log').open('w') as log:
    def run(command,cwd=None):
        log.write('$ '+' '.join(map(str,command))+'\n');log.flush()
        subprocess.run(list(map(str,command)),cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True)
    run(['rustfmt','--config-path',ROOT/'servo/rustfmt.toml','--check',*[HERE/'candidate'/n for n in sources if n.endswith('.rs')]])
    with tempfile.TemporaryDirectory(prefix='css-cac13-delivery-',dir='/private/tmp') as temp:
        for n,b in base.items():
            if b is not None:
                p=Path(temp)/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
        run(['patch','-p1','--fuzz=0','--batch','-i',HERE/'C-after-163.patch'],temp)
        assert all((Path(temp)/n).read_bytes()==b for n,b in candidate.items())
        run(['patch','-R','-p1','--fuzz=0','--batch','-i',HERE/'C-after-163.patch'],temp)
        assert all((Path(temp)/n).read_bytes()==b if b is not None else not (Path(temp)/n).exists() for n,b in base.items())
(HERE/'CHECK.json').write_text(json.dumps({'prerequisite_commit':BASE,'candidate_hashes':expected,'base_hashes':{n:sha(b) if b is not None else None for n,b in base.items()},'current_working_WPT':probes,'configured_rustfmt':True,'patch_forward_reverse_exact_zero_fuzz':True,'patch_sha256':sha((HERE/'C-after-163.patch').read_bytes()),'scratch_removed':True,'production_adoption':False,'native_validation_by_this_check':False,'callback_scope':{'C':72,'substitution':20,'D_before':48,'D_after':64,'additional':108}},indent=2)+'\n')
print(json.dumps(probes,indent=2))
