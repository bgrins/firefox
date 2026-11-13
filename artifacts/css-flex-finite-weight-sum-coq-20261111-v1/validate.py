import hashlib
import json
from pathlib import Path
import re

root = Path(__file__).resolve().parent
target = json.loads((root / 'TARGET.json').read_text())
attempt = root / 'attempt-2'
names = ['WeightTarget', 'Product', 'Addition', 'Weights']
types = ['ProductTarget', 'AdditionTarget', 'OrderedTarget', 'PrefixTarget',
         'FactorSumTarget', 'FullWeightTarget']
allowed = {'ClassicalDedekindReals.sig_not_dec',
           'ClassicalDedekindReals.sig_forall_dec',
           'FunctionalExtensionality.functional_extensionality_dep', 'classic'}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


assert digest(root / target['source']) == target['sha256']
assert digest(attempt / 'inputs/WeightTarget.v') == target['sha256']
rows = json.loads((attempt / 'output/RESULTS.json').read_text())
assert len(rows) == 5 and all(row['exit'] == 0 for row in rows)
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
proof = (root / 'inputs/Weights.v').read_text()
for name, kind in zip(target['required_roots'], types):
    assert f'Theorem {name} : {kind}.' in proof
assert re.findall(r'^Print Assumptions (\w+)\.', proof, re.M) == target['required_roots']
blocks = (attempt / 'output/Weights.stdout').read_text().split('Axioms:\n')
assert len(blocks) == 7
for block in blocks[1:]:
    assert set(re.findall(r'^([A-Za-z_][\w.]*)\s*(?=:|\n\s*:)', block, re.M)) == allowed
generation = json.loads((root / 'GENERATION.json').read_text())
assert [row['name'] for row in generation['queries']] == ['Product', 'Addition']
for row in generation['queries']:
    assert row['exit'] == 0
    assert digest(root / 'queries' / (row['name'] + '.g')) == row['query_sha256']
    assert digest(root / 'generated' / (row['name'] + '.v')) == row['certificate_sha256']
assert (root / 'generated/Product.v').read_bytes() == (root / 'inputs/Product.v').read_bytes()
raw = (root / 'generated/Addition.v').read_text()
expected = raw.replace('Require Import Gappa.Gappa_library.',
                       'Require Import Reals Ring Gappa.Gappa_library.').replace(
    'Hypothesis a1 : r1 = r6.',
    'Lemma a1 : r1 = r6.\nProof. unfold r1, r6, r7, _raw. ring. Qed.')
assert expected == (root / 'inputs/Addition.v').read_text()
revision = json.loads((root / 'DESIGN-REVISION.json').read_text())
assert digest(root / 'design-1/WeightTarget.v') == revision['before_sha256']
assert target['sha256'] == revision['after_sha256']
terminal = json.loads((attempt / 'TERMINAL.json').read_text())
assert terminal['exit'] == 0 and terminal['container_absent']
result = {'status': 'PASS full finite-weight and ordered-prefix target',
          'theorem_roots': target['required_roots'], 'commands': 5,
          'target_sha256': target['sha256'], 'proof_sha256': hashes['Weights.v'],
          'count_limit': 4294967295, 'prefix_upper_bound_power_of_two': 192,
          'raw_intermediate_upper_bound_power_of_two': 193,
          'allowed_axioms': sorted(allowed), 'rewrite_hypotheses_discharged': 1,
          'native_correspondence_proved': False, 'lean_import_checked': False,
          'new_browser_bugs': 0}
(root / 'VALIDATION.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result))
