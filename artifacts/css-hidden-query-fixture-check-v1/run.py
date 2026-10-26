import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit('Require python3 -I -S without optimization')
sys.dont_write_bytecode = True
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--manifest-sha', required=True)
args = parser.parse_args()
def need(ok, message):
    if not ok:
        raise RuntimeError(message)
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
need(sha(HERE / 'INPUT-FILES.json') == args.manifest_sha, 'manifest identity')
manifest = json.loads((HERE / 'INPUT-FILES.json').read_text())
for name, pin in manifest.items():
    need(not Path(name).is_absolute() and '..' not in Path(name).parts, 'unsafe path')
    need(sha(HERE / name) == pin, 'input changed ' + name)
need(not (HERE / 'BEFORE.json').exists(), 'already run')
spec = importlib.util.spec_from_file_location('fixture_wpt', HERE / 'run_wpt.py')
wpt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wpt)
c = wpt.CONFIG
prior = ROOT / c['prior_runtime']
prior_state = json.loads((prior / 'STATE.json').read_text())
need(prior_state['status'] == 'terminal' and prior_state['restored'] is True
     and prior_state['restore_build_exit'] == 0 and prior_state['recovery_errors'] == [],
     'preceding experiment not restored')
before = wpt.snapshot()
need(before == json.loads((prior / 'FINAL.json').read_text()), 'restored source/HEAD/index changed')
need(not wpt.git('diff', '--cached', '--name-only').strip(), 'index not empty')
need(all(not (ROOT / n).exists() and not (ROOT / n).is_symlink() for n in c['install']),
     'temporary tests not absent')
resources = wpt.pins(wpt.resource_paths(c['tests'], virtual=True), virtual=True)
binaries = wpt.pins(wpt.BINARIES)
wpt.save('BEFORE.json', before)
wpt.save('INPUTS.json', {'resources': resources, 'binaries': binaries,
                       'prior_state_sha256': sha(prior / 'STATE.json'),
                       'prior_final_sha256': sha(prior / 'FINAL.json'),
                       'input_manifest_sha256': args.manifest_sha,
                       'scope': 'Restored working build with preserved native prototypes; fixture diagnostic only'})
installed = []
errors = []
state = {'status': 'starting', 'native_accepted': False, 'native_sources_written': False}
try:
    for target, source in c['install'].items():
        with (ROOT / target).open('xb') as stream:
            installed.append(target)
            stream.write((HERE / source).read_bytes())
    state['lint_exit'] = wpt.command('wpt-lint', ['./mach', 'lint', '-l', 'wpt', *c['tests']])
    need(state['lint_exit'] == 0, 'WPT lint failed')
    state['status'] = 'testing'
    wpt.save('STATE.json', state)
    state['wpt'] = wpt.test_run('fixtures', c['tests'], resources)
    run = json.loads((HERE / 'fixtures/RUN.json').read_text())
    state['counts'] = {status: sum(r['status'] == status for r in run['rows']) for status in ['PASS', 'FAIL']}
    state['failures'] = [{k: r.get(k) for k in ['test', 'subtest', 'message']}
                         for r in run['rows'] if r['status'] == 'FAIL']
except BaseException as error:
    state['failure'] = repr(error)
finally:
    for target in installed:
        try:
            (ROOT / target).unlink()
        except BaseException as error:
            errors.append({'target': target, 'error': repr(error)})
    final = wpt.snapshot()
    state['restored'] = (final == before and wpt.pins(wpt.BINARIES) == binaries
                         and all(not (ROOT / n).exists() for n in c['install'])
                         and wpt.pins(wpt.resource_paths(c['tests'], virtual=True), virtual=True) == resources)
    state['cleanup_errors'] = errors
    state['status'] = 'terminal'
    wpt.save('FINAL.json', final)
    wpt.save('STATE.json', state)
print(json.dumps(state, indent=2))
need('failure' not in state and not errors and state['restored'], 'diagnostic or restoration failed')
