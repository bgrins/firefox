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
f = json.loads((ROOT / 'FREEZE.json').read_text())
assert sha(ROOT / 'MANIFEST.json') == f['manifest_sha256']
m = json.loads((ROOT / 'MANIFEST.json').read_text())
for n, h in m.items():
    q = ROOT / n
    assert not q.is_symlink() and q.is_file() and sha(q) == h, n
lean = a.lean.resolve()
assert sha(lean) == 'd1d9c26a539f54fe839d2aa7760bf1ac1dd76a30b26e2c9684bebf2900038fcf'
out = a.output.resolve()
assert not out.exists()
out.mkdir(parents=True)
commands = []
def run(cmd, cwd, success=True):
    r = subprocess.run(cmd, cwd=cwd, env=dict(os.environ, LEAN_PATH=str(out)), capture_output=True, text=True)
    commands.append(dict(cmd=cmd, cwd=str(cwd), exit=r.returncode, stdout=r.stdout, stderr=r.stderr))
    (out / 'commands.json').write_text(json.dumps(commands, indent=2) + '\n')
    assert (r.returncode == 0) == success, commands[-1]
    return r.stdout + r.stderr

ids = json.loads((ROOT / 'IDENTITIES.json').read_text())
rel = Path('third_party/rust/cssparser/src/tokenizer.rs')
old = (ROOT / 'original' / rel).read_text()
new = (ROOT / 'candidate' / rel).read_text()
a0 = old.index('fn is_ident_start(')
b0 = old.index('\nfn consume_ident_like', a0)
body = old[a0:b0]
assert body.count('has_newline_at(1)') == 2
assert new == old[:a0] + body.replace('has_newline_at(1)', 'has_newline_at(2)', 1) + old[b0:]
assert sha(ROOT / 'original' / rel) == ids['original_tokenizer']
assert sha(ROOT / 'candidate' / rel) == ids['candidate_tokenizer']
checksum = Path('third_party/rust/cssparser/.cargo-checksum.json')
c0 = json.loads((ROOT / 'original' / checksum).read_text())
c1 = json.loads((ROOT / 'candidate' / checksum).read_text())
assert c0['files']['src/tokenizer.rs'] == ids['original_tokenizer']
c0['files']['src/tokenizer.rs'] = ids['candidate_tokenizer']
assert c0 == c1 and c1['package'] is None
shutil.copytree(ROOT / 'original', out / 'patch-tree')
run(['patch', '-p1', '--batch', '-i', str(ROOT / 'native.patch')], out / 'patch-tree')
for n in [rel, checksum]:
    assert sha(out / 'patch-tree' / n) == sha(ROOT / 'candidate' / n)
run(['patch', '-p1', '--batch', '-R', '-i', str(ROOT / 'native.patch')], out / 'patch-tree')
for n in [rel, checksum]:
    assert sha(out / 'patch-tree' / n) == sha(ROOT / 'original' / n)

run([sys.executable, str(ROOT / 'dispatch-v2/check.py'), '--lean', str(lean), '--output', str(out / 'dispatch-baseline')], out)
dispatch = out / 'candidate-dispatch'
shutil.copytree(ROOT / 'dispatch-v2', dispatch)
shutil.copyfile(ROOT / 'candidate' / rel, dispatch / 'source/cssparser/src/tokenizer.rs')
run([sys.executable, str(dispatch / 'extract.py'), '--output', str(out / 'candidate-tables')], out)
tables0 = json.loads((ROOT / 'dispatch-v2/generated/INVOCATIONS.json').read_text())
tables1 = json.loads((out / 'candidate-tables/INVOCATIONS.json').read_text())
assert len(tables0) == len(tables1) == 22
changed = []
for i, (x, y) in enumerate(zip(tables0, tables1)):
    assert x['path'] == y['path']
    assert [z['pattern'] for z in x['arms']] == [z['pattern'] for z in y['arms']]
    assert x['table'] == y['table']
    if x['invocation_sha256'] != y['invocation_sha256']:
        changed.append(i)
assert len(changed) == 2
assert sha(ROOT / 'dispatch-v2/generated/CurrentInvocations.lean') == sha(out / 'candidate-tables/CurrentInvocations.lean')
shutil.copyfile(ROOT / 'lean/IdentifierStart.lean', out / 'IdentifierStart.lean')
s = (out / 'IdentifierStart.lean').read_text()
assert not re.search(r'\b(sorry|admit|axiom|native_decide)\b', s)
log = run([str(lean), '-o', 'IdentifierStart.olean', 'IdentifierStart.lean'], out)
audits = re.findall(r"^'([^']+)' (?:depends on axioms: \[([^\]]*)\]|does not depend on any axioms)$", log, re.M)
assert len(audits) == 8
for n, deps in audits:
    assert set(filter(None, deps.split(', '))) <= {'propext', 'Classical.choice', 'Quot.sound'}, (n, deps)
start = s.index('def corrected ')
end = s.index('\ntheorem ascii_classification', start)
mutations = [('restore-wrong-offset', '!newlineAt input 2', '!newlineAt input 1'),
             ('change-outer-offset', '!newlineAt input 1', '!newlineAt input 2')]
for name, before, after in mutations:
    segment = s[start:end]
    assert segment.count(before) == 1
    mutant = s[:start] + segment.replace(before, after) + s[end:]
    target = out / (name + '.lean')
    target.write_text(mutant)
    log = run([str(lean), target.name], out, False)
    assert 'error:' in log

browser = ROOT / 'evidence/browser'
assert json.loads((browser / 'baseline-before.json').read_text()) == json.loads((browser / 'baseline-after.json').read_text())
receipt = json.loads((browser / 'baseline-result.json').read_text())
assert receipt['counts'] == {'FAIL': 4, 'PASS': 7}
assert receipt['raw_sha256'] == sha(browser / 'baseline-raw.jsonl')
raw = [json.loads(x) for x in (browser / 'baseline-raw.jsonl').read_text().splitlines()]
statuses = [x for x in raw if x.get('action') == 'test_status']
assert len(statuses) == 11
assert sum(x['status'] == 'FAIL' for x in statuses) == 4
assert all(x['message'] == 'assert_equals: surviving rule count expected 0 but got 1' for x in statuses if x['status'] == 'FAIL')
assert sha(ROOT / 'wpt/identifier-start-escaped-newline.html') == ids['wpt']
result = dict(authenticated=len(m), predicate_theorem_audits=8, retained_dispatch_audits=8,
              candidate_invocations=22, unchanged_dispatch_decisions=5632, changed_nested_invocations=changed,
              predicate_mutants_rejected=[x[0] for x in mutations], patch_apply_reverse=True,
              vendor_checksum_exact=True, baseline={'FAIL': 4, 'PASS': 7},
              native_build='NOT RUN', candidate_browser='ROOT GATE', full_name_escape='OPEN',
              Rust_to_Lean='reviewed exact-source correspondence, not compiler verification')
(out / 'RESULT.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result))
