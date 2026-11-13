import hashlib
import json
from pathlib import Path
import re

root = Path(__file__).resolve().parent
target = json.loads((root / 'TARGET.json').read_text())
attempt = root / 'attempt-1'
names = ['Target', 'div_negative', 'div_positive', 'factor_adjustment',
         'mul_negative', 'mul_positive', 'Provider', 'ConversionTarget', 'Witness',
         'Conversion', 'WeightTarget', 'Product', 'Addition', 'Weights',
         'ShareTarget', 'Share', 'DistributionTarget', 'Distribution', 'InputTarget', 'InputProof']
types = ['PromotionTarget', 'IntegerPromotionTarget', 'InputWeightTarget', 'InputListTarget',
         'InputDistributionTarget', 'InputWitnessTarget', 'FullInputTarget']
allowed = {'ClassicalDedekindReals.sig_not_dec',
           'ClassicalDedekindReals.sig_forall_dec',
           'FunctionalExtensionality.functional_extensionality_dep', 'Classical_Prop.classic'}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


for predecessor in [target['predecessor']]:
    name = Path(predecessor['path']).name
    base = root.parent / name
    assert digest(base / 'FILES.json') == predecessor['manifest_sha256']
    for relative, expected in json.loads((base / 'FILES.json').read_text()).items():
        assert digest(base / relative) == expected, (name, relative)
    for source, expected in predecessor['inputs'].items():
        assert digest(root / 'inputs' / source) == expected
        assert digest(base / 'inputs' / source) == expected
assert digest(root / target['source']) == target['sha256']
assert digest(attempt / 'inputs/InputTarget.v') == target['sha256']
rows = json.loads((attempt / 'output/RESULTS.json').read_text())
assert len(rows) == 21 and all(row['exit'] == 0 for row in rows)
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
proof = (root / 'inputs/InputProof.v').read_text()
for name, kind in zip(target['required_roots'], types):
    assert f'Theorem {name} : {kind}.' in proof
assert re.findall(r'^Print Assumptions (\w+)\.', proof, re.M) == target['required_roots']
blocks = (attempt / 'output/InputProof.stdout').read_text().split('Axioms:\n')
assert len(blocks) == 8
for block in blocks[1:]:
    assert set(re.findall(r'^([A-Za-z_][\w.]*)\s*(?=:|\n\s*:)', block, re.M)) == allowed
terminal = json.loads((attempt / 'TERMINAL.json').read_text())
assert terminal['exit'] == 0 and terminal['container_absent']
result = {'status': 'PASS encoded binary32 input and composed distribution target',
          'theorem_roots': target['required_roots'], 'commands': 21,
          'target_sha256': target['sha256'], 'proof_sha256': hashes['InputProof.v'],
          'free_space_domain_power_of_two': 60, 'envelope_error_power_of_two': 20,
          'count_limit': 4294967295, 'zero_and_whole_branches_checked': True,
          'binary32_encoded_inputs': True, 'integer_promotions_exact': True,
          'growth_negative_bases_admitted': True,
          'allowed_axioms': sorted(allowed),
          'native_correspondence_proved': False, 'lean_import_checked': False,
          'new_browser_bugs': 0}
(root / 'VALIDATION.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result))
