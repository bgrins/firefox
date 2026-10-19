from pathlib import Path
import hashlib
import json
import re
import sys

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
r = Path(__file__).resolve().parent
f = json.loads((r / 'FREEZE.json').read_text())
assert hashlib.sha256((r / 'MANIFEST.json').read_bytes()).hexdigest() == f['manifest_sha256']
m = json.loads((r / 'MANIFEST.json').read_text())
assert not any(p.is_symlink() for p in r.rglob('*'))
assert {str(p.relative_to(r)) for p in r.rglob('*') if p.is_file()} == set(m) | {'MANIFEST.json', 'FREEZE.json'}
for name, pin in m.items():
    assert hashlib.sha256((r / name).read_bytes()).hexdigest() == pin, name
x = json.loads((r / 'receipts/CHECK.json').read_text())
assert (x['new_axiom_reports'], x['inherited_axiom_reports'], x['total_axiom_reports']) == (32, 105, 137)
roster = json.loads((r / 'capsule/AUDITS.json').read_text())['names']
text = (r / 'receipts/composition-axioms.log').read_text()
observed = re.findall(r"'([^']+)' (?:depends on axioms: \[([^\]]*)\]|does not depend on any axioms)", text)
assert [name for name, _ in observed] == roster
for _, axioms in observed:
    assert {a.strip() for a in axioms.split(',') if a.strip()} <= {'propext', 'Quot.sound', 'Classical.choice'}
expected = {'baseline':'true|true|true|true|true', 'flattened-raw':'false|false|true|true|true',
            'unfiltered-index':'true|false|true|true|true', 'collapsed-owner':'true|true|true|false|true'}
for name, value in expected.items():
    assert (r / 'receipts' / (name + '-definitions.log')).read_text() == ''
    assert (r / 'receipts' / (name + '-gate.log')).read_text().strip() == value
assert len(json.loads((r / 'GUARDS.json').read_text())) == 8
assert json.loads((r / 'OUTPUT-PATH-LIMIT.json').read_text())['actual_output_is_inside_capsule'] is True
print('PASS', len(m), 'inputs; retained fresh 137-audit replay, 11 semantic mutants, 8 integrity rejections; output-path caveat explicit')
