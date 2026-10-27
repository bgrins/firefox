import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit('Require python3 -I -S without optimization')
sys.dont_write_bytecode = True
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import stat

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RUNTIME = ROOT / 'artifacts/css-svg-length-readiness-comparison-runtime-v1'

def need(ok, why):
    if not ok:
        raise RuntimeError(why)

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def read(p):
    return json.loads(p.read_text())

def authenticate(pins, base):
    for name, digest in pins.items():
        need(not Path(name).is_absolute() and '..' not in Path(name).parts, 'unsafe pin')
        p = base / name
        need(stat.S_ISREG(p.lstat().st_mode) and sha(p) == digest, 'pin ' + name)

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def exact_pins(pins):
    for name, digest in pins.items():
        p = ROOT / name
        if digest is None:
            need(not p.exists() and not p.is_symlink(), 'required absence ' + name)
        else:
            need(stat.S_ISREG(p.lstat().st_mode) and sha(p) == digest, 'live pin ' + name)

def phase_check(phase, c, state, resources, tests):
    directory = RUNTIME / ('wpt-' + phase)
    raw = directory / 'raw.json'
    need(stat.S_ISREG(raw.lstat().st_mode) and raw.stat().st_size <= 128 * 1024 * 1024, 'raw ownership/size')
    events = [json.loads(line) for line in raw.read_text().splitlines()]
    rows = [e for e in events if e.get('action') == 'test_status']
    starts = [e for e in events if e.get('action') == 'test_start']
    ends = [e for e in events if e.get('action') == 'test_end']
    expected = {(test, name) for test, names in c['expected_subtests'].items() for name in names}
    keys = [(r['test'], r['subtest']) for r in rows]
    need(len(expected) == len(rows) == len(set(keys)) == 51 and set(keys) == expected, 'raw51 identities')
    need(len(starts) == len(ends) == 7 and {e['test'] for e in starts} == set(c['expected_subtests'])
         and {e['test'] for e in ends} == set(c['expected_subtests'])
         and all(e['status'] == 'OK' for e in ends), 'seven complete harnesses')
    need(sum(e.get('action') == 'suite_start' for e in events) == 1
         and sum(e.get('action') == 'suite_end' for e in events) == 1
         and not tests.infrastructure_faults(events), 'raw infrastructure')
    failures = {(r['test'], r['subtest']): {k: r.get(k) for k in ('status', 'message', 'expected', 'known_intermittent')}
                for r in rows if r['status'] != 'PASS'}
    allowed = {(test, name): value for test, names in c['baseline_allowed_failures'].items() for name, value in names.items()}
    need(len(allowed) == 16, 'expected16 repair roster')
    need(failures == (allowed if phase == 'baseline' else {}), 'exact phase failures and diagnostics')
    need(sum(r['test'] in c['main_tests'] for r in rows) == 25, 'main25')
    run = read(directory / 'RUN.json')
    need(run['complete'] is True and run['exit'] == (1 if phase == 'baseline' else 0)
         and run['rows'] == rows and run['starts'] == starts and run['ends'] == ends
         and run['infrastructure_faults'] == [] and run['before'] == run['after'], 'RUN/raw agreement')
    command = ['./mach', 'wpt', '--headless', '--processes=1', '--log-raw=' + str(raw), *c['tests']]
    need(run['command'] == command, 'actual WPT invocation')
    cleanup = read(directory / 'CLEANUP.json')
    need(cleanup == {'owned_group_absent': True, 'errors': []}, 'WPT cleanup')
    record = state['phases'][phase]
    source = {**c['head_pins'], **(c['candidate_pins'] if phase == 'candidate' else {})}
    need(record['build_exit'] == 0 and record['source_before_build'] == record['source_after_build']
         and record['source_before_build']['sources'] == source, 'phase source isolation')
    before = read(RUNTIME / 'BEFORE.json')
    need(all(record['source_before_build'][k] == before[k] for k in ('head', 'index_diff_sha256', 'index_entries_sha256')), 'phase index/HEAD')
    if phase == 'baseline':
        need(record['source_before_build']['native_diff_sha256'] == hashlib.sha256(b'').hexdigest(), 'baseline empty native diff')
    build = read(RUNTIME / (phase + '-build.json'))
    need(build == {'command': ['./mach', 'build', 'binaries'], 'exit': 0}, 'build receipt')
    fixtures = {name: sha(RUNTIME / file) for name, file in c['install'].items()}
    expected_pins = {**resources, **source, **fixtures, **record['binary_pins']}
    need(set(record['binary_pins']) == set(BINARIES) and run['before'] == expected_pins, 'complete phase role/binary join')
    counts = {s: sum(r['status'] == s for r in rows) for s in ('PASS', 'FAIL')}
    need(counts == record['subtests'], 'phase counts')
    return rows, counts, {'raw_sha256': sha(raw), 'run_sha256': sha(directory / 'RUN.json'),
                          'cleanup_sha256': sha(directory / 'CLEANUP.json'), 'binary_pins': record['binary_pins']}

parser = argparse.ArgumentParser()
parser.add_argument('--session-exit', type=int, required=True)
args = parser.parse_args()
need(args.session_exit == 0, 'root must supply actual terminal20804 exit0')
authenticate(read(HERE / 'FILES.json'), HERE)
authenticate(read(HERE / 'REFERENCES.json'), ROOT)
authenticate(read(RUNTIME / 'DRAFT-FILES.json'), RUNTIME)
authenticate(read(RUNTIME / 'REFERENCES.json'), ROOT)
c = read(RUNTIME / 'CONFIG.json')
state = read(RUNTIME / 'STATE.json')
state_pin = sha(RUNTIME / 'STATE.json')
need(set(c['candidate_pins']) == {'dom/svg/DOMSVGLength.cpp', 'dom/svg/DOMSVGLength.h'}
     and len(c['head_pins']) == 53 and set(c['head_pins']) == set(c['source_pins']), 'exact two-file candidate and53 roles')
