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
need(all(isinstance(c[n], str) and c[n] for n in ('epoch', 'reanalysis')), 'unbound restored epoch or baseline reanalysis')
need(all(not (HERE / n).exists() and not (HERE / n).is_symlink()
         for n in ('wpt-baseline', 'wpt-candidate')), 'WPT output directory exists')
need(not any((HERE / n).exists() for n in ('BEFORE.json', 'STATE.json', 'original')), 'already started')
need(all(not (ROOT / n).with_name('.' + Path(n).name + '.rounding-comparison.tmp').exists()
         and not (ROOT / n).with_name('.' + Path(n).name + '.rounding-comparison.tmp').is_symlink() for n in c['sources']), 'source temp exists')
wpt = load('rounding_wpt', ROOT / c['helpers'] / 'run_wpt.py')
bindings = load('rounding_bindings', ROOT / c['helpers'] / 'bindings.py')
reanalysis = ROOT / c['reanalysis']
authenticate(read(reanalysis / 'FILES.json'), reanalysis)
old_tests = load('retained_rounding_tests', reanalysis / 'tests.py')
tests = load('consolidated_tests', HERE / 'tests.py')
wpt.HERE, wpt.CONFIG = HERE, c
previous = ROOT / c['epoch']
authenticate(read(previous / 'FILES.json'), previous)
epoch, receipt = read(previous / 'STATE.json'), read(previous / 'ROOT-FINAL-CHECK.json')
def require_epoch(previous, epoch, receipt):
    need(c['epoch_receipt'] is not None, 'unbound epoch receipt')
    need(epoch['status'] == 'terminal' and epoch['restored'] is True
         and epoch['restore_build_exit'] == 0 and epoch['recovery_errors'] == []
         and epoch['lint_exit'] == 0 and 'failure' not in epoch
         and epoch['restored_paths'] == c['sources']
         and set(epoch['phases']) == {'candidate'}
         and epoch['phases']['candidate']['build_exit'] == 0
         and epoch['paired_preservation_passed'] is True, 'successful candidate restoration gate')
    need(receipt == c['epoch_receipt']
         and receipt['status'] == 'COMPARISON_PASSED_RESTORATION_VERIFIED'
         and receipt['baseline_reanalysis_files_sha256'] == sha(reanalysis / 'FILES.json'), 'exact root restoration receipt')
    need(receipt['state_sha256'] == sha(previous / 'STATE.json')
         and receipt['final_sha256'] == sha(previous / 'FINAL.json')
         and receipt['restored_binary_pins'] == epoch['restored_binary_pins'], 'root restoration joins')
    final = read(previous / 'FINAL.json')
    need(read(previous / 'BEFORE.json') == final, 'restored snapshot')
    need(read(previous / 'FINAL-PINS.json') == {**read(previous / 'RESOURCES.json'),
         **final['sources'], **epoch['restored_binary_pins']}, 'restored epoch role map')
require_epoch(previous, epoch, receipt)
bindings.index_state(wpt)
before = wpt.snapshot()
prior_final = read(previous / 'FINAL.json')
need(all(before[k] == prior_final[k] for k in before if k != 'sources')
     and all(before['sources'][n] == h for n, h in prior_final['sources'].items()), 'restored source epoch')
need(before['head'] == c['head'] and before['sources'] == c['source_pins'], 'working source roles')
need(wpt.pins(wpt.BINARIES) == epoch['restored_binary_pins'], 'restored binaries')
prior_pins = read(previous / 'FINAL-PINS.json')
need(wpt.pins(list(prior_pins)) == prior_pins, 'complete prior source/resource/binary epoch')
need(all(prior_pins[n] == h for n, h in c['existing_test_pins'].items()), 'installed test epoch transfer')
wpt.ENV.update(MOZ_DISABLE_SAFE_MODE_KEY='1', MOZ_DISABLE_UPDATE_PROCESSING='1')
wpt.ENV.pop('MOZ_SAFE_MODE_RESTART', None)
resources = read(HERE / 'RESOURCES.json')
need(wpt.pins(list(resources)) == resources, 'initial resources')
owned_test = next(iter(c['install']))
need(len(c['install']) == 1 and len(c['tests']) == 13 and len(c['baseline_tests']) == 5 and len(c['candidate_sources']) == 1, 'comparison scope')
need(not (ROOT / owned_test).exists() and not (ROOT / owned_test).is_symlink()
     and not wpt.git('ls-files', '--', owned_test), 'test absent/untracked')
fixture = (HERE / c['install'][owned_test]).read_bytes()
def phase_resources(phase):
    return {**resources, **c['head_pins'], **c['baseline_pins'],
            **(c['candidate_pins'] if phase == 'candidate' else {}),
            owned_test: hashlib.sha256(fixture).hexdigest()}

def modified_native():
    return [n for n in wpt.git('diff', '--name-only').decode().splitlines() if not n.startswith('artifacts/')]
