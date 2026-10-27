import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys

assert sys.flags.isolated and sys.flags.no_site
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
read = lambda p: json.loads(p.read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
i = read(HERE / 'INPUTS.json')
for name, h in {**i['pins'], **i['references']}.items():
    assert sha(ROOT / name) == h, name
for name, h in read(HERE / 'INPUT-FILES.json').items():
    assert sha(HERE / name) == h, name
out = Path(sys.argv[1]).resolve()
out.mkdir(exist_ok=False)
prefix = '\n'.join(line for line in (ROOT / i['prefix']).read_text().splitlines()
                   if not line.startswith('#print axioms ')) + '\n'
source = prefix + '\n' + (HERE / 'ExtendedPolicy.lean').read_text()
env = {**os.environ, 'LEAN_NUM_THREADS':'2', 'LEAN_PATH':str(ROOT / i['library_objects'])}
def execute(name, body):
    path = out / (name + '.lean')
    try:
        path.write_text(body)
        r = subprocess.run([str(ROOT / i['compiler']), str(path)], cwd=ROOT,
            env=env, capture_output=True, text=True, timeout=60)
        log = r.stdout + r.stderr
        (out / (name + '.log')).write_text(log)
        return r.returncode, log
    finally:
        path.unlink(missing_ok=True)
code, log = execute('main', source)
assert code == 0 and 'error:' not in log and 'sorryAx' not in log
matches = re.findall(r"'([^']+)' (?:does not depend on any axioms|depends on axioms:\s*\[([^\]]*)\])", log)
assert [n for n,_ in matches] == read(HERE / 'AUDIT-NAMES.json')
axioms = {n:[a.strip() for a in s.split(',') if a.strip()] for n,s in matches}
assert all(set(v) <= {'propext','Classical.choice','Quot.sound'} for v in axioms.values())
negatives = {
 'viewport-public-destination':'example : code (.viewport .vw) ≤ 10 := by decide +kernel',
 'none-covers-viewport':'example : sufficient .style (.viewport .vw) .px .none := by unfold sufficient; decide +kernel',
 'style-covers-layout-profile':'example : sufficient .layout (.viewport .vw) .em .style := by unfold sufficient; decide +kernel',
 'stale-result-preserves':'example : Preserves (basis fresh) ⟨.viewport .vw, 10⟩ (.legacy .px) ⟨.legacy .px, 20⟩ := by unfold Preserves; decide +kernel',
}
rejected = {}
for name, claim in negatives.items():
    result, output = execute(name, source + '\nopen SvgLengthExtendedPolicy CssSemantics.UnitConversion\n' + claim + '\n')
    assert result != 0 and 'error:' in output and 'false' in output and 'decide' in output
    assert 'unknown identifier' not in output and 'unknown module' not in output
    rejected[name] = {'exit':result, 'false_claim_rejected':True}
for name, h in {**i['pins'], **i['references']}.items():
    assert sha(ROOT / name) == h, name
for name, h in read(HERE / 'INPUT-FILES.json').items():
    assert sha(HERE / name) == h, name
assert not list(out.glob('*.lean')) and not list(out.glob('*.olean'))
receipt = {'status':'PASS','audited_results':len(axioms),'axioms':axioms,'negative_controls':rejected,
 'threads':2,'prefix_body_reused':True,'prefix_existing_audits_not_recounted':True,
 'compiler_sha256':sha(ROOT / i['compiler']),'source_sha256':sha(HERE / 'ExtendedPolicy.lean'),
 'native_or_browser_bug_claim':False,'canonical_changed':False,'new_target_directory':False,
 'owned_temporary_sources_removed':True,'native_bodies_read_during_replay':False}
(out / 'CHECK.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({k:v for k,v in receipt.items() if k!='axioms'},indent=2))
