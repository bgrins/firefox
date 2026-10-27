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
need(all(isinstance(c[n], str) and c[n] for n in ('epoch', 'epoch_manifest_sha256', 'acceptance', 'acceptance_sha256'))
     and c['epoch_receipt'] is not None and c['acceptance_receipt'] is not None, 'unbound epoch or acceptance')
need(all(not (HERE / n).exists() and not (HERE / n).is_symlink()
         for n in ('wpt-candidate', 'BEFORE.json', 'STATE.json', 'original')), 'already started/output collision')
acceptance = ROOT / c['acceptance']
need(sha(acceptance) == c['acceptance_sha256'] and read(acceptance) == c['acceptance_receipt'], 'exact acceptance')
need(c['acceptance_receipt']['status'] == 'SCOPED_ACCEPTED', 'root scoped acceptance required')
proposal = ROOT / c['proposal']
authenticate(read(proposal / 'FILES.json'), proposal)
source_pins = read(proposal / 'SOURCE-PINS.json')
original_pins = {n: v['before_sha256'] for n, v in source_pins.items()}
candidate_pins = {n: v['candidate_sha256'] for n, v in source_pins.items()}
accepted_patch = c['acceptance_receipt'].get('patch')
accepted_hash = (accepted_patch.get('sha256') if isinstance(accepted_patch, dict)
                 else c['acceptance_receipt'].get('native_patch_sha256'))
need(accepted_hash == sha(proposal / 'standalone.patch'), 'accepted exact three-path patch')
wpt = load('install_wpt', ROOT / c['helpers'] / 'run_wpt.py')
bindings = load('install_bindings', ROOT / c['helpers'] / 'bindings.py')
tests = load('install_tests', ROOT / 'artifacts/css-svg-length-conversion-comparison-v1/tests.py')
wpt.HERE, wpt.CONFIG = HERE, c
wpt.ENV.update(MOZ_DISABLE_SAFE_MODE_KEY='1', MOZ_DISABLE_UPDATE_PROCESSING='1')
wpt.ENV.pop('MOZ_SAFE_MODE_RESTART', None)
previous = ROOT / c['epoch']
need(sha(previous / 'FILES.json') == c['epoch_manifest_sha256'], 'comparison epoch seal')
authenticate(read(previous / 'FILES.json'), previous)
epoch, receipt = read(previous / 'STATE.json'), read(previous / 'ROOT-FINAL-CHECK.json')
need(epoch['status'] == 'terminal' and epoch['restored'] is True and epoch['restore_build_exit'] == 0
     and epoch['recovery_errors'] == [] and 'failure' not in epoch
     and epoch['paired_preservation_passed'] is True
     and set(epoch['phases']) == {'baseline', 'candidate'}
     and all(v['build_exit'] == 0 for v in epoch['phases'].values()), 'paired comparison terminal restoration')
need(receipt == c['epoch_receipt'] and receipt['state_sha256'] == sha(previous / 'STATE.json')
     and receipt['final_sha256'] == sha(previous / 'FINAL.json')
     and receipt['restored_binary_pins'] == epoch['restored_binary_pins'], 'exact root epoch receipt')
prior_final = read(previous / 'FINAL.json')
need(read(previous / 'BEFORE.json') == prior_final, 'restored comparison snapshot')
prior_pins = read(previous / 'FINAL-PINS.json')
need(prior_pins == {**read(previous / 'RESOURCES.json'), **prior_final['sources'],
                   **epoch['restored_binary_pins']}, 'complete restored role map')
for directory in ('css-cssom-client-install-runtime-v1', 'css-cssom-offset-scroll-install-runtime-v1',
                  'css-hidden-svg-matrix-install-runtime-v1'):
    installed = ROOT / 'artifacts' / directory
    authenticate(read(installed / 'FILES.json'), installed)
    item = read(installed / 'INSTALLATION.json')
    need(c['installed_tests'][item['owned_test']] == {
        'identity': item['owned_test_identity'], 'sha256': item['owned_test_sha256']}, 'installed test receipt join')
bindings.index_state(wpt)
before = wpt.snapshot()
need(before == prior_final and before['head'] == c['head']
     and before['sources'] == c['source_pins'], 'current restored source/index epoch')
need(wpt.pins(list(prior_pins)) == prior_pins, 'current restored resources and binaries')
resources = read(HERE / 'RESOURCES.json')
need(wpt.pins(list(resources)) == resources, 'initial resources')
natives = sorted(source_pins)
owned_test = next(iter(c['install']))
need(len(c['install']) == 1 and sorted(c['sources']) == natives and set(c['tests']) == {'testing/web-platform/tests'+n for n in c['main_tests']} and len(c['expected_subtests']) == 1
     and sum(map(len,c['expected_subtests'].values())) == 9 and len(c['guard_sources']) == 52 and len(natives) == 2, 'integration scope')
