from pathlib import Path
import contextlib
import hashlib
import io
import json
import re
import runpy
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
P = HERE.parent / 'css-grid-baseline-padding-producer-20261112-v1'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_text())
assert sha(P / 'FILES.json') == 'a5e14e9a9cd833c1bf0d0ae0c2f09d2e6d444e172c2261d72dd14811060ac1ba'
manifest = read(P / 'FILES.json')
assert len(manifest) == 35
for name, record in manifest.items():
    assert sha(P / name) == record['sha256'], name
    assert (P / name).stat().st_size == record['bytes']
assert sha(P / 'Target.lean') == '9d76de313cfe68d0b1a7f364f8ba526ed8a00be66e0700260573c78928c39668'
assert sha(P / 'TARGET-FREEZE.json') == '283c8db357e9a690d063e7103c38b94eb4d269a4dc182e1ff217f577ceafa036'
output = io.StringIO()
with contextlib.redirect_stdout(output):
    runpy.run_path(str(P / 'check.py'), run_name='retained_review')
result = json.loads(output.getvalue())
assert result == {k: v for k, v in read(P / 'CHECKS.json').items() if k in result}
target = (P / 'Target.lean').read_text()
proof = (P / 'Proof.lean').read_text()
strength = (P / 'Strength.lean').read_text()
assert proof.startswith(target) and strength.startswith(proof)
def declarations(text):
    return {name: ' '.join(signature.split()) for name, signature in
            re.findall(r'^theorem (\w+)\s*:(.*?)\s*:=', text, re.M | re.S)}
assert declarations((P / 'proof-1/Proof.lean').read_text()) == declarations(proof)
fields = re.findall(r'^  (\w+) : ', target, re.M)
assert len(fields) == 16 and set(declarations(proof)) == set(fields + ['complete'])
mutants = ['removing_clamp_breaks_range', 'moving_clamp_breaks_last', 'retaining_zero_breaks_presence']
names = fields + ['complete'] + mutants
lines = (P / 'proof-2/strength.log').read_text().splitlines()
audits = []
for name, line in zip(names, lines, strict=True):
    match = re.fullmatch(r"'BaselinePadding\." + name + r"' (?:does not depend on any axioms|depends on axioms: \[([^\]]*)\])", line)
    assert match, line
    axioms = [] if match[1] is None else match[1].split(', ')
    assert set(axioms) <= {'propext', 'Classical.choice', 'Quot.sound'}
    if name.endswith('_witness') or name in mutants:
        assert not axioms
    audits.append(dict(name=name, axioms=axioms))
assert len(audits) == 20
assert 'sorryAx' in (P / 'proof-1/proof.log').read_text()
assert 'sorryAx' not in (P / 'proof-2/strength.log').read_text()
print(json.dumps(dict(status='PASS independent retained proof review', files=35,
                     unchanged_theorem_statements=True, exact_target_prefix=True,
                     audits=audits, receipt_replay=result,
                     failed_attempt_credit=False, fresh_kernel_execution=False,
                     native_refinement=False, protected_comparator=False), indent=2))
