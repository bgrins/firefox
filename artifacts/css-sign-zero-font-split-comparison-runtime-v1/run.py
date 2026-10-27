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
need(c['candidate_status'] == 'REVIEWED_FOR_COMPARISON', 'candidate source review HOLD')
need(all(isinstance(v, dict) and isinstance(v.get('path'), str) and isinstance(v.get('sha256'), str)
         for v in c['required_seals'].values()), 'unbound proposal/review')
for value in c['required_seals'].values():
    need(sha(ROOT / value['path']) == value['sha256'], 'required final seal')
    authenticate(read(ROOT / value['path']), (ROOT / value['path']).parent)
proposal = ROOT / c['proposal']
authenticate(read(proposal / 'FILES.json'), proposal)
fixture_proposal = ROOT / c['fixture_proposal']
authenticate(read(fixture_proposal / 'FILES.json'), fixture_proposal)
need(all(isinstance(c[n], str) and c[n] for n in ('epoch', 'proposal'))
     and isinstance(c['epoch_receipt'], dict) and isinstance(c['source_pins'], dict)
     and isinstance(c['modified_native_paths'], list), 'unbound installed epoch/source roles')
need(all(not (HERE / n).exists() and not (HERE / n).is_symlink()
         for n in ('wpt-baseline', 'wpt-raw_only', 'wpt-raw_plus_sign')), 'WPT output directory exists')
need(not any((HERE / n).exists() for n in ('BEFORE.json', 'STATE.json', 'original')), 'already started')
need(all(not (ROOT / n).with_name('.' + Path(n).name + '.sign-split-comparison.tmp').exists()
         and not (ROOT / n).with_name('.' + Path(n).name + '.sign-split-comparison.tmp').is_symlink() for n in c['sources']), 'source temp exists')
wpt = load('rounding_wpt', ROOT / c['helpers'] / 'run_wpt.py')
bindings = load('sentinel_index', HERE / 'index_gate.py')
tests = load('sentinel_tests', HERE / 'tests.py')
wpt.HERE, wpt.CONFIG = HERE, c
previous = ROOT / c['epoch']
need(sha(previous / 'FILES.json') == c['epoch_manifest_sha256'], 'installed test epoch')
authenticate(read(previous / 'FILES.json'), previous)
need(read(previous / 'ROOT-FINAL-CHECK.json') == c['epoch_receipt'], 'exact restored root receipt')
need(isinstance(c['epoch_adapter'], str) and isinstance(c['epoch_adapter_sha256'], str)
     and sha(ROOT / c['epoch_adapter']) == c['epoch_adapter_sha256'], 'reviewed actual epoch adapter')
epoch_gate = load('round_restored_epoch_gate', ROOT / c['epoch_adapter'])
prior_final, prior_pins, installed_tests, binary_pins = epoch_gate.bind(ROOT, previous, c, read, sha, authenticate)
need(set(read(HERE / 'PLANNED-SCOPE.json')['installed_tests']) <= set(installed_tests), 'all prior installed identities carried')
epoch = {'installed_binary_pins': binary_pins}
bindings.index_state(wpt)
before = wpt.snapshot()
need(before == c['execution_snapshot'] and before['sources'] == c['source_pins'], 'root-bound current execution state')
need(all(before['sources'][n] == h for n, h in prior_final['sources'].items()), 'restored source continuity after signing')
need(wpt.pins(wpt.BINARIES) == binary_pins, 'restored binaries')
need(wpt.pins(list(prior_pins)) == prior_pins, 'complete prior source/resource/binary epoch')
need(all(prior_pins[n] == c['existing_test_pins'][n] for n in installed_tests), 'installed test epoch transfer')
wpt.ENV.update(MOZ_DISABLE_SAFE_MODE_KEY='1', MOZ_DISABLE_UPDATE_PROCESSING='1')
wpt.ENV.pop('MOZ_SAFE_MODE_RESTART', None)
wpt.ENV.pop('MOZ_ANCESTOR_CANCELLATION_TRACE', None)
wpt.ENV.pop('MOZ_NESTED_EDGE_TRACE', None)
resources = {n: h for n, h in prior_pins.items() if n not in c['guard_sources'] and n not in wpt.BINARIES}
for n, h in read(HERE / 'RESOURCES.json').items():
    need(n not in resources or resources[n] == h, 'resource transfer conflict: ' + n)
    resources[n] = h
