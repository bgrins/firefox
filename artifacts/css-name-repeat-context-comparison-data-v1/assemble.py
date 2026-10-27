import collections
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OUT = Path(sys.argv[1]).resolve()
assert not OUT.exists()
OUT.mkdir()
refs = {}

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def read(p):
    return json.loads(p.read_text())

def ref(p):
    refs[str(p.relative_to(ROOT))] = sha(p)

def capsule(name, seal):
    p = ROOT / 'artifacts' / name
    assert sha(p / 'FILES.json') == seal
    for n, h in read(p / 'FILES.json').items():
        assert sha(p / n) == h, (name, n)
    ref(p / 'FILES.json')
    return p

def put(n, value):
    (OUT / n).write_text(json.dumps(value, indent=2) + '\n')

old = capsule('css-round-infinite-value-step-comparison-data-v1', '9bad23b202ff79ff3bc8f282213d52bb39d0b74e861644aebdb25dfc6924bcb0')
prior = capsule('css-round-infinite-value-step-runtime-v1', '736a7240a8105a2e765a93b0d6862ce808e010fb77953869575e9188ba86fc5a')
base = capsule('css-name-repeat-context-baseline-runtime-v1', 'b20c44a3b2459410288d930a1844b1b5072be643156ac70e6afb4dfe19fd93e2')
peer = capsule('css-name-repeat-context-baseline-terminal-review-v1', '4dbb89e017b80b4a5ff97beca9fecf2b924f6ff9a06bf3f3b2dcf73dedc0effa')
assert read(peer/'CHECK.json')['status'] == 'NAME_REPEAT_BASELINE_TERMINAL_REVIEW_GO'
proposal = capsule('css-name-repeat-context-repair-v1', '046289055e5ed4da18d074590ed240513c39378c28f3b73ecb5f7da83ea08308')
v3 = capsule('css-name-repeat-context-repair-v3', '454359c092351c37d751f6fcdb21b75cb7959233dfc05523183d84bb8fbeb259')
capsule('css-name-repeat-context-repair-review-v1', '142d06e2a55683d48c321ad33bd57665234aef4dbe9210b43e54f30b91327180')
capsule('css-name-repeat-context-repair-review-v3', '68913d02e764ccdf32572e2e1755ad61a4e09fc21ac23fb30dc4849515577935')
final = read(base / 'FINAL.json')
prev = read(prior / 'FINAL.json')
assert final['snapshot'] == prev['snapshot']
assert final['installed_tests'] == prev['installed_tests']
assert all(final['pins'][k] == v for k, v in prev['pins'].items())
assert final['pins'] == read(base / 'FINAL-PINS.json')
assert len(final['pins']) == 611 and len(final['installed_tests']) == 23
root = read(base / 'ROOT-FINAL-CHECK.json')
assert root == dict(status='NAME_REPEAT_BASELINE_PRESERVATION_PASS', roles=611, sources=72, installed_identities=23, staged_paths=925, native_paths=43, temporary_tests_removed=1, capture_error=None, final_pins_sha256=sha(base/'FINAL-PINS.json'), native_acceptance=False)
completion = read(base / 'ROOT-COMPLETION.json')
assert completion['capture_session'] == 66325 and completion['capture_exit'] == completion['classifier_exit'] == 0
assert not completion['native_candidate_applied'] and not completion['build_performed']
assert read(base/'CLEANUP.json') == dict(removed=['testing/web-platform/tests/css/css-grid/subgrid/subgrid-contextual-name-repeat.html'], errors=[], capture_error=None)
roster = read(HERE/'ROSTER.json')
url = '/css/css-grid/subgrid/subgrid-contextual-name-repeat.html'
run = read(base/'wpt-diagnostic/RUN.json')
events = [json.loads(x) for x in (base/'wpt-diagnostic/raw.json').read_text().splitlines() if x.strip()]
for key, action in [('rows','test_status'),('starts','test_start'),('ends','test_end')]:
    assert run[key] == [e for e in events if e.get('action') == action]
assert run['complete'] and run['infrastructure_faults'] == [] and run['exit'] == 1
assert run['before'] == run['after']
assert len(run['starts']) == len(run['ends']) == 1
assert run['starts'][0]['test'] == run['ends'][0]['test'] == url and run['ends'][0]['status'] == 'OK'
assert [e['subtest'] for e in run['rows']] == roster['expected_subtests'][url]
assert all(e['test'] == url for e in run['rows'])
assert collections.Counter(e['status'] for e in run['rows']) == {'PASS':2,'FAIL':8}
for e in run['rows']:
    assert e['status'] in ['PASS','FAIL']
    if e['status'] == 'FAIL':
        assert e['message'] == 'assert_true: target name-repeat: declaration admission expected true got false'
        assert e['expected'] == 'PASS' and e.get('known_intermittent',[]) == []
classification = read(base/'CLASSIFICATION.json')
assert classification['status'] == 'NAME_REPEAT_BASELINE_CLASSIFIED' and classification['issues'] == []
assert {(e['test'],e['subtest']) for e in classification['observations']} == {(e['test'],e['subtest']) for e in run['rows'] if e['status']=='FAIL'}
assert all(e['classification']=='TARGET_ADMISSION_FAILURE' and e['later_history_reached'] is False for e in classification['observations'])

