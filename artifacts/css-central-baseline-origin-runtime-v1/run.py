import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit('Require python3 -I -S without optimization')
sys.dont_write_bytecode = True
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import stat
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]

def need(ok, why):
    if not ok:
        raise RuntimeError(why)
def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):
    return json.loads(p.read_text())
def authenticate(mapping, base):
    for n, h in mapping.items():
        need(not Path(n).is_absolute() and '..' not in Path(n).parts, 'unsafe pin')
        p = base / n
        need(stat.S_ISREG(p.lstat().st_mode) and sha(p) == h, 'pin ' + n)
def load(name, p):
    spec = importlib.util.spec_from_file_location(name, p)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

parser = argparse.ArgumentParser()
parser.add_argument('--draft-sha', required=True)
args = parser.parse_args()
need(sha(HERE / 'DRAFT-FILES.json') == args.draft_sha, 'draft seal')
payloads, refs = read(HERE / 'DRAFT-FILES.json'), read(HERE / 'REFERENCES.json')
authenticate(payloads, HERE)
authenticate(refs, ROOT)
c = read(HERE / 'CONFIG.json')
need(c['ready_for_execution'] is True, 'disabled draft')
need(not any((HERE / n).exists() for n in ('BEFORE.json', 'STATE.json', 'original')), 'already started')
wpt = load('central_wpt', ROOT / c['helpers'] / 'run_wpt.py')
bindings = load('central_bindings', ROOT / c['helpers'] / 'bindings.py')
tests = load('central_tests', HERE / 'tests.py')
wpt.HERE, wpt.CONFIG = HERE, c
previous = ROOT / 'artifacts/css-wide-baseline-interface-compile-runtime-v1'
observation = ROOT / 'artifacts/css-central-baseline-origin-working-v2'
authenticate(read(previous / 'FILES.json'), previous)
authenticate(read(observation / 'FILES.json'), observation)
epoch, receipt = read(previous / 'STATE.json'), read(previous / 'ROOT-FINAL-CHECK.json')
observed = read(observation / 'STATE.json')
need(epoch['status'] == 'terminal' and epoch['restored'] and epoch['restore_build_exit'] == 0
     and not epoch['recovery_errors'] and 'failure' not in epoch
     and epoch['phases']['candidate']['build_exit'] == 0, 'interface compile/restoration gate')
need(receipt['state_sha256'] == sha(previous / 'STATE.json') and receipt['final_sha256'] == sha(previous / 'FINAL.json')
     and receipt['restored_binary_pins'] == epoch['restored_binary_pins'], 'root interface receipt')
need(observed['status'] == 'terminal' and observed['restored'] and observed['complete']
     and observed['owned_process_group_absent'] and not observed['cleanup_errors'] and 'failure' not in observed,
     'v2 observation not complete/restored')
bindings.index_state(wpt)
before = wpt.snapshot()
need(before == read(previous / 'FINAL.json') == read(previous / 'BEFORE.json'), 'restored source epoch')
need(read(observation / 'BEFORE.json') == read(observation / 'FINAL.json'), 'v2 changed state')
need(read(observation / 'FINAL.json')['snapshot'] == before
     and read(observation / 'FINAL.json')['binary_pins'] == epoch['restored_binary_pins'], 'v2 epoch correspondence')
need(before['head'] == c['head'] and before['sources'] == c['source_pins'], 'working source roles')
need(wpt.pins(wpt.BINARIES) == epoch['restored_binary_pins'], 'restored binaries')
resources = read(HERE / 'RESOURCES.json')
need(wpt.pins(list(resources)) == resources, 'initial resources')
owned_test = next(iter(c['install']))
need(len(c['install']) == 1 and len(c['tests']) == 14 and len(c['candidate_sources']) == 1, 'comparison scope')
need(not (ROOT / owned_test).exists() and not (ROOT / owned_test).is_symlink()
     and not wpt.git('ls-files', '--', owned_test), 'test absent/untracked')
fixture = (HERE / c['install'][owned_test]).read_bytes()
phase_resources = {**resources, owned_test: hashlib.sha256(fixture).hexdigest()}

