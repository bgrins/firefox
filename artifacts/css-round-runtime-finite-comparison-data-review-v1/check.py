from collections import Counter
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
DATA = ROOT / 'artifacts/css-round-runtime-finite-comparison-data-v1'
BASE = ROOT / 'artifacts/css-round-numerical-baseline-runtime-v1'
OLD = ROOT / 'artifacts/css-counter-additive-install-runtime-v1'
PLAN = ROOT / 'artifacts/css-round-numerical-baseline-plan-v2'
INSTALL = ROOT / 'artifacts/css-counter-additive-install-plan-v1'
read = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
refs = read(DATA / 'REFERENCES.json')
refs['artifacts/css-round-runtime-finite-comparison-data-v1/FILES.json'] = 'a885b08993116b58f786484fe217b6f0bd62b0705cb516e53f26313243f31c09'
refs['artifacts/css-round-numerical-baseline-terminal-review-v1/FILES.json'] = '34f469c07bcc45acf493d3e3dc2e9623b2ee34e2f7fd1efdd1b84e8bb93c955c'
for name, digest in refs.items():
    assert name.startswith('artifacts/') and '..' not in Path(name).parts
    p = ROOT / name
    assert sha(p) == digest
    if p.name == 'FILES.json':
        for member, value in read(p).items():
            assert not Path(member).is_absolute() and '..' not in Path(member).parts
            assert sha(p.parent / member) == value
roster = read(DATA / 'ROSTER.json')
old_roster = read(INSTALL / 'WPT-ROSTER.json')
new_roster = read(PLAN / 'ROSTER.json')
assert not set(old_roster['expected_subtests']) & set(new_roster)
assert roster['expected_subtests'] == {**old_roster['expected_subtests'], **new_roster}
assert roster['reftests'] == old_roster['reftests']
assert roster['tests'] == list(roster['expected_subtests']) + roster['reftests']
assert len(set(roster['tests'])) == 43 and len(roster['expected_subtests']) == 35
assert sum(map(len, roster['expected_subtests'].values())) == 1484
rows = []
for p in [OLD / 'wpt-installed/raw.json', BASE / 'wpt-diagnostic/raw.json']:
    for line in p.read_bytes().splitlines():
        e = json.loads(line)
        if e['action'] == 'test_status' or (e['action'] == 'test_end' and e['test'] in roster['reftests']):
            rows.append({'test': e['test'], 'subtest': e.get('subtest'), 'status': e['status'],
                         'message': e.get('message'), 'expected': e.get('expected'),
                         'effective_expected': e.get('expected', e['status']),
                         'known_intermittent': e.get('known_intermittent', [])})
archived = read(DATA / 'ARCHIVED-OUTCOMES.json')
key = lambda r: (r['test'], r['subtest'])
assert len({key(r) for r in rows}) == len(rows) == 1492
assert {key(r): r for r in rows} == {key(r): r for r in archived}
assert Counter(r['status'] for r in rows if r['subtest'] is not None) == {'PASS': 1408, 'FAIL': 76}
mandatory = read(DATA / 'MANDATORY.json')
assert mandatory['installed_mandatory'] == read(INSTALL / 'MANDATORY-ROSTER.json')
assert sum(map(len, mandatory['installed_mandatory']['subtests'].values())) == 159
assert mandatory['parse_guard_included'] is False and mandatory['no_executable_waivers'] is True
fixtures = read(DATA / 'FIXTURES.json')
families = read(PLAN / 'CLASSIFICATION.json')['families']
for variant, family, count in [('runtime_nan_only', 'runtime_nan', 8), ('finite_zero_only', 'finite_pow', 4)]:
    test, item = next((t, f) for t, f in fixtures.items() if f['family'] == family)
    required = mandatory['candidate_families'][variant]
    assert required['required_pass'] == {test: new_roster[test]}
    assert required['required_repairs'] == [{'test': test, 'subtest': n} for n in families[family]['target_names']]
    assert len(required['required_repairs']) == count
    assert all(next(r for r in rows if key(r) == (v['test'], v['subtest']))['status'] == 'FAIL'
               for v in required['required_repairs'])
