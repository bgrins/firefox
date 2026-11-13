import hashlib
import json
from pathlib import Path
import re

root = Path(__file__).resolve().parent
predecessor = root.parent / 'css-flex-finite-weight-sum-coq-20261111-v1'
target = json.loads((root / 'TARGET.json').read_text())
attempt = root / 'attempt-3'
names = ['WeightTarget', 'Product', 'Addition', 'Weights', 'ShareTarget', 'Share']
types = ['MonotoneTarget', 'IdempotentTarget', 'SumDominatesTarget', 'ShareTarget',
         'ScaledTarget', 'ZeroTarget', 'WitnessTarget', 'FullShareTarget']
allowed = {'ClassicalDedekindReals.sig_not_dec',
           'ClassicalDedekindReals.sig_forall_dec',
           'FunctionalExtensionality.functional_extensionality_dep', 'Classical_Prop.classic'}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


assert digest(predecessor / 'FILES.json') == '9f925c2b4e2f49dab51c80681e51da80f3f6ead86bf5c0a01a946515e07d6b8c'
for name, expected in json.loads((predecessor / 'FILES.json').read_text()).items():
    assert digest(predecessor / name) == expected, name
assert digest(root / target['source']) == target['sha256']
assert digest(attempt / 'inputs/ShareTarget.v') == target['sha256']
for name, expected in target['predecessor_sources'].items():
    assert digest(root / 'inputs' / name) == expected
    assert digest(predecessor / 'inputs' / name) == expected
rows = json.loads((attempt / 'output/RESULTS.json').read_text())
assert len(rows) == 7 and all(row['exit'] == 0 for row in rows)
hashes = {}
for name, row in zip(names, rows):
    source = attempt / 'inputs' / (name + '.v')
    hashes[source.name] = digest(source)
    assert source.read_bytes() == (root / 'inputs' / source.name).read_bytes()
    assert row['command'] == ['coqc', '-q', source.name]
    assert row['input_sha256'] == {source.name: hashes[source.name]}
    assert not re.search(r'\b(?:Abort|Admitted|admit|Axiom|Hypothesis)\b', source.read_text())
    assert not (attempt / 'output' / (name + '.stderr')).read_text()
assert rows[-1]['command'] == ['coqchk', '-silent'] + names
assert rows[-1]['input_sha256'] == hashes
assert not (attempt / 'output/coqchk.stderr').read_text()
proof = (root / 'inputs/Share.v').read_text()
for name, kind in zip(target['required_roots'], types):
    assert f'Theorem {name} : {kind}.' in proof
assert re.findall(r'^Print Assumptions (\w+)\.', proof, re.M) == target['required_roots']
blocks = (attempt / 'output/Share.stdout').read_text().split('Axioms:\n')
assert len(blocks) == 9
for block in blocks[1:]:
    assert set(re.findall(r'^([A-Za-z_][\w.]*)\s*(?=:|\n\s*:)', block, re.M)) == allowed
terminal = json.loads((attempt / 'TERMINAL.json').read_text())
assert terminal['exit'] == 0 and terminal['container_absent']
result = {'status': 'PASS full finite representable-weight share target',
          'theorem_roots': target['required_roots'], 'commands': 7,
          'target_sha256': target['sha256'], 'proof_sha256': hashes['Share.v'],
          'count_limit': 4294967295, 'denominator_upper_bound_power_of_two': 192,
          'rounded_share_interval': [0, 1], 'representability_explicit': True,
          'allowed_axioms': sorted(allowed),
          'native_correspondence_proved': False, 'lean_import_checked': False,
          'new_browser_bugs': 0}
(root / 'VALIDATION.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result))
