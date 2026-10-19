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
p.add_argument('--lean',type=Path,required=True)
p.add_argument('--output',type=Path,required=True)
a = p.parse_args()
f = json.loads((ROOT/'FREEZE.json').read_text())
assert sha(ROOT/'MANIFEST.json') == f['manifest_sha256']
m = json.loads((ROOT/'MANIFEST.json').read_text())
for n,h in m.items():
    q = ROOT/n
    assert q.is_file() and not q.is_symlink() and sha(q) == h,n
for key,(_,mh,fh) in json.loads((ROOT/'PARENTS.json').read_text()).items():
    d = ROOT/'inputs'/key
    assert sha(d/'MANIFEST.json') == mh and sha(d/'FREEZE.json') == fh
    for n,h in json.loads((d/'MANIFEST.json').read_text()).items():
        assert sha(d/n) == h,(key,n)
lean = a.lean.resolve()
assert sha(lean) == 'd1d9c26a539f54fe839d2aa7760bf1ac1dd76a30b26e2c9684bebf2900038fcf'
out = a.output.resolve()
assert not out.exists()
out.mkdir(parents=True)
commands = []
def run(cmd,cwd,success=True):
    r = subprocess.run(cmd,cwd=cwd,env=dict(os.environ,LEAN_PATH=str(cwd),PYTHONDONTWRITEBYTECODE='1'),capture_output=True,text=True)
    commands.append(dict(cmd=cmd,cwd=str(cwd),exit=r.returncode,stdout=r.stdout,stderr=r.stderr))
    (out/'commands.json').write_text(json.dumps(commands,indent=2)+'\n')
    assert (r.returncode == 0) == success,commands[-1]
    return r.stdout+r.stderr

name = ROOT/'inputs/name'
repair = ROOT/'inputs/repair'
rel = Path('third_party/rust/cssparser/src/tokenizer.rs')
assert sha(ROOT/'current'/rel) == '8a5925e228e5838ef6afcaf165b27037cf48d0daa31f0bef3d42338c30ff51ab'
assert (ROOT/'current'/rel).read_bytes() == (repair/'candidate'/rel).read_bytes()
assert (ROOT/'current/third_party/rust/cssparser/.cargo-checksum.json').read_bytes() == (repair/'candidate/third_party/rust/cssparser/.cargo-checksum.json').read_bytes()
assert (ROOT/'current/third_party/rust/cssparser/src/parser.rs').read_bytes() == (name/'source/cssparser/src/parser.rs').read_bytes()
old = (name/'lean/IdentifierStart.lean').read_text()
new = (repair/'lean/IdentifierStart.lean').read_text()
assert old[:old.index('def reference ')] == new[:new.index('def reference ')]
source_tree = out/'current-source-binding'
source_tree.mkdir()
for file in ['bindings.py','rust_reader.py']:
    shutil.copyfile(name/file,source_tree/file)
target = source_tree/'source/cssparser/src/tokenizer.rs'
target.parent.mkdir(parents=True)
shutil.copyfile(ROOT/'current'/rel,target)
run([sys.executable,str(source_tree/'bindings.py'),'--output',str(out/'CURRENT-BINDINGS.json')],out)
before = json.loads((name/'SOURCE-BINDINGS.json').read_text())
after = json.loads((out/'CURRENT-BINDINGS.json').read_text())
assert len(before) == len(after) == 21
changed = []
for x,y in zip(before,after):
    assert x['name'] == y['name']
    if x['body'] != y['body']:
        changed.append(x['name'])
        assert x['name'] == 'is_ident_start'
        assert y['body'] == x['body'].replace('has_newline_at(1)','has_newline_at(2)',1)
assert changed == ['is_ident_start']
parser = (ROOT/'current/third_party/rust/cssparser/src/parser.rs').read_text()
metadata = 'pub(crate) fn advance_line_number(&mut self, count: u32) {\n        self.line_number_and_block_type += count << Self::BLOCK_TYPE_BITS;\n    }'
assert metadata in parser and 'const BLOCK_TYPE_BITS: u32 = 2;' in parser
(out/'METADATA-BINDING.json').write_text(json.dumps(dict(body=metadata,body_sha256=hashlib.sha256(metadata.encode()).hexdigest(),parser_sha256=sha(ROOT/'current/third_party/rust/cssparser/src/parser.rs'),normal_return_headroom='explicit admission, not derived from all input lengths'),indent=2)+'\n')

proof = out/'proof'
proof.mkdir()
modules = ['IdentifierStart','HexPrefix','Escape','Name','Boundary','EscapeBoundary','SemanticName','Caller','Witnesses','Integration']
audits = []
for n in modules:
    src = name/'lean'/(n+'.lean')
    if n == 'IdentifierStart': src = repair/'lean/IdentifierStart.lean'
    if n == 'Integration': src = ROOT/'lean/Integration.lean'
    assert not re.search(r'\b(sorry|admit|axiom|native_decide)\b',src.read_text())
    shutil.copyfile(src,proof/src.name)
    log = run([str(lean),'-o',n+'.olean',n+'.lean'],proof)
    found = re.findall(r"^'([^']+)' (?:depends on axioms: \[([^\]]*)\]|does not depend on any axioms)$",log,re.M)
    assert found,n
    for theorem,deps in found:
        assert set(filter(None,deps.split(', '))) <= {'propext','Classical.choice','Quot.sound'},(theorem,deps)
    audits.extend(found)
assert len(audits) == 57
mutation = (ROOT/'lean/Integration.lean').read_text()
mutation += '\nexample : IdentifierStart.corrected [45,92,10] = true := by decide\n'
(proof/'invalid-reverse-transfer.lean').write_text(mutation)
log = run([str(lean),'invalid-reverse-transfer.lean'],proof,False)
assert 'error:' in log
result = dict(authenticated=len(m),modules=10,theorem_audits=57,new_integration_audits=5,
              current_full_tokenizer_bindings=21,additional_metadata_binding=1,
              changed_function=changed,transfer='corrected approval implies original approval',
              invalid_reverse_transfer_rejected=True,ownership='native projection only; independent ownership semantics not proved',
              metadata='normal-return/headroom admission remains explicit',
              native_build='NOT RUN',whole_tokenizer='OPEN')
(out/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