need(state['status'] == 'terminal' and state['restored'] is True and state['restore_build_exit'] == 0
     and state['recovery_errors'] == [] and 'failure' not in state and state['paired_preservation_passed'] is True
     and set(state['phases']) == {'baseline', 'candidate'} and state['lint_exit'] == 0, 'terminal successful restoration')
need(read(RUNTIME / 'fixture-lint.json') == {'command': ['./mach', 'lint', '--linter', 'wpt', *c['install']], 'exit': 0}, 'lint receipt')
before, final = read(RUNTIME / 'BEFORE.json'), read(RUNTIME / 'FINAL.json')
need(before == final and final['sources'] == c['source_pins'] and len(final['sources']) == 53, 'before/final53')
need(len(c['sources']) == len(set(c['sources'])) == 30 and set(state['restored_paths']) == set(c['sources'])
     and len(state['restored_paths']) == 30 and len(c['modified_native_paths']) == 30, 'restored30 source roster')
resources = read(RUNTIME / 'RESOURCES.json')
need(len(resources) == 390, 'resource390')
final_pins = read(RUNTIME / 'FINAL-PINS.json')
need(final_pins == {**resources, **final['sources'], **state['restored_binary_pins']}, 'full final pins')
wpt = load('final_check_wpt', ROOT / c['helpers'] / 'run_wpt.py')
bindings = load('final_check_bindings', ROOT / c['helpers'] / 'bindings.py')
tests = load('final_check_tests', RUNTIME / 'tests.py')
wpt.CONFIG, wpt.HERE = c, RUNTIME
BINARIES = wpt.BINARIES
need(set(state['restored_binary_pins']) == set(BINARIES), 'two restored binaries')
index = bindings.index_state(wpt)
need(len(index['staged_paths']) == 925 and wpt.snapshot() == final, 'live source/index restoration')
exact_pins(final_pins)
for name in c['sources']:
    need(sha(RUNTIME / 'original' / name) == c['source_pins'][name] == sha(ROOT / name), 'saved original body ' + name)
    temporary = (ROOT / name).with_name('.' + Path(name).name + '.svg-readiness-comparison.tmp')
    need(not temporary.exists() and not temporary.is_symlink(), 'native temp remains')
modified = [n for n in wpt.git('diff', '--name-only').decode().splitlines() if not n.startswith('artifacts/')]
need(modified == c['modified_native_paths'], 'actual30 native changes')
need(not wpt.git('ls-files', '--others', '--exclude-standard', '--', 'layout', 'dom', 'servo', 'mfbt'), 'untracked native source')
for name in set(c['must_be_absent']) | set(c['install']):
    p = ROOT / name
    need(not p.exists() and not p.is_symlink(), 'owned/prior temp remains ' + name)
need(not wpt.git('ls-files', '--', *c['install']), 'owned WPT tracked')
installed = c['epoch_receipt']['installed_tests']
need(len(installed) == 7, 'seven installed identities')
for name, item in installed.items():
    p = ROOT / name
    st = p.lstat()
    need(stat.S_ISREG(st.st_mode) and [st.st_dev, st.st_ino] == item['identity'] and sha(p) == item['sha256'], 'installed identity ' + name)
exact_pins(c['existing_test_pins'])
need(wpt.git('ls-files', '--', *c['existing_tests']).decode().splitlines() == c['tracked_existing_tests'], 'test ownership partition')
raws, counts, evidence = {}, {}, {}
for phase in ('baseline', 'candidate'):
    raws[phase], counts[phase], evidence[phase] = phase_check(phase, c, state, resources, tests)
old = {(r['test'], r['subtest']): r for r in raws['baseline']}
new = {(r['test'], r['subtest']): r for r in raws['candidate']}
repairs = [list(k) for k in old if old[k]['status'] == 'FAIL' and new[k]['status'] == 'PASS']
comparison = read(RUNTIME / 'COMPARISON.json')
need(len(repairs) == 16 and comparison == {'regressions': [], 'changed_failures': [], 'repaired': repairs, 'native_acceptance': False}, 'exact paired16 receipt')
need(wpt.snapshot() == final and sha(RUNTIME / 'STATE.json') == state_pin, 'end source/index/state snapshot')
exact_pins(final_pins)
receipt = {'status': 'RESTORED_VERIFIED', 'session': 20804, 'exit': args.session_exit,
           'state_sha256': sha(RUNTIME / 'STATE.json'), 'final_sha256': sha(RUNTIME / 'FINAL.json'),
           'final_pins_sha256': sha(RUNTIME / 'FINAL-PINS.json'), 'restored_binary_pins': state['restored_binary_pins'],
           'installed_tests': installed, 'source_count': 53, 'pin_count': len(final_pins), 'resource_count': 390,
           'restored_original_paths': 30, 'native_modified_paths': 30, 'staged_paths': 925,
           'baseline': counts['baseline'], 'candidate': counts['candidate'], 'repair_count': 16,
           'phase_evidence': evidence, 'restore_build_log_sha256': sha(RUNTIME / 'restore-build.log'),
           'accepted_native_repair': False,
           'session_exit_supplied_by_root': True}
with (HERE / 'ROOT-FINAL-CHECK.json').open('x') as stream:
    stream.write(json.dumps(receipt, indent=2) + '\n')
print(json.dumps(receipt, indent=2))