need(wpt.pins(list(resources)) == resources, 'initial resources')
owned_tests = tuple(c['install'])
need(len(owned_tests) == 2 and c['baseline_tests'] == c['tests']
     and set(c['candidate_sources']) == {'servo/components/style/values/generics/calc.rs', 'servo/components/style/values/specified/calc.rs', 'servo/components/style/values/specified/length.rs', 'servo/components/style/values/computed/length_percentage.rs'}
     and set(read(HERE / 'PLANNED-SCOPE.json')['guard_sources']) <= set(c['guard_sources'])
     and set(read(HERE / 'PLANNED-SCOPE.json')['sources']) <= set(c['sources']), 'comparison scope')
fixtures = {}
for owned_test in owned_tests:
    need(not (ROOT / owned_test).exists() and not (ROOT / owned_test).is_symlink()
         and not wpt.git('ls-files', '--', owned_test), 'test absent/untracked')
    fixtures[owned_test] = (HERE / c['install'][owned_test]).read_bytes()
    need(fixtures[owned_test] == (fixture_proposal / c['proposal_test_files'][owned_test]).read_bytes(), 'exact proposed WPT')
for name, proposal_file in c['proposal_test_files'].items():
    if name not in fixtures:
        need(name in c['existing_test_pins'] and sha(fixture_proposal / proposal_file) == c['existing_test_pins'][name],
             'readonly proposed WPT matches installed test')
phase_paths = c['phase_candidate_paths']
raw_paths = {'servo/components/style/values/specified/calc.rs', 'servo/components/style/values/specified/length.rs', 'servo/components/style/values/computed/length_percentage.rs'}
need(set(phase_paths) == {'baseline', 'raw_only', 'raw_plus_sign'}
     and phase_paths['baseline'] == [] and set(phase_paths['raw_only']) == raw_paths
     and set(phase_paths['raw_plus_sign']) == set(c['candidate_sources'])
     and all(len(paths) == len(set(paths)) for paths in phase_paths.values()), 'exact phase candidate maps')
raw_test = '/css/css-values/calc-relative-length-nonfinite-intermediates.html'
sign_test = '/css/css-values/sign-zero-font-basis.html'
need(c['landing_tests'] == [raw_test, sign_test]
     and c['phase_required_tests'] == {'raw_only': [raw_test], 'raw_plus_sign': [raw_test, sign_test]}
     and c['phase_repair_tests'] == {'raw_only': [raw_test], 'raw_plus_sign': [sign_test]}
     and c['phase_repair_basis'] == {'raw_only': 'baseline', 'raw_plus_sign': 'raw_only'}, 'exact variant acceptance families')
phase_pins = {phase: {n: c['candidate_pins'][n] for n in paths} for phase, paths in phase_paths.items()}
def phase_resources(phase):
    return {**resources, **c['head_pins'],
            **phase_pins[phase],
            **{n: hashlib.sha256(data).hexdigest() for n, data in fixtures.items()}}

def modified_native():
    return [n for n in wpt.git('diff', '--name-only').decode().splitlines() if not n.startswith('artifacts/')]
def untracked_native():
    return wpt.git('ls-files', '--others', '--exclude-standard', '--', 'layout', 'dom', 'servo', 'mfbt').decode().splitlines()
def existing_tests():
    need(wpt.pins(c['existing_tests']) == c['existing_test_pins'], 'read-only existing tests')
    for name, item in installed_tests.items():
        installed_test = ROOT / name
        info = installed_test.lstat()
        need(stat.S_ISREG(info.st_mode) and [info.st_dev, info.st_ino] == item['identity']
             and sha(installed_test) == item['sha256'], 'installed test identity changed')
    need(wpt.git('ls-files', '--', *c['existing_tests']).decode().splitlines() == c['tracked_existing_tests'], 'existing test ownership')
    for n, h in read(HERE / 'TEST-SOURCE-PINS.json').items():
        need(sha(ROOT / n) == h and hashlib.sha256(wpt.git('show', c['baseline_revision'] + ':' + n)).hexdigest() == h, 'comparison test HEAD binding')
existing_tests()
need(modified_native() == c['modified_native_paths'] and not untracked_native(), 'complete native roster')
need(({n for n, h in before['sources'].items() if h != c['head_pins'][n]} | set(c['candidate_sources']))
     <= set(c['sources']) <= set(c['guard_sources']), 'full normalization and saved original domain')
need(set(c['modified_native_paths']) <= set(c['sources']), 'save all current native differences')
head = {n: wpt.git('show', c['baseline_revision'] + ':' + n) for n in c['guard_sources']}
need({n: hashlib.sha256(b).hexdigest() for n, b in head.items()} == c['head_pins'], 'HEAD bodies')
original = {n: (ROOT / n).read_bytes() for n in c['sources']}
selected = {n: (ROOT / p).read_bytes() for n, p in c['candidate_sources'].items()}
need(set(selected) <= set(original) and {n: hashlib.sha256(b).hexdigest() for n, b in selected.items()} == c['candidate_pins'], 'candidate source')

