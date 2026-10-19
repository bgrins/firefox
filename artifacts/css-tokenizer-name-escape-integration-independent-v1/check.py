import argparse
import hashlib
import json
from pathlib import Path
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
for n,h in m.items():
    q = ROOT/n
    assert q.is_file() and not q.is_symlink() and sha(q) == h,n
src = ROOT/'import'
assert sha(src/'FREEZE.json') == '05f22e47825a0a85d6c90b9e782556ec79b7bea6babb9d83ccb07d9e60ccc58e'
assert sha(src/'MANIFEST.json') == 'b0ee6d8fd601c2045c978b6de84d5dac76a2745eda2a23ea498faeca1b5e5709'
im = json.loads((src/'MANIFEST.json').read_text())
assert len(im) == 166
for n,h in im.items():
    assert sha(src/n) == h,n
old = (src/'inputs/name/source/cssparser/src/tokenizer.rs').read_text()
new = (src/'current/third_party/rust/cssparser/src/tokenizer.rs').read_text()
before = "b'\\\\' => !parser.has_newline_at(1),"
after = "b'\\\\' => !parser.has_newline_at(2),"
before = '\n                    ' + before
after = '\n                    ' + after
assert old.count(before) == 1 and old.replace(before,after) == new
assert (src/'inputs/name/source/cssparser/src/parser.rs').read_bytes() == (src/'current/third_party/rust/cssparser/src/parser.rs').read_bytes()
lean = a.lean.resolve()
assert sha(lean) == 'd1d9c26a539f54fe839d2aa7760bf1ac1dd76a30b26e2c9684bebf2900038fcf'
out = a.output.resolve()
assert not out.exists()
r = subprocess.run([sys.executable,str(src/'check.py'),'--lean',str(lean),'--output',str(out)],capture_output=True,text=True)
assert r.returncode == 0,r.stdout+r.stderr
result = json.loads((out/'RESULT.json').read_text())
assert result['new_integration_audits'] == 5 and result['theorem_audits'] == 57
assert result['invalid_reverse_transfer_rejected']
(out/'INDEPENDENT.json').write_text(json.dumps(dict(authenticated=len(m),whole_source_delta='exact one-offset change',verdict='conditional corrected-guard transfer accepted',component=result),indent=2)+'\n')
print((out/'INDEPENDENT.json').read_text())
