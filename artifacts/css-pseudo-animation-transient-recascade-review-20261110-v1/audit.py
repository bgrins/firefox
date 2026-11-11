import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
SOURCE = ROOT / 'artifacts/css-pseudo-animation-transient-recascade-20261110-v1'
sha = lambda data: hashlib.sha256(data).hexdigest()
manifest = json.loads((SOURCE/'SOURCE-ONLY.json').read_text())
assert sha((SOURCE/'SOURCE-ONLY.json').read_bytes()) == '6aeedef5df63410009fd1e65f15aa2fd263a951b90f21fb9e15e90de86b744e3'
for name, expected in manifest.items():
    assert sha((SOURCE/name).read_bytes()) == expected, name
pins = json.loads((SOURCE/'SOURCES.json').read_text())
env = dict(os.environ, GIT_OPTIONAL_LOCKS='0', PYTHONDONTWRITEBYTECODE='1')
for name, expected in pins['files'].items():
    raw = subprocess.check_output(['git','-c','core.fsmonitor=false','show',pins['revision']+':'+name],cwd=ROOT,env=env)
    assert sha(raw)==expected and raw==(SOURCE/'source'/name).read_bytes(), name
with tempfile.TemporaryDirectory(prefix='recascade-independent-') as directory:
    scratch = Path(directory)
    copied = scratch/'copied'
    copied.mkdir()
    for name in manifest:
        target = copied/name; target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(SOURCE/name,target)
    checker = copied/'check.py'
    text = checker.read_text()
    assert text.count('ROOT = HERE.parent.parent') == 1
    checker.write_text(text.replace('ROOT = HERE.parent.parent','ROOT = Path('+repr(str(ROOT))+')'))
    transformed_hash = sha(checker.read_bytes())
    result = subprocess.run([sys.executable,'-B',str(checker)],cwd=ROOT,env=env,capture_output=True,text=True)
    (HERE/'copied-check.log').write_text(result.stdout+result.stderr)
    assert result.returncode==0, result.stderr
    shutil.copytree(copied/'verification',HERE/'copied-verification')
    tree = scratch/'tree'
    shutil.copytree(SOURCE/'prerequisite',tree)
    inventory=lambda: {p.relative_to(tree).as_posix():sha(p.read_bytes()) for p in tree.rglob('*') if p.is_file()}
    before=inventory()
    for direction in ['forward','reverse']:
        cmd=['git','apply'] + (['--reverse'] if direction=='reverse' else []) + [str(SOURCE/'extension.patch')]
        r=subprocess.run(cmd,cwd=tree,env=env,capture_output=True,text=True)
        (HERE/(direction+'-patch.log')).write_text(r.stdout+r.stderr)
        assert r.returncode==0,r.stderr
        if direction=='forward':
            expected={p.relative_to(SOURCE/'candidate').as_posix():sha(p.read_bytes()) for p in (SOURCE/'candidate').rglob('*') if p.is_file()}
            assert inventory()==expected
        else: assert inventory()==before
for name,expected in manifest.items(): assert sha((SOURCE/name).read_bytes())==expected,name
report={'status':'PASS','source_manifest':sha((SOURCE/'SOURCE-ONLY.json').read_bytes()),'authenticated_inputs':len(manifest),
 'git_objects':len(pins['files']),'copied_checker_root_only_amendment_sha256':transformed_hash,
 'exact_forward_reverse_inventory':True,'copied_source_checker':True,'scratch_removed':not scratch.exists(),
 'native_build':False,'browser_execution':False}
(HERE/'AUDIT.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