need(all(before['sources'][n] == h for n, h in original_pins.items()), 'DOMSVGLength sources have unrelated working changes')
fixture = (HERE / c['install'][owned_test]).read_bytes()
need(fixture == (proposal / 'candidate' / owned_test).read_bytes(), 'exact final fixture')
candidate = {n: (ROOT / c['candidate_sources'][n]).read_bytes() for n in natives}
need({n: hashlib.sha256(b).hexdigest() for n, b in candidate.items()} == c['candidate_pins'] == candidate_pins, 'exact candidate')
original = {n: (ROOT / n).read_bytes() for n in natives}
need(not (ROOT / owned_test).exists() and not (ROOT / owned_test).is_symlink()
     and not wpt.git('ls-files', '--', owned_test), 'owned WPT absent/untracked')
temps = [(ROOT / n).with_name('.' + Path(n).name + '.svg-length-install.tmp') for n in natives]
need(all(not p.exists() and not p.is_symlink() for p in temps), 'source temporary exists')

def modified_native():
    return [n for n in wpt.git('diff', '--name-only').decode().splitlines() if not n.startswith('artifacts/')]
def untracked_native():
    return wpt.git('ls-files', '--others', '--exclude-standard', '--', 'layout', 'dom', 'servo', 'mfbt').decode().splitlines()
def existing_tests():
    need(wpt.pins(c['existing_tests']) == c['existing_test_pins'], 'existing tests changed')
    for name, item in c['installed_tests'].items():
        old_test = ROOT / name
        info = old_test.lstat()
        need(stat.S_ISREG(info.st_mode) and [info.st_dev, info.st_ino] == item['identity']
             and sha(old_test) == item['sha256'] == c['existing_test_pins'][name], 'installed test ownership')
    need(wpt.git('ls-files', '--', *c['existing_tests']).decode().splitlines() == c['tracked_existing_tests'], 'existing test ownership')
need(modified_native() == c['modified_native_paths'] and not untracked_native(), 'native inventory')
existing_tests()
expected_sources = {**before['sources'], **candidate_pins}
phase_resources = {**resources, **expected_sources, owned_test: hashlib.sha256(fixture).hexdigest()}
def verify_installed():
    now = wpt.snapshot()
    need(all(now[k] == before[k] for k in ('head', 'index_diff_sha256', 'index_entries_sha256')), 'HEAD/index changed')
    need(now['sources'] == expected_sources, 'installed source roles')
    for name in natives:
        native_info = (ROOT / name).lstat()
        need(stat.S_ISREG(native_info.st_mode)
             and (native_info.st_dev, native_info.st_ino, candidate_pins[name]) in owned_sources[name], 'native inode replaced')
    need(sorted(modified_native()) == sorted(set(c['modified_native_paths']) | set(natives))
         and not untracked_native(), 'installed native inventory')
    need(wpt.pins(list(phase_resources)) == phase_resources, 'installed source/resource drift')
    need(all(not (ROOT / n).exists() and not (ROOT / n).is_symlink() for n in c['must_be_absent']), 'old temporary appeared')
    need(not wpt.git('ls-files', '--', owned_test), 'owned WPT became tracked')
    info = (ROOT / owned_test).lstat()
    need(stat.S_ISREG(info.st_mode) and (info.st_dev, info.st_ino) == owned_identity, 'owned WPT replaced')
    existing_tests()
    authenticate(payloads, HERE)
    authenticate(refs, ROOT)
    bindings.index_state(wpt)
    return now

for n, data in original.items():
    p = HERE / 'original' / n
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(data)
wpt.save('BEFORE.json', before)
wpt.save('ORIGINAL-BINARIES.json', epoch['restored_binary_pins'])
state = {'status': 'starting', 'installed': False, 'restored': False, 'sources': natives,
         'acceptance_sha256': c['acceptance_sha256'], 'recovery_errors': []}
