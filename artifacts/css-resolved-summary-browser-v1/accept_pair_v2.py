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
    assert len(result) == len(values) == 239
    assert receipt['all_inputs_unchanged'] and receipt['pins_before'] == receipt['pins_after']
    assert receipt['absent_before'] == receipt['absent_after']
    return result, receipt
before, b = rows('baseline-v1')
after, a = rows('candidate-v2')
assert b['exit_code'] == 1 and a['exit_code'] == 0
assert before.keys() == after.keys()
assert Counter(before.values()) == {'PASS':214, 'FAIL':13, 'OK':12}
assert Counter(after.values()) == {'PASS':227, 'OK':12}
changes = [{'test':key[0], 'subtest':key[1], 'before':before[key], 'after':after[key]} for key in before if before[key] != after[key]]
assert len(changes) == 13 and all(x['before']=='FAIL' and x['after']=='PASS' for x in changes)
pin_changes = [key for key in b['pins_before'] if b['pins_before'][key] != a['pins_before'][key]]
expected = ['servo/components/style/custom_properties.rs','objdir-full.noindex/dist/Nightly.app/Contents/MacOS/firefox','objdir-full.noindex/dist/Nightly.app/Contents/MacOS/XUL']
assert sorted(pin_changes) == sorted(expected)
assert a['absent_before'] == b['absent_before']
assert set(a['pins_before']) - set(b['pins_before']) == {'artifacts/css-resolved-summary-browser-v1/run_wpt_v2.py'}
assert not set(b['pins_before']) - set(a['pins_before'])
record = {'status':'PASS','baseline':dict(Counter(before.values())),'candidate':dict(Counter(after.values())),'improvements':changes,'unchanged_rows':226,'changed_pins':pin_changes,'inputs_stable':True,'raw_sha256':{n:sha(here/n) for n in ['baseline-v1.jsonl','candidate-v2.jsonl','baseline-v1-receipt.json','candidate-v2-receipt.json']},'remaining_failures':[{'test':key[0],'subtest':key[1]} for key in after if after[key]=='FAIL'],'scope':'All 13 baseline failures repaired. Conditional Lean composition does not prove the actual tokenizer or full graph. Incomplete scans retain previous empty metadata. Shared experimental tree; exact isolated patch checked separately. No clean-base build. Security WPT has support-gated branches.'}
(here/'ROOT-BROWSER-PAIR-v2.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(record,indent=2))
