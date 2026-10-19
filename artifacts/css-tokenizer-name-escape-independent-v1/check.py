import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
p = argparse.ArgumentParser()
p.add_argument('--lean', type=Path, required=True)
p.add_argument('--output', type=Path, required=True)
a = p.parse_args()
f = json.loads((ROOT/'FREEZE.json').read_text())
assert sha(ROOT/'MANIFEST.json') == f['manifest_sha256']
m = json.loads((ROOT/'MANIFEST.json').read_text())
for name, digest in m.items():
    q = ROOT/name
    assert not q.is_symlink() and q.is_file() and sha(q) == digest, name
src = ROOT/'import'
assert sha(src/'FREEZE.json') == '47bc465615b4f25f05701b696da8dae622f8333f13d42cc15e2a061825456e48'
assert sha(src/'MANIFEST.json') == '03343c12289092567f619d0ddcdc0dde5f69bdeaf3782320d32ee8f7fbcdd666'
im = json.loads((src/'MANIFEST.json').read_text())
assert len(im) == 77
for name, digest in im.items():
    assert sha(src/name) == digest, name
lean = a.lean.resolve()
assert sha(lean) == 'd1d9c26a539f54fe839d2aa7760bf1ac1dd76a30b26e2c9684bebf2900038fcf'
out = a.output.resolve()
assert not out.exists()
out.mkdir(parents=True)
commands = []
def run(cmd, cwd):
    r = subprocess.run(cmd, cwd=cwd, env=dict(os.environ, LEAN_PATH=str(cwd), PYTHONDONTWRITEBYTECODE='1'), capture_output=True, text=True)
    commands.append(dict(cmd=cmd, cwd=str(cwd), exit=r.returncode, stdout=r.stdout, stderr=r.stderr))
    (out/'commands.json').write_text(json.dumps(commands, indent=2)+'\n')
    return r
r = run([sys.executable, str(src/'check.py'), '--lean', str(lean), '--output', str(out/'component')], out)
assert r.returncode == 0, r.stderr
modules = ['IdentifierStart','HexPrefix','Escape','Name','Boundary','EscapeBoundary','SemanticName','Caller','Witnesses']
diagnostic = out/'codec-diagnostic'
diagnostic.mkdir()
for name in modules:
    shutil.copyfile(src/'lean'/(name+'.lean'), diagnostic/(name+'.lean'))
q = diagnostic/'Escape.lean'
s = q.read_text()
before = 'if n < 128 then [byte n]'
after = 'if n < 128 then [byte (n + 1)]'
assert s.count(before) == 1
q.write_text(s.replace(before, after))
audits = []
for name in modules:
    r = run([str(lean), '-o', name+'.olean', name+'.lean'], diagnostic)
    assert r.returncode == 0, r.stdout+r.stderr
    found = re.findall(r"^'([^']+)' (?:depends on axioms: \[([^\]]*)\]|does not depend on any axioms)$", r.stdout+r.stderr, re.M)
    assert found, name
    for n, deps in found:
        assert set(filter(None, deps.split(', '))) <= {'propext','Classical.choice','Quot.sound'}, (n,deps)
    audits.extend(found)
assert len(audits) == 48
bad = out/'tampered'
bad.mkdir()
for name in [*im, 'MANIFEST.json', 'FREEZE.json']:
    q = bad/name
    q.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src/name, q)
q = bad/'lean/Name.lean'
q.write_bytes(q.read_bytes()+b'\n-- deliberate authentication test\n')
r = run([sys.executable, str(bad/'check.py'), '--lean', str(lean), '--output', str(out/'must-not-exist')], out)
assert r.returncode != 0 and 'lean/Name.lean' in r.stderr
assert not (out/'must-not-exist').exists()
result = dict(authenticated=len(m), component=json.loads((out/'component/RESULT.json').read_text()), shared_codec_diagnostic='expected all nine modules and 48 standard audits pass', tamper='rejected before output creation', status='conditional original-source component accepted; current-source transfer pending')
(out/'RESULT.json').write_text(json.dumps(result, indent=2)+'\n')
print(json.dumps(result))
