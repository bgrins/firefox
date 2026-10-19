import hashlib
import json
from pathlib import Path
from collections import Counter

here = Path(__file__).resolve().parent
root = here.parents[1]
def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()
def read(name):
    return json.loads((here / name).read_text())
def rows(phase):
    raw = [json.loads(line) for line in (here / (phase + '.jsonl')).read_text().splitlines()]
    values = [e for e in raw if e.get('action') in {'test_status','test_end'}]
    receipt = read(phase + '-receipt.json')
    assert values == receipt['statuses']
    assert sum(e.get('action') == 'suite_end' for e in raw) == 1
    result = {(e['test'], e.get('subtest')):e['status'] for e in values}
    assert len(result) == len(values) == 192
    assert receipt['all_inputs_unchanged'] and receipt['pins_before'] == receipt['pins_after']
    assert receipt['absent_before'] == receipt['absent_after']
    return result, receipt
before, b = rows('baseline-v1')
after, a = rows('candidate-v1')
assert b['exit_code'] == 1 and a['exit_code'] == 0
assert before.keys() == after.keys()
assert Counter(before.values()) == {'PASS':175, 'FAIL':8, 'OK':9}
assert Counter(after.values()) == {'PASS':183, 'OK':9}
changes = [{'test':key[0], 'subtest':key[1], 'before':before[key], 'after':after[key]} for key in before if before[key] != after[key]]
assert len(changes) == 8 and all(x['before']=='FAIL' and x['after']=='PASS' for x in changes)
pin_changes = [key for key in b['pins_before'] if b['pins_before'][key] != a['pins_before'][key]]
expected = ['servo/components/style/custom_properties.rs','servo/components/style/properties/cascade.rs','servo/components/style/properties/mod.rs','objdir-full.noindex/dist/Nightly.app/Contents/MacOS/firefox','objdir-full.noindex/dist/Nightly.app/Contents/MacOS/XUL']
assert sorted(pin_changes) == sorted(expected)
assert a['absent_before'] == b['absent_before']
record = {'status':'PASS','baseline':dict(Counter(before.values())),'candidate':dict(Counter(after.values())),'improvements':changes,'unchanged_rows':184,'changed_pins':pin_changes,'inputs_stable':True,'raw_sha256':{n:sha(here/n) for n in ['baseline-v1.jsonl','candidate-v1.jsonl','baseline-v1-receipt.json','candidate-v1-receipt.json']},'scope':'Shared experimental tree; exact isolated patch checked separately. No clean-base build. Security WPT has support-gated branches.'}
(here/'ROOT-BROWSER-PAIR-v1.json').write_text(json.dumps(record,indent=2)+'\n')
acceptance = {'status':'ACCEPTED_SCOPED','repair':'attr-typed-fallback-eligibility','patch':{'path':str((here/'native-wpt-v1.patch').relative_to(root)),'sha256':sha(here/'native-wpt-v1.patch')},'browser_pair':sha(here/'ROOT-BROWSER-PAIR-v1.json'),'native_build_exit_code':0,'lint_exit_code':0,'lint_errors':0,'lint_warnings':2,'independent_review_freeze_sha256':sha(root/'artifacts/css-attr-typed-eligibility-independent-v1/FREEZE.json'),'model_commit':'bd97b69e209cc493200cbbb06bc88c50694c1723','formal_scope':'Existing generic-parser eligibility model: 15 audits and two rejected mutants. This native integration adds no Lean theorem and does not prove native parser or complete graph correctness.','source_scope':'Occurrence-specific primary syntax eligibility after readiness, sharing parser and originating property context with final substitution. Cache invalidity and taint publication preserved.','limits':['Shared experimental tree browser pairing; HEAD-isolated patch is not separately built.','Context tests exercise transport, not discriminating context-erasure counterexamples.','Full SCC scheduling, provider freshness and observer/native parser admissions remain open.','Additional parse work and reference-vector footprint are unmeasured.','Build monitor emitted nonfatal export KeyError; native build completed with exit 0.']}
(here/'ROOT-SCOPED-ACCEPTANCE-v1.json').write_text(json.dumps(acceptance,indent=2)+'\n')
print(json.dumps(record,indent=2))
