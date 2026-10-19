import sys
assert sys.flags.isolated and sys.flags.no_site
import hashlib
import json
import re
from pathlib import Path, PurePosixPath
R = Path(__file__).resolve().parent

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def read(p):
    return json.loads(p.read_text())

def authenticate(root, rows):
    names = set()
    for row in rows:
        name = row['path']
        rel = PurePosixPath(name)
        assert str(rel) == name and not rel.is_absolute() and '..' not in rel.parts
        assert name not in names
        names.add(name)
        assert sha(root / name) == row['sha256'], name
    assert not any(p.is_symlink() for p in root.rglob('*'))
    assert {p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file()} == names | {'MANIFEST.json', 'FREEZE.json'}
    return len(names)

own = authenticate(R, read(R / 'MANIFEST.json'))
p = R.parent / 'css-declaration-publication-proof-v1'
assert sha(p / 'FREEZE.json') == 'ccadac40732e9de66705ac9b6331af767be04b8e69a6d5ea5fd07123e478998d'
assert sha(p / 'MANIFEST.json') == '2e8ed98ebbefbf49e2a4067a6544e1c0e96f2ffe44f57decaf06032dc282ee1e'
assert authenticate(p, read(p / 'MANIFEST.json')) == 235
assert sha(p / 'check.py') == '21bb17a10280a749fd37e6064488031eb219911153451b59072c3cf1828a98eb'
assert sha(p / 'lean/Publication.lean') == 'aec090751671091de50d8a42b53a3058684c13890a6351268bae25f5c511cd7d'
names = read(R / 'THEOREMS.json')
assert len(names) == len(set(names)) == 29
assert names == read(p / 'THEOREMS.json')
source = (p / 'lean/Publication.lean').read_text()
assert names == ['Publication.' + n for n in re.findall(r'^theorem\s+(\w+)', source, re.M)]
assert not re.search(r'\b(sorry|axiom|admit|native_decide)\b', source)
e = R / 'evidence'
axioms = (e / 'AXIOMS.txt').read_text()
for name in names:
    assert axioms.count("'" + name + "'") == 1
assert axioms.count('depends on axioms:') + axioms.count('does not depend on any axioms') == 29
for group in re.findall(r'depends on axioms:\s*\[([^\]]*)\]', axioms):
    assert set(re.findall(r'[A-Za-z_][\w.]*', group)) <= {'propext', 'Quot.sound', 'Classical.choice'}
for path in ['COMMANDS.json', 'native/COMMANDS.json']:
    assert all(r['exit'] == 0 for r in read(e / path))
variants = ['original', 'candidate', 'clear-declarations-only', 'clear-fast-path', 'clear-after-publication']
observations = {}
for variant in variants:
    observations[variant] = [json.loads(x) for x in (e / 'native' / (variant + '.jsonl')).read_text().splitlines()]
    assert len(observations[variant]) == 16
    assert (e / 'native' / (variant + '.jsonl')).read_bytes() == (p / 'receipts/native' / (variant + '.jsonl')).read_bytes()
    records = read(e / 'native' / (variant + '-bindings.json'))
    assert len(records) == 21 and all(r['complete'] for r in records)
    assert records == read(p / 'receipts/native' / (variant + '-bindings.json'))
old = observations['original']; new = observations['candidate']
assert sum(a != b for a,b in zip(old[:13],new[:13])) == 4
assert old[0]['scratch'] == ['ordinary','with-variables'] and new[0]['scratch'] == ['with-variables']
assert new[13] == {'mode':'failure-declarations','helper_ok':False,'declarations':[],'all_present':False}
assert new[14] == {'mode':'failure-all','helper_ok':False,'declarations':[],'all_present':False}
assert observations['clear-declarations-only'][14] == dict(new[14], all_present=True)
assert new[4]['value'] == 'none' and new[4]['scratch'] == ['ordinary']
assert observations['clear-fast-path'][4] == dict(new[4], scratch=[])
assert observations['clear-after-publication'][0] == dict(new[0], scratch=[])
for rows in observations.values():
    assert rows[15] == {'mode':'drain','drained':['ordinary'],'all_drained':True,'empty_after':True}
result = read(e / 'RESULT.json')
assert result['theorems'] == 29 and result['source_only']
assert len(result['mutation_witnesses']) == 4
for witness in result['mutation_witnesses']:
    assert witness['kernel_witness'] in names
    assert witness['control'] == new[witness['row']]
    assert witness['mutant'] == observations[witness['variant']][witness['row']]
    assert witness['control'] != witness['mutant']
controls = read(e / 'TAMPER.json')
assert {r['case'] for r in controls} == {'shadow','changed-model','symlink','duplicate','escape'}
assert all(r['exit'] != 0 and not r['output_created'] and not r['stdout'] and 'AssertionError' in r['stderr'] for r in controls)
assert sha(p / 'evidence/discovery/evidence/candidate-properties.rs') == '2ef96482f50b06dcf87a18abc4d1a9aa0109a9063aa71cadc53e7737022c094d'
print(json.dumps({'review_inputs':own,'producer_inputs':235,'theorems':29,'native_variants':5,'rows_per_variant':16,'semantic_mutants':4,'tamper_rejections':5,'recommendation':'accept conditional publication component'}))