def verify_phase(phase):
    now = wpt.snapshot()
    need(all(now[k] == before[k] for k in ('head', 'index_diff_sha256', 'index_entries_sha256')), 'HEAD/index changed')
    expected = {**c['head_pins'], **phase_pins[phase]}
    need(now['sources'] == expected, 'exact phase sources')
    need(sorted(n for n in wpt.git('diff', '--name-only', c['baseline_revision']).decode().splitlines() if not n.startswith('artifacts/')) == sorted(phase_paths[phase]) and not untracked_native(), 'complete phase diff')
    need(wpt.pins(list(phase_resources(phase))) == phase_resources(phase), 'phase resources')
    need(all(not (ROOT / n).exists() and not (ROOT / n).is_symlink() for n in c['must_be_absent']), 'prior temporary input appeared')
    for owned_test in owned_tests:
        need(not wpt.git('ls-files', '--', owned_test), 'owned test became tracked')
        owned_stat = (ROOT / owned_test).lstat()
        need(stat.S_ISREG(owned_stat.st_mode) and (owned_stat.st_dev, owned_stat.st_ino) == owned_identities[owned_test], 'owned fixture identity drift')
    existing_tests()
    authenticate(payloads, HERE)
    authenticate(refs, ROOT)

for n, data in original.items():
    p = HERE / 'original' / n
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(data)
wpt.save('BEFORE.json', before)
wpt.save('ORIGINAL-BINARIES.json', epoch['installed_binary_pins'])
state = {'status': 'starting', 'phases': {}, 'accepted_native_repair': False, 'original_source_role': 'actual root-bound restored working stack; normalize all differing saved native bodies to explicit HEAD90; candidate only explicitly reviewed bound source paths', 'pending_acceptance_gates': c['pending_acceptance_gates']}
changed = False
owned_identities = {}
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
    temp = path.with_name('.' + path.name + '.sign-split-comparison.tmp')
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
        target = head[n]
        if original[n] != target:
            changed = True
            replace_source(n, target)
    for owned_test, fixture in fixtures.items():
        with (ROOT / owned_test).open('xb') as stream:
            info = os.fstat(stream.fileno())
            owned_identities[owned_test] = (info.st_dev, info.st_ino)
            need(stream.write(fixture) == len(fixture), 'short fixture write')
    verify_phase('baseline')
    state['lint_exit'] = wpt.command('fixture-lint', ['./mach', 'lint', '--linter', 'wpt', *owned_tests])
    wpt.save('STATE.json', state)
    need(state['lint_exit'] == 0, 'owned WPT lint failed')
    verify_phase('baseline')
    runs = {}
    for phase in ('baseline', 'raw_only', 'raw_plus_sign'):
        for n in selected:
            data = selected[n] if n in phase_paths[phase] else head[n]
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
        if phase != 'baseline':
            basis = c['phase_repair_basis'][phase]
            record['semantic_comparison'] = tests.compare(wpt, runs['baseline'], runs[phase], phase, runs[basis])
        verify_phase(phase)
        wpt.save('STATE.json', state)
    state['campaign_completed'] = True
    state['all_variants_passed'] = all(state['phases'][p]['semantic_comparison']['status'] == 'PASSED'
                                      for p in ('raw_only', 'raw_plus_sign'))
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
    for owned_test, owned_identity in owned_identities.items():
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
            and wpt.pins(list(resources)) == resources
            and all(not (ROOT / n).exists() and not (ROOT / n).is_symlink()
                    and not wpt.git('ls-files', '--', n) for n in owned_tests)
            and all(not (ROOT / n).with_name('.' + Path(n).name + '.sign-split-comparison.tmp').exists()
                    and not (ROOT / n).with_name('.' + Path(n).name + '.sign-split-comparison.tmp').is_symlink() for n in c['sources']))
        state['restored_binary_pins'] = wpt.pins(wpt.BINARIES)
        recovery_save('FINAL.json', final)
        recovery_save('FINAL-PINS.json', {**resources, **final['sources'], **state['restored_binary_pins']})
    except BaseException as error:
        errors.append({'operation': 'final check', 'error': repr(error)})
    state['status'] = 'terminal'
    recovery_save('STATE.json', state)
print(json.dumps(state, indent=2))
if 'failure' in state or errors or not state['restored'] or (changed and state.get('restore_build_exit') != 0) or not state.get('all_variants_passed', False):
    raise SystemExit(1)