def modified_native():
    return [n for n in wpt.git('diff', '--name-only').decode().splitlines() if not n.startswith('artifacts/')]
def untracked_native():
    return wpt.git('ls-files', '--others', '--exclude-standard', '--', 'layout', 'dom', 'servo', 'mfbt').decode().splitlines()
def existing_tests():
    need(wpt.pins(c['existing_tests']) == c['existing_test_pins'], 'read-only existing tests')
    need(wpt.git('ls-files', '--', *c['existing_tests']).decode().splitlines() == c['tracked_existing_tests'], 'existing test ownership')
    for n, h in read(HERE / 'TEST-SOURCE-PINS.json').items():
        need(sha(ROOT / n) == h and hashlib.sha256(wpt.git('show', 'HEAD:' + n)).hexdigest() == h, 'comparison test HEAD binding')
existing_tests()
need(modified_native() == c['modified_native_paths'] and not untracked_native(), 'complete native roster')
need(len(c['sources']) == 32 and len(c['guard_sources']) == 44 and set(c['modified_native_paths']) <= set(c['sources']), 'normalization roster')
head = {n: wpt.git('show', 'HEAD:' + n) for n in c['guard_sources']}
need({n: hashlib.sha256(b).hexdigest() for n, b in head.items()} == c['head_pins'], 'HEAD bodies')
original = {n: (ROOT / n).read_bytes() for n in c['sources']}
selected = {n: (ROOT / p).read_bytes() for n, p in c['candidate_sources'].items()}
need(set(selected) <= set(original) and {n: hashlib.sha256(b).hexdigest() for n, b in selected.items()} == c['candidate_pins'], 'candidate source')

def verify_phase(phase):
    now = wpt.snapshot()
    need(all(now[k] == before[k] for k in ('head', 'index_diff_sha256', 'index_entries_sha256')), 'HEAD/index changed')
    expected = {**c['head_pins'], **(c['candidate_pins'] if phase == 'candidate' else {})}
    need(now['sources'] == expected, 'exact phase sources')
    need(sorted(modified_native()) == (sorted(selected) if phase == 'candidate' else []) and not untracked_native(), 'complete phase diff')
    need(wpt.pins(list(phase_resources)) == phase_resources, 'phase resources')
    need(all(not (ROOT / n).exists() and not (ROOT / n).is_symlink() for n in c['must_be_absent']), 'prior temporary input appeared')
    need(not wpt.git('ls-files', '--', owned_test), 'owned test became tracked')
    existing_tests()
    authenticate(payloads, HERE)
    authenticate(refs, ROOT)

for n, data in original.items():
    p = HERE / 'original' / n
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(data)
wpt.save('BEFORE.json', before)
wpt.save('ORIGINAL-BINARIES.json', epoch['restored_binary_pins'])
state = {'status': 'starting', 'phases': {}, 'accepted_native_repair': False, 'pending_acceptance_gates': c['pending_acceptance_gates']}
changed = False
owned_identity = None
errors = []
def recovery_save(name, data):
    try:
        wpt.save(name, data)
    except BaseException as error:
        errors.append({'operation': 'save ' + name, 'error': repr(error)})