owned_identity = None
changed = False
succeeded = False
errors = state['recovery_errors']
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
    temp = path.with_name('.' + path.name + '.svg-length-install.tmp')
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
    changed = True
    for name, body in candidate.items():
        replace_source(name, body)
    with (ROOT / owned_test).open('xb') as stream:
        info = os.fstat(stream.fileno())
        owned_identity = (info.st_dev, info.st_ino)
        need(stream.write(fixture) == len(fixture), 'short fixture write')
    verify_installed()
    state['lint_exit'] = wpt.command('fixture-lint', ['./mach', 'lint', '--linter', 'wpt', owned_test])
    need(state['lint_exit'] == 0, 'WPT lint failed')
    build_before = verify_installed()
    state['status'] = 'building'
    wpt.save('STATE.json', state)
    state['build_exit'] = wpt.command('installed-build', ['./mach', 'build', 'binaries'])
    need(state['build_exit'] == 0 and verify_installed() == build_before, 'installed build failed/source changed')
    state['installed_binary_pins'] = wpt.pins(wpt.BINARIES)
    state['status'] = 'testing'
    wpt.save('STATE.json', state)
    result = tests.run(wpt, 'candidate', phase_resources)
    tests.require_phase(wpt, 'candidate', result)
    need(len(result['rows']) == 9 and all(row['status'] == 'PASS' for row in result['rows']), 'own9 integration')
    need(all(result['before'][n] == h for n, h in state['installed_binary_pins'].items()), 'built binary/test join')
    final = verify_installed()
    need(wpt.pins(wpt.BINARIES) == state['installed_binary_pins'], 'binary drift')
    wpt.save('FINAL.json', final)
    wpt.save('FINAL-PINS.json', {**phase_resources, **state['installed_binary_pins']})
    state.update(status='terminal', installed=True, subtests={'PASS': 9, 'FAIL': 0}, files_ok=1)
    wpt.save('INSTALLATION.json', {'before': before, 'after': final,
        'original_source_pins': original_pins, 'installed_source_pins': candidate_pins,
        'owned_test': owned_test, 'owned_test_sha256': hashlib.sha256(fixture).hexdigest(),
        'owned_test_identity': owned_identity, 'binary_pins': state['installed_binary_pins'],
        'acceptance_sha256': c['acceptance_sha256']})
    wpt.save('STATE.json', state)
    succeeded = True
except BaseException as error:
    state.update(installed=False, failure={'type': type(error).__name__, 'message': str(error)})
finally:
    if not succeeded:
        def recovery_save(name, data):
            try:
                wpt.save(name, data)
            except BaseException as error:
                errors.append({'operation': 'save ' + name, 'error': repr(error)})
        state['status'] = 'restoring'
        recovery_save('STATE.json', state)
        for name, body in original.items():
            try:
                replace_source(name, body)
            except BaseException as error:
                errors.append({'operation': 'restore ' + name, 'error': repr(error)})
        if owned_identity is not None:
            try:
                info = (ROOT / owned_test).lstat()
                need(stat.S_ISREG(info.st_mode) and (info.st_dev, info.st_ino) == owned_identity, 'owned WPT replaced; preserve replacement')
                (ROOT / owned_test).unlink()
            except BaseException as error:
                errors.append({'operation': 'remove owned test', 'error': repr(error)})
        state['original_source_restored'] = False
        state['all_native_sources_restored'] = False
        try:
            state['original_source_restored'] = all((ROOT / n).read_bytes() == b for n, b in original.items())
            state['all_native_sources_restored'] = (wpt.snapshot()['sources'] == before['sources']
                and modified_native() == c['modified_native_paths'] and not untracked_native())
            need(state['original_source_restored'] and state['all_native_sources_restored'], 'native restoration incomplete; withhold build')
        except BaseException as error:
            errors.append({'operation': 'verify source restoration', 'error': repr(error)})
        if changed and state['original_source_restored'] and state['all_native_sources_restored']:
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
        try:
            final = wpt.snapshot()
            existing_tests()
            bindings.index_state(wpt)
            state['restored'] = (final == before and modified_native() == c['modified_native_paths']
                and not untracked_native() and wpt.pins(list(resources)) == resources
                and not (ROOT / owned_test).exists() and not (ROOT / owned_test).is_symlink()
                and not wpt.git('ls-files', '--', owned_test) and all(not p.exists() and not p.is_symlink() for p in temps)
                and all(not (ROOT / n).exists() and not (ROOT / n).is_symlink() for n in c['must_be_absent']))
            state['restored_binary_pins'] = wpt.pins(wpt.BINARIES)
            recovery_save('FINAL.json', final)
            recovery_save('FINAL-PINS.json', {**resources, **final['sources'], **state['restored_binary_pins']})
        except BaseException as error:
            errors.append({'operation': 'final check', 'error': repr(error)})
        state['status'] = 'terminal'
        recovery_save('STATE.json', state)
print(json.dumps(state, indent=2))
if not succeeded:
    raise SystemExit(1)
