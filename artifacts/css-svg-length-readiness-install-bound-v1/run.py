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
need(c['acceptance_receipt']['status'] == 'SCOPED_ACCEPTED' and c['acceptance_receipt']['fix'] == 114
     and c['acceptance_receipt']['landing_cases'] == 25, 'expanded114 scoped acceptance required')
proposal = ROOT / c['proposal']
authenticate(read(proposal / 'FILES.json'), proposal)
original_pins = {'dom/svg/DOMSVGLength.cpp': sha(ROOT / c['original_source_artifact'])}
candidate_pins = {'dom/svg/DOMSVGLength.cpp': sha(proposal / 'candidate/dom/svg/DOMSVGLength.cpp')}
accepted_patch = c['acceptance_receipt'].get('patch')
accepted_hash = (accepted_patch.get('sha256') if isinstance(accepted_patch, dict)
                 else c['acceptance_receipt'].get('native_patch_sha256'))
need(accepted_hash == sha(proposal / 'standalone.patch'), 'accepted exact expanded five-path patch')
wpt = load('install_wpt', ROOT / c['helpers'] / 'run_wpt.py')
bindings = load('install_bindings', ROOT / c['helpers'] / 'bindings.py')
tests = load('install_tests', ROOT / 'artifacts/css-svg-length-readiness-comparison-v1/tests.py')
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
prior_config = read(previous / 'CONFIG.json')
need(prior_config['epoch_receipt']['installed_tests'] == c['installed_tests']
     and len(c['installed_tests']) == 7, 'seven installed test identities transferred from comparison')
bindings.index_state(wpt)
before = wpt.snapshot()
need(before == prior_final and before['head'] == c['head']
     and before['sources'] == c['source_pins'], 'current restored source/index epoch')
need(wpt.pins(list(prior_pins)) == prior_pins, 'current restored resources and binaries')
resources = read(HERE / 'RESOURCES.json')
need(wpt.pins(list(resources)) == resources, 'initial resources')
natives = sorted(original_pins)
owned_tests = list(c['install'])
need(len(owned_tests) == 1 and sorted(c['sources']) == natives
     and set(c['tests']) == {'testing/web-platform/tests'+n for n in c['main_tests']}
     and len(c['expected_subtests']) == 3 and sum(map(len, c['expected_subtests'].values())) == 25
     and len(c['guard_sources']) == 53 and len(natives) == 1, 'integration scope')
need(all(before['sources'][n] == h for n, h in original_pins.items()), 'installed114 source has unrelated working changes')
fixtures = {n: (HERE / c['install'][n]).read_bytes() for n in owned_tests}
need(all(body == (proposal / c['proposal_test_files'][n]).read_bytes() for n, body in fixtures.items()), 'exact final fixtures')
for name, proposal_file in c['proposal_test_files'].items():
    if name not in fixtures:
        need(name in c['existing_test_pins'] and sha(proposal / proposal_file) == c['existing_test_pins'][name], 'existing main test remains exact')
need(before['sources']['dom/svg/DOMSVGLength.h'] == sha(proposal / 'candidate/dom/svg/DOMSVGLength.h'), 'installed114 header already matches')
candidate = {n: (ROOT / c['candidate_sources'][n]).read_bytes() for n in natives}
need({n: hashlib.sha256(b).hexdigest() for n, b in candidate.items()} == c['candidate_pins'] == candidate_pins, 'exact candidate')
original = {n: (ROOT / n).read_bytes() for n in natives}
need(all(not (ROOT / n).exists() and not (ROOT / n).is_symlink()
         and not wpt.git('ls-files', '--', n) for n in owned_tests), 'owned WPTs absent/untracked')
temps = [(ROOT / n).with_name('.' + Path(n).name + '.svg-readiness-install.tmp') for n in natives]
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
phase_resources = {**resources, **expected_sources, **{n: hashlib.sha256(b).hexdigest() for n, b in fixtures.items()}}
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
    for name in owned_tests:
        need(not wpt.git('ls-files', '--', name), 'owned WPT became tracked')
        info = (ROOT / name).lstat()
        need(stat.S_ISREG(info.st_mode) and (info.st_dev, info.st_ino) == owned_identities[name], 'owned WPT replaced')
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
owned_identities = {}
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
    temp = path.with_name('.' + path.name + '.svg-readiness-install.tmp')
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
    for name, fixture in fixtures.items():
        with (ROOT / name).open('xb') as stream:
            info = os.fstat(stream.fileno())
            owned_identities[name] = (info.st_dev, info.st_ino)
            need(stream.write(fixture) == len(fixture), 'short fixture write')
    verify_installed()
    state['lint_exit'] = wpt.command('fixture-lint', ['./mach', 'lint', '--linter', 'wpt', *owned_tests])
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
    need(len(result['rows']) == 25 and all(row['status'] == 'PASS' for row in result['rows']), 'own25 integration')
    need(all(result['before'][n] == h for n, h in state['installed_binary_pins'].items()), 'built binary/test join')
    final = verify_installed()
    need(wpt.pins(wpt.BINARIES) == state['installed_binary_pins'], 'binary drift')
    wpt.save('FINAL.json', final)
    wpt.save('FINAL-PINS.json', {**phase_resources, **state['installed_binary_pins']})
    state.update(status='terminal', installed=True, subtests={'PASS': 25, 'FAIL': 0}, files_ok=3)
    wpt.save('INSTALLATION.json', {'before': before, 'after': final,
        'original_source_pins': original_pins, 'installed_source_pins': candidate_pins,
        'owned_tests': {n: {'sha256': hashlib.sha256(fixtures[n]).hexdigest(),
                            'identity': owned_identities[n]} for n in owned_tests},
        'binary_pins': state['installed_binary_pins'],
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
        for name, identity in owned_identities.items():
            try:
                info = (ROOT / name).lstat()
                need(stat.S_ISREG(info.st_mode) and (info.st_dev, info.st_ino) == identity, 'owned WPT replaced; preserve replacement')
                (ROOT / name).unlink()
            except BaseException as error:
                errors.append({'operation': 'remove owned test ' + name, 'error': repr(error)})
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
                and all(not (ROOT / n).exists() and not (ROOT / n).is_symlink()
                        and not wpt.git('ls-files', '--', n) for n in owned_tests)
                and all(not p.exists() and not p.is_symlink() for p in temps)
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