combined = mandatory['candidate_families']['combined_optional']
assert combined['required_repairs'] == mandatory['candidate_families']['runtime_nan_only']['required_repairs'] + mandatory['candidate_families']['finite_zero_only']['required_repairs']
assert combined['preservation_bases'] == ['baseline', 'runtime_nan_only', 'finite_zero_only']
pins = read(DATA / 'RESTORATION-PINS.json')
assert pins == read(BASE / 'FINAL-PINS.json') and len(pins) == 605
ownership = read(DATA / 'OWNERSHIP.json')
assert ownership['installed_identities'] == read(BASE / 'FINAL.json')['installed_tests']
assert len(ownership['installed_identities']) == 21
owned = ownership['temporary_fixtures']
assert len(owned) == 6
assert set(owned) == {'testing/web-platform/tests' + t for t in roster['tests'] if pins['testing/web-platform/tests' + t] is None}
for name, item in owned.items():
    assert pins[name] is item['baseline'] is item['final'] is None
    assert sha(ROOT / item['source']) == item['sha256'] == ownership['temporary_phase_overlay'][name]
assert ownership['strict_baseline_absences'] == [n for n, h in read(BASE / 'FINAL-PINS.json').items() if h is None]
assert set(ownership['phase_permanent_absences']) == {n for n, h in pins.items() if h is None} - set(owned)
for test, item in fixtures.items():
    assert sha(DATA / item['local']) == item['sha256']
    original = next(f for f in read(PLAN / 'FIXTURES.json') if '/' + f['wpt_relative'] == test)
    assert item['sha256'] == original['sha256'] and item['names'] == original['names']
epoch = read(DATA / 'EPOCH.json')
assert epoch['ready_for_execution'] is False and epoch['baseline_terminal_review'] is None
assert epoch['future_runtime'] is epoch['future_session'] is None
assert epoch['source_snapshot'] == read(BASE / 'FINAL.json')['snapshot']
assert epoch['baseline_manifest'] == sha(BASE / 'FILES.json')
assert epoch['baseline_root_receipt'] == sha(BASE / 'ROOT-FINAL-CHECK.json')
source = 'servo/components/style/values/generics/calc.rs'
maps = read(DATA / 'SOURCE-MAPS.json')['source_maps']
assert maps['baseline'] == epoch['source_snapshot']['sources'] and len(maps['baseline']) == 72
assert sha(DATA / 'original' / source) == maps['baseline'][source]
for variant in ['runtime_nan_only', 'finite_zero_only', 'combined']:
    assert maps[variant] == dict(maps['baseline'], **{source: sha(DATA / 'candidate' / variant / source)})
records = []
with tempfile.TemporaryDirectory(prefix='round-data-peer-') as directory:
    scratch = Path(directory)
    subprocess.run(['git', 'init', '-q', str(scratch)], check=True, capture_output=True)
    target = scratch / source
    target.parent.mkdir(parents=True)
    original = (DATA / 'original' / source).read_bytes()
    target.write_bytes(original)

    def apply(name, reverse=False):
        args = ['git', 'apply', *(['--reverse'] if reverse else [])]
        for check in [True, False]:
            p = subprocess.run([*args, *(['--check'] if check else []), str(DATA / name)],
                               cwd=scratch, check=True, capture_output=True)
            assert p.stdout == p.stderr == b''

    singles = ['runtime_nan_only', 'finite_zero_only']
    for variant in singles:
        patch = variant + '-gecko-wpt.patch'
        apply(patch)
        assert sha(target) == maps[variant][source]
        expected_test = next(t for t, f in fixtures.items() if f['family'] == ('runtime_nan' if variant == singles[0] else 'finite_pow'))
        html = scratch / ('testing/web-platform/tests' + expected_test)
        assert sha(html) == fixtures[expected_test]['sha256']
        assert len(list(scratch.glob('testing/**/*.html'))) == 1
        apply(patch, True)
        assert target.read_bytes() == original and not list(scratch.glob('testing/**/*.html'))
        records.append(variant)
    for order in [singles, singles[::-1]]:
        for variant in order:
            apply(variant + '-gecko-wpt.patch')
        assert sha(target) == maps['combined'][source]
        for variant in reversed(order):
            apply(variant + '-gecko-wpt.patch', True)
        assert target.read_bytes() == original and not list(scratch.glob('testing/**/*.html'))
        records.append(order)
check = {'status': 'ROUND_RUNTIME_FINITE_DATA_REVIEW_GO', 'data_manifest_sha256': sha(DATA / 'FILES.json'),
         'subtests': 1484, 'harnesses': 35, 'reftests': 8, 'roles': 605, 'temporary_fixtures': 6,
         'source_maps': 4, 'source_guards': 72, 'installed_identities': 21, 'mandatory_installed': 159,
         'required_repairs': {'runtime_nan_only': 8, 'finite_zero_only': 4, 'combined_optional': 12},
         'scratch_transport': records, 'live_inputs_read': False, 'execution_approved': False}
for name, data in [('CHECK.json', check), ('REFERENCES.json', refs)]:
    with (HERE / name).open('x') as f:
        f.write(json.dumps(data, indent=2) + '\n')
print(json.dumps(check, indent=2))