def normalized(e):
    return dict(test=e['test'],subtest=e['subtest'],status=e['status'],message=e.get('message'),expected=e.get('expected'),effective_expected=e.get('expected',e['status']),known_intermittent=e.get('known_intermittent',[]))
rows = read(old/'data/ARCHIVED-OUTCOMES.json') + [normalized(e) for e in run['rows']]
assert len(rows) == 1540 and len({(e['test'],e['subtest']) for e in rows}) == 1540
assert {(e['test'],e['subtest']) for e in rows} == {(t,n) for t, ns in roster['expected_subtests'].items() for n in ns} | {(t,None) for t in roster['reftests']}
assert sum(len(ns) for ns in roster['expected_subtests'].values()) == 1532
assert len(roster['expected_subtests']) == 38 and len(roster['reftests']) == 8 and len(roster['tests']) == 46
owned = read(HERE/'OWNERSHIP-DRAFT.json')['temporary_fixtures']
assert len(owned) == 7
for path, v in owned.items():
    assert path in final['pins'] and final['pins'][path] is None and path not in final['installed_tests']
    assert sha(ROOT/v['source']) == v['sha256']; ref(ROOT/v['source'])
phase = dict(final['pins']); phase['testing/web-platform/tests'+url] = owned['testing/web-platform/tests'+url]['sha256']
assert run['after'] == phase
maps = read(HERE/'SOURCE-MAPS.json')
assert maps['baseline'] == maps['restored'] == final['snapshot']['sources'] and len(maps['baseline']) == 72
assert {p for p in maps['baseline'] if maps['baseline'][p]!=maps['candidate'][p]} == set(maps['bodies'])
assert len(maps['bodies']) == 2
for p, b in maps['bodies'].items():
    assert sha(ROOT/b['original']) == maps['baseline'][p]
    assert sha(ROOT/b['candidate']) == maps['candidate'][p]
    ref(ROOT/b['original']); ref(ROOT/b['candidate'])
maps['binding_status'] = 'actual baseline source map equality verified'
maps['installed_three_path_patch'] = str((v3/'installed-standalone.patch').relative_to(ROOT))
ref(v3/'installed-standalone.patch')
binaries = {k:v for k,v in final['pins'].items() if k.startswith('objdir-full.noindex/') and (k.endswith('/MacOS/firefox') or k.endswith('/MacOS/XUL'))}
assert len(binaries) == 2
resources = {k:v for k,v in final['pins'].items() if k not in maps['baseline'] and k not in binaries}
assert len(resources) == 537
policy = read(HERE/'EXPERIMENT-POLICY-DRAFT.json')
policy.update(status='BOUND_BASELINE_DATA_ONLY', observed_repair_witnesses=[normalized(e) for e in run['rows'] if e['status']=='FAIL'])
put('ROSTER.json',roster); put('ARCHIVED-OUTCOMES.json',rows); put('SOURCE-MAPS.json',maps)
put('RESTORATION-PINS.json',final['pins']); put('RESOURCES.json',resources)
put('OWNERSHIP.json',dict(temporary_fixtures=owned,installed_identities=final['installed_tests'],permanent_absences=[k for k,v in resources.items() if v is None and k not in owned]))
put('EXPERIMENT-POLICY.json',policy)
put('EPOCH.json',dict(snapshot=final['snapshot'],baseline_binary_pins=binaries,roles=611,source_guards=72,resources=537,installed_identities=23,modified_native_paths=43,staged_paths=925,authority='Three archived captures on identical source/binary/index/installed-test epoch; not one combined capture',head90_normalization=False,fresh_live_preflight_required=True))
put('DISABLED.json',dict(data_only=True,ready_for_execution=False,native_acceptance=False,controller=None,actual_comparison_runtime=None,candidate_build=None,restored_build=None,candidate_binary_pins=None,restored_binary_pins=None,phase_order=['candidate','restored'],baseline_capture_session=66325,baseline_capture_exit=0,baseline_terminal_review=str((peer/'FILES.json').relative_to(ROOT))))
for n in ['FINAL.json','FINAL-PINS.json','ROOT-FINAL-CHECK.json','ROOT-COMPLETION.json','CLASSIFICATION.json','wpt-diagnostic/RUN.json','wpt-diagnostic/raw.json']:
    ref(base/n)
for n in ['ROSTER.json','SOURCE-MAPS.json','OWNERSHIP-DRAFT.json','EXPERIMENT-POLICY-DRAFT.json']:
    ref(HERE/n)
put('REFERENCES.json',refs)
put('CHECK.json',dict(status='NAME_REPEAT_COMPARISON_DATA_VERIFIED',normalized_outcomes=1540,subtests=1532,reftests=8,files=46,baseline_status_counts=dict(collections.Counter(e['status'] for e in rows)),new_baseline=dict(PASS=2,FAIL=8),required_new_PASS=10,required_repairs=8,source_changes=2,roles=611,source_guards=72,resources=537,temporary_fixtures=7,installed_identities=23,head90_normalization=False,native_acceptance=False,live_reads=False))
print(json.dumps(read(OUT/'CHECK.json'),sort_keys=True))