def untracked_native():
    return wpt.git('ls-files', '--others', '--exclude-standard', '--', 'layout', 'dom', 'servo', 'mfbt').decode().splitlines()
def existing_tests():
    need(wpt.pins(c['existing_tests']) == c['existing_test_pins'], 'read-only existing tests')
    need(wpt.git('ls-files', '--', *c['existing_tests']).decode().splitlines() == c['tracked_existing_tests'], 'existing test ownership')
    for n, h in read(HERE / 'TEST-SOURCE-PINS.json').items():
        need(sha(ROOT / n) == h and hashlib.sha256(wpt.git('show', c['head'] + ':' + n)).hexdigest() == h, 'comparison test HEAD binding')
existing_tests()
need(modified_native() == c['modified_native_paths'] and not untracked_native(), 'complete native roster')
need(len(c['sources']) == 30 and len(c['guard_sources']) == 47 and set(c['modified_native_paths']) <= set(c['sources']), 'normalization roster')
head = {n: wpt.git('show', c['head'] + ':' + n) for n in c['guard_sources']}
need({n: hashlib.sha256(b).hexdigest() for n, b in head.items()} == c['head_pins'], 'HEAD bodies')
original = {n: (ROOT / n).read_bytes() for n in c['sources']}
baseline = {n: (ROOT / p).read_bytes() for n, p in c['baseline_sources'].items()}
need(set(baseline) <= set(original) and {n: hashlib.sha256(b).hexdigest() for n, b in baseline.items()} == c['baseline_pins'], 'baseline reverse sources')
selected = {n: (ROOT / p).read_bytes() for n, p in c['candidate_sources'].items()}
need(set(selected) <= set(original) and {n: hashlib.sha256(b).hexdigest() for n, b in selected.items()} == c['candidate_pins'], 'candidate source')

def verify_phase(phase):
    now = wpt.snapshot()
    need(all(now[k] == before[k] for k in ('head', 'index_diff_sha256', 'index_entries_sha256')), 'HEAD/index changed')
    expected = {**c['head_pins'], **c['baseline_pins'], **(c['candidate_pins'] if phase == 'candidate' else {})}
    need(now['sources'] == expected, 'exact phase sources')
    need(sorted(modified_native()) == sorted(set(baseline) | (set(selected) if phase == 'candidate' else set())) and not untracked_native(), 'complete phase diff')
    need(wpt.pins(list(phase_resources(phase))) == phase_resources(phase), 'phase resources')
    need(all(not (ROOT / n).exists() and not (ROOT / n).is_symlink() for n in c['must_be_absent']), 'prior temporary input appeared')
    need(not wpt.git('ls-files', '--', owned_test), 'owned test became tracked')
    existing_tests()
    authenticate(payloads, HERE)
    authenticate(refs, ROOT)

baseline_gate = load('retained_baseline_gate', HERE / 'baseline_gate.py')
old_runtime = ROOT / c['retained_baseline']
authenticate(read(old_runtime / 'FILES.json'), old_runtime)
old_config = read(old_runtime / 'CONFIG.json')
old_config['epoch'] = c['retained_baseline']
old_resources = read(old_runtime / 'RESOURCES.json')
old_fixture_path, old_fixture_copy = next(iter(old_config['install'].items()))
try:
    wpt.CONFIG = old_config
    retained_baseline = baseline_gate.validate(wpt, old_tests, old_runtime, reanalysis,
        read(old_runtime / 'STATE.json'), old_resources, sha(old_runtime / old_fixture_copy), sha)
finally:
    wpt.CONFIG = c
need(old_config['head_pins'] == c['head_pins'] and old_config['baseline_pins'] == c['baseline_pins'],
     'retained baseline native role identity')
old_phase_resources = {**old_resources, **old_config['head_pins'], **old_config['baseline_pins']}
need(all(phase_resources('baseline').get(n) == h for n, h in old_phase_resources.items()
         if n != old_fixture_path), 'retained baseline source/resource/metadata transfer')
retained_controls = [row for row in retained_baseline['rows'] if row['test'] in c['expected_subtests']]
need(len(retained_controls) == 80 and len({(r['test'], r['subtest']) for r in retained_controls}) == 80,
     'retained eighty controls')

for n, data in original.items():
    p = HERE / 'original' / n
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(data)
wpt.save('BEFORE.json', before)
wpt.save('ORIGINAL-BINARIES.json', epoch['restored_binary_pins'])
state = {'status': 'starting', 'phases': {}, 'baseline_reuse': {'runtime': c['retained_baseline'], 'reanalysis': c['reanalysis'], 'run_sha256': sha(old_runtime / 'wpt-baseline/RUN.json'), 'original_complete': False, 'revalidated_complete': True}, 'accepted_native_repair': False, 'pending_acceptance_gates': c['pending_acceptance_gates']}
changed = False
owned_identity = None
errors = []
def recovery_save(name, data):
    try:
        wpt.save(name, data)
    except BaseException as error:
        errors.append({'operation': 'save ' + name, 'error': repr(error)})