try:
    for n in c['sources']:
        if not (ROOT / n).exists() or (ROOT / n).read_bytes() != head[n]:
            changed = True
            (ROOT / n).write_bytes(head[n])
    with (ROOT / owned_test).open('xb') as stream:
        info = os.fstat(stream.fileno())
        owned_identity = (info.st_dev, info.st_ino)
        stream.write(fixture)
    verify_phase('baseline')
    state['lint_exit'] = wpt.command('fixture-lint', ['./mach', 'lint', '--linter', 'wpt', owned_test])
    wpt.save('STATE.json', state)
    need(state['lint_exit'] == 0, 'owned WPT lint failed')
    verify_phase('baseline')
    runs = {}
    for phase in ('baseline', 'candidate'):
        if phase == 'candidate':
            for n, data in selected.items():
                if not (ROOT / n).exists() or (ROOT / n).read_bytes() != data:
                    changed = True
                    (ROOT / n).write_bytes(data)
        verify_phase(phase)
        record = state['phases'][phase] = {'source_before_build': wpt.snapshot()}
        state['status'] = 'building ' + phase
        wpt.save('STATE.json', state)
        record['build_exit'] = wpt.command(phase + '-build', ['./mach', 'build', 'binaries'])
        record['source_after_build'] = wpt.snapshot()
        record['binary_pins'] = wpt.pins(wpt.BINARIES)
        wpt.save('STATE.json', state)
        need(record['build_exit'] == 0, 'phase build failed')
        need(record['source_before_build'] == record['source_after_build'], 'source changed during build')
        verify_phase(phase)
        state['status'] = 'testing ' + phase
        wpt.save('STATE.json', state)
        runs[phase] = tests.run(wpt, phase, phase_resources)
        record['subtests'] = {s: sum(r['status'] == s for r in runs[phase]['rows']) for s in ('PASS', 'FAIL')}
        need(all(runs[phase]['before'][n] == h for n, h in record['binary_pins'].items()), 'built binary/test join')
        if phase == 'baseline':
            main = next(iter(c['expected_subtests']))
            current = [r for r in runs[phase]['rows'] if r['test'] == main]
            prior = read(observation / 'RESULT.json')['rows']
            need([(r['subtest'], r['status']) for r in current] == [(r['subtest'], r['status']) for r in prior], 'HEAD midpoint classification differs from working observation')
            need(all('physical margin-box center aligns with symmetric reference' in (r.get('message') or '') for r in current if r['status'] == 'FAIL'), 'HEAD midpoint failure is calibration or another assertion')
        verify_phase(phase)
        wpt.save('STATE.json', state)
    tests.compare(wpt, runs['baseline'], runs['candidate'])
    state['paired_preservation_passed'] = True
except BaseException as error:
    state['failure'] = {'type': type(error).__name__, 'message': str(error)}
finally:
    state.update(status='restoring', recovery_errors=errors)
    recovery_save('STATE.json', state)
    for n, data in original.items():
        try:
            if not (ROOT / n).exists() or (ROOT / n).read_bytes() != data:
                (ROOT / n).write_bytes(data)
        except BaseException as error:
            errors.append({'operation': 'restore ' + n, 'error': repr(error)})
    if owned_identity is not None:
        try:
            info = (ROOT / owned_test).lstat()
            need(stat.S_ISREG(info.st_mode) and (info.st_dev, info.st_ino) == owned_identity, 'owned test replaced; preserve replacement')
            (ROOT / owned_test).unlink()
        except BaseException as error:
            errors.append({'operation': 'remove owned test', 'error': repr(error)})
    if changed:
        try:
            try:
                log = (HERE / 'restore-build.log').open('w')
            except OSError as error:
                errors.append({'operation': 'open restore log', 'error': repr(error)})
                log = None
            try:
                state['restore_build_exit'] = subprocess.run(['./mach', 'build', 'binaries'], cwd=ROOT,
                    env=wpt.ENV, stdout=log, stderr=subprocess.STDOUT).returncode
            finally:
                if log is not None:
                    log.close()
        except BaseException as error:
            errors.append({'operation': 'restore build', 'error': repr(error)})
    state['restored'] = False
    try:
        final = wpt.snapshot()
        existing_tests()
        bindings.index_state(wpt)
        state['restored'] = (final == before and modified_native() == c['modified_native_paths'] and not untracked_native()
            and all(not (ROOT / n).exists() and not (ROOT / n).is_symlink() for n in c['must_be_absent'])
            and wpt.pins(list(resources)) == resources and not (ROOT / owned_test).exists()
            and not (ROOT / owned_test).is_symlink() and not wpt.git('ls-files', '--', owned_test))
        state['restored_binary_pins'] = wpt.pins(wpt.BINARIES)
        recovery_save('FINAL.json', final)
    except BaseException as error:
        errors.append({'operation': 'final check', 'error': repr(error)})
    state['status'] = 'terminal'
    recovery_save('STATE.json', state)
print(json.dumps(state, indent=2))
if 'failure' in state or errors or not state['restored'] or (changed and state.get('restore_build_exit') != 0):
    raise SystemExit(1)
