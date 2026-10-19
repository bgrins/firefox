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
    assert not q.is_symlink() and q.is_file() and sha(q) == h,n
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

run([sys.executable,str(ROOT/'bindings.py'),'--output',str(out/'SOURCE-BINDINGS.json')],out)
assert sha(out/'SOURCE-BINDINGS.json') == sha(ROOT/'SOURCE-BINDINGS.json')
records = json.loads((out/'SOURCE-BINDINGS.json').read_text())
assert len(records) == 21
for item in records:
    raw = (ROOT/item['source']).read_bytes()
    assert raw[item['byte_start']:item['byte_end']] == item['body'].encode()
    assert hashlib.sha256(item['body'].encode()).hexdigest() == item['sha256']
assert sha(ROOT/'source/cssparser/src/tokenizer.rs') == '9e46cbb4fc239301dc786cb76b3355b6d8c1ea2d19f845f142db8a6bca020b4f'
assert sha(ROOT/'source/cssparser/src/tokenizer.rs') == sha(ROOT/'dispatch-v2/source/cssparser/src/tokenizer.rs')
run([sys.executable,str(ROOT/'dispatch-v2/check.py'),'--lean',str(lean),'--output',str(out/'dispatch')],out)
modules = ['IdentifierStart','HexPrefix','Escape','Name','Boundary','EscapeBoundary','SemanticName','Caller','Witnesses']
proof = out/'proof'
proof.mkdir()
audits = []
for name in modules:
    src = ROOT/'lean'/(name+'.lean')
    assert not re.search(r'\b(sorry|admit|axiom|native_decide)\b',src.read_text())
    shutil.copyfile(src,proof/src.name)
    log = run([str(lean),'-o',name+'.olean',name+'.lean'],proof)
    found = re.findall(r"^'([^']+)' (?:depends on axioms: \[([^\]]*)\]|does not depend on any axioms)$",log,re.M)
    assert found,name
    for n,deps in found:
        assert set(filter(None,deps.split(', '))) <= {'propext','Classical.choice','Quot.sound'},(n,deps)
    audits.extend(found)
mutants = [('skip-continuation','Name','simple b || continuation b || fourIntro b','simple b || fourIntro b'),
           ('zero-not-replaced','Escape','if n = 0 then 65533','if n = 0 then 0'),
           ('CRLF-consumes-one','Escape','then 2 else 1','then 1 else 1'),
           ('seven-hex-digits','Escape','HexPrefix.run 6 xs 0','HexPrefix.run 7 xs 0')]
for label,module,before,after in mutants:
    source = (ROOT/'lean'/(module+'.lean')).read_text()
    assert source.count(before) == 1
    target = proof/(label+'.lean')
    target.write_text(source.replace(before,after))
    log = run([str(lean),target.name],proof,False)
    assert 'error:' in log
result = dict(authenticated=len(m),modules=len(modules),theorem_audits=len(audits),
              full_native_definitions=len(records),semantic_mutants=[x[0] for x in mutants],
              dispatch_invocations=22,dispatch_byte_decisions=5632,
              native_build='NOT RUN',source_correspondence='reviewed full-body projection, not compiler proof',
              primitive_boundaries=['Rust str validity and chars/len_utf8/encode_utf8/from_u32',
                                    'defined native position arithmetic','allocation and compiler',
                                    'line/column metadata outside projection'],
              known_identifier_start_bug='retained; separate repair capsule',
              whole_tokenizer='OPEN')
(out/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