owned_sources = {}
for name, body in original.items():
    info = (ROOT / name).lstat()
    need(stat.S_ISREG(info.st_mode), 'source is not regular')
    owned_sources[name] = {(info.st_dev, info.st_ino, hashlib.sha256(body).hexdigest())}

def replace_source(name, data):
    path = ROOT / name
    info = path.lstat()
    current = path.read_bytes()
    identity = (info.st_dev, info.st_ino, hashlib.sha256(current).hexdigest())
    need(stat.S_ISREG(info.st_mode) and identity in owned_sources[name], 'unknown native edit: ' + name)
    if data == current:
        return
    temp = path.with_name('.' + path.name + '.rounding-comparison.tmp')
    temporary_identity = None
    try:
        with temp.open('xb') as stream:
            temporary = os.fstat(stream.fileno())
            temporary_identity = (temporary.st_dev, temporary.st_ino)
            need(stream.write(data) == len(data), 'short native write')
            stream.flush()
            os.fchmod(stream.fileno(), stat.S_IMODE(info.st_mode))
        need(temp.read_bytes() == data, 'incomplete native temporary body')
        fresh = path.lstat()
        need((fresh.st_dev, fresh.st_ino) == identity[:2] and path.read_bytes() == current,
             'native edit before replacement: ' + name)
        owned_sources[name].add((*temporary_identity, hashlib.sha256(data).hexdigest()))
        os.replace(temp, path)
    finally:
        if temporary_identity is not None and (temp.exists() or temp.is_symlink()):
            remaining = temp.lstat()
            need(stat.S_ISREG(remaining.st_mode) and (remaining.st_dev, remaining.st_ino) == temporary_identity,
                 'owned source temp replaced')
            temp.unlink()

try:
    for n in c['sources']:
        target = baseline.get(n, head[n])
        if original[n] != target:
            changed = True
            replace_source(n, target)
    with (ROOT / owned_test).open('xb') as stream:
        info = os.fstat(stream.fileno())
        owned_identity = (info.st_dev, info.st_ino)
        need(stream.write(fixture) == len(fixture), 'short fixture write')
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
                    replace_source(n, data)
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
        runs[phase] = tests.run(wpt, phase, phase_resources(phase))
        record['subtests'] = {s: sum(r['status'] == s for r in runs[phase]['rows']) for s in ('PASS', 'FAIL')}
        need(all(runs[phase]['before'][n] == h for n, h in record['binary_pins'].items()), 'built binary/test join')
        tests.require_phase(wpt, phase, runs[phase])
        verify_phase(phase)
        wpt.save('STATE.json', state)
    combined_baseline = {'rows': runs['baseline']['rows'] + retained_controls}
    wpt.save('COMBINED-BASELINE.json', {'new_run': 'wpt-baseline/RUN.json', 'retained_runtime': c['retained_baseline'],
        'retained_reanalysis': c['reanalysis'], **combined_baseline})
    tests.compare(wpt, combined_baseline, runs['candidate'])
    state['paired_preservation_passed'] = True
    state['baseline_reused'] = True
except BaseException as error:
    state['failure'] = {'type': type(error).__name__, 'message': str(error)}
finally:
    state.update(status='restoring', recovery_errors=errors)
    recovery_save('STATE.json', state)
    for n, data in original.items():
        try:
            replace_source(n, data)
        except BaseException as error:
            errors.append({'operation': 'restore ' + n, 'error': repr(error)})
    if owned_identity is not None:
        try:
            info = (ROOT / owned_test).lstat()
            need(stat.S_ISREG(info.st_mode) and (info.st_dev, info.st_ino) == owned_identity, 'owned test replaced; preserve replacement')
            (ROOT / owned_test).unlink()
        except BaseException as error:
            errors.append({'operation': 'remove owned test', 'error': repr(error)})
    state['restored_paths'] = []
    for n, data in original.items():
        try:
            need((ROOT / n).read_bytes() == data, 'original source not restored: ' + n)
            state['restored_paths'].append(n)
        except BaseException as error:
            errors.append({'operation': 'verify restoration ' + n, 'error': repr(error)})
    if changed and len(state['restored_paths']) == len(original):
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
            and not (ROOT / owned_test).is_symlink() and not wpt.git('ls-files', '--', owned_test)
            and all(not (ROOT / n).with_name('.' + Path(n).name + '.rounding-comparison.tmp').exists()
                    and not (ROOT / n).with_name('.' + Path(n).name + '.rounding-comparison.tmp').is_symlink() for n in c['sources']))
        state['restored_binary_pins'] = wpt.pins(wpt.BINARIES)
        recovery_save('FINAL.json', final)
    except BaseException as error:
        errors.append({'operation': 'final check', 'error': repr(error)})
    state['status'] = 'terminal'
    recovery_save('STATE.json', state)
print(json.dumps(state, indent=2))
if 'failure' in state or errors or not state['restored'] or (changed and state.get('restore_build_exit') != 0):
    raise SystemExit(1)
