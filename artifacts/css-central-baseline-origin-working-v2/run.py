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
import signal
import stat
import subprocess
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
EPOCH = ROOT / 'artifacts/css-wide-baseline-interface-compile-runtime-v1'
FIXTURE = ROOT / 'artifacts/css-central-baseline-origin-oracle-v2/central-baseline-source-margin-center.html'
DEST = 'testing/web-platform/tests/css/css-inline/central-baseline-source-margin-center.html'
TEST = '/css/css-inline/central-baseline-source-margin-center.html'
EXPECTED = [f'{wm}: {source} source, block margins {s}px / {e}px'
            for wm in ('vertical-rl', 'vertical-lr') for s, e in ((10, 30), (30, 10), (20, 20))
            for source in ('first', 'last')]

def need(ok, why):
    if not ok:
        raise RuntimeError(why)
def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):
    return json.loads(p.read_text())
def save(name, value):
    (HERE / name).write_text(json.dumps(value, indent=2) + '\n')
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

def infrastructure_faults(events):
    faults = []
    for e in events:
        a = e.get('action')
        if a in ('crash', 'suite_abort', 'test_abort'):
            faults.append(e)
        elif a == 'log' and e.get('level', '').upper() in ('ERROR', 'CRITICAL'):
            faults.append(e)
        elif a == 'process_exit' and e.get('exitcode', e.get('returncode', 0)) != 0:
            faults.append(e)
        elif a == 'assertion_count' and not e.get('min_expected', 0) <= e['count'] <= e.get('max_expected', 0):
            faults.append(e)
        elif a in ('log', 'process_output') and any(t in e.get('message', '') + e.get('data', '')
                for t in ('PROCESS-CRASH', 'TEST-UNEXPECTED-ERROR', 'TEST-UNEXPECTED-TIMEOUT')):
            faults.append(e)
    return faults

parser = argparse.ArgumentParser()
parser.add_argument('--draft-sha', required=True)
parser.add_argument('--epoch-sha', required=True)
parser.add_argument('--execute', action='store_true')
args = parser.parse_args()
need(args.execute, 'explicit --execute required')
need(sha(HERE / 'DRAFT-FILES.json') == args.draft_sha, 'draft seal')
authenticate(read(HERE / 'DRAFT-FILES.json'), HERE)
authenticate(read(HERE / 'REFERENCES.json'), ROOT)
need(sha(EPOCH / 'FILES.json') == args.epoch_sha, 'terminal interface seal required')
authenticate(read(EPOCH / 'FILES.json'), EPOCH)
epoch = read(EPOCH / 'STATE.json')
receipt = read(EPOCH / 'ROOT-FINAL-CHECK.json')
need(epoch['status'] == 'terminal' and epoch['restored'] is True and epoch['restore_build_exit'] == 0
     and not epoch['recovery_errors'] and 'failure' not in epoch
     and epoch['phases']['candidate']['build_exit'] == 0, 'wait for successful interface restoration')
need(receipt['state_sha256'] == sha(EPOCH / 'STATE.json') and receipt['final_sha256'] == sha(EPOCH / 'FINAL.json')
     and receipt['restored_binary_pins'] == epoch['restored_binary_pins'], 'root restoration join')
need(read(EPOCH / 'BEFORE.json') == read(EPOCH / 'FINAL.json'), 'interface restoration')
need(not any((HERE / n).exists() for n in ('STATE.json', 'BEFORE.json', 'raw.json')), 'already started')
c = read(EPOCH / 'CONFIG.json')
wpt = load('central_wpt', ROOT / c['helpers'] / 'run_wpt.py')
bindings = load('central_bindings', ROOT / c['helpers'] / 'bindings.py')
wpt.CONFIG = c
resources = {**read(EPOCH / 'RESOURCES.json'), **read(HERE / 'EXTRA-RESOURCES.json')}
path = ROOT / DEST
need(not path.exists() and not path.is_symlink() and not wpt.git('ls-files', '--', DEST), 'test must be absent/untracked')
fixture = FIXTURE.read_bytes()

def verify():
    bindings.index_state(wpt)
    snapshot = wpt.snapshot()
    need(snapshot == read(EPOCH / 'FINAL.json'), 'source/index epoch drift')
    need(wpt.pins(wpt.BINARIES) == epoch['restored_binary_pins'], 'binary epoch drift')
    need(wpt.pins(list(resources)) == resources, 'resource drift')
    need(wpt.pins(c['existing_tests']) == c['existing_test_pins'], 'existing WPT drift')
    need(wpt.git('ls-files', '--', *c['existing_tests']).decode().splitlines() == c['tracked_existing_tests'], 'existing WPT ownership')
    need([n for n in wpt.git('diff', '--name-only').decode().splitlines() if not n.startswith('artifacts/')]
         == c['modified_native_paths'], 'tracked nonartifact diff drift')
    need(not wpt.git('ls-files', '--others', '--exclude-standard', '--', 'layout', 'dom', 'servo', 'mfbt'), 'untracked native drift')
    need(all(not (ROOT / n).exists() and not (ROOT / n).is_symlink() for n in c['must_be_absent']), 'prior temporary input appeared')
    authenticate(read(HERE / 'REFERENCES.json'), ROOT)
    return {'snapshot': snapshot, 'binary_pins': wpt.pins(wpt.BINARIES), 'resource_pins': wpt.pins(list(resources))}

before = verify()
save('BEFORE.json', before)
save('EPOCH-USED.json', {'runtime': str(EPOCH.relative_to(ROOT)), 'files_sha256': args.epoch_sha,
                       'state_sha256': sha(EPOCH / 'STATE.json'), 'root_receipt_sha256': sha(EPOCH / 'ROOT-FINAL-CHECK.json')})
state = {'status': 'starting', 'restored': False, 'source_role': 'restored working build; not normalized HEAD or paired repair', 'cleanup_errors': []}
owned = process = None
try:
    with path.open('xb') as output:
        st = os.fstat(output.fileno())
        owned = (st.st_dev, st.st_ino)
        output.write(fixture)
    need(path.read_bytes() == fixture, 'fixture differs')
    state['status'] = 'testing'
    save('STATE.json', state)
    command = ['./mach', 'wpt', '--headless', '--processes=1', '--log-raw=' + str(HERE / 'raw.json'), DEST]
    save('COMMAND.json', command)
    with (HERE / 'wpt.log').open('w') as log:
        process = subprocess.Popen(command, cwd=ROOT, env=wpt.ENV, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
        state['wpt_exit'] = process.wait(timeout=300)
    events = [json.loads(line) for line in (HERE / 'raw.json').read_text().splitlines()]
    rows = [e for e in events if e.get('action') == 'test_status']
    starts = [e for e in events if e.get('action') == 'test_start']
    ends = [e for e in events if e.get('action') == 'test_end']
    faults = infrastructure_faults(events)
    save('RESULT.json', {'rows': rows, 'starts': starts, 'ends': ends, 'infrastructure_faults': faults, 'wpt_exit': state['wpt_exit']})
    need(len(starts) == len(ends) == 1 and starts[0]['test'] == ends[0]['test'] == TEST
         and ends[0]['status'] == 'OK' and [r['subtest'] for r in rows] == EXPECTED
         and all(r['test'] == TEST and r['status'] in ('PASS', 'FAIL') for r in rows)
         and sum(e.get('action') == 'suite_start' for e in events) == 1
         and sum(e.get('action') == 'suite_end' for e in events) == 1 and not faults, 'incomplete twelve-case harness')
    need(state['wpt_exit'] == 0 or (state['wpt_exit'] == 1 and any(r['status'] == 'FAIL' for r in rows)), 'unexpected harness exit')
    state['subtests'] = {s: sum(r['status'] == s for r in rows) for s in ('PASS', 'FAIL')}
    state['complete'] = True
    need(path.read_bytes() == fixture, 'fixture changed during WPT')
    save('AFTER-RUN.json', verify())
except BaseException as error:
    state['failure'] = {'type': type(error).__name__, 'message': str(error)}
finally:
    if process is not None:
        try:
            for sig in (signal.SIGTERM, signal.SIGKILL):
                try:
                    os.killpg(process.pid, sig)
                except ProcessLookupError:
                    break
                time.sleep(0.2)
            process.wait(timeout=10)
            try:
                os.killpg(process.pid, 0)
            except ProcessLookupError:
                state['owned_process_group_absent'] = True
            else:
                raise RuntimeError('owned process group remains alive')
        except BaseException as error:
            state['cleanup_errors'].append(repr(error))
    if owned is not None:
        try:
            st = path.lstat()
            need(stat.S_ISREG(st.st_mode) and (st.st_dev, st.st_ino) == owned, 'owned test replaced; preserve replacement')
            path.unlink()
        except BaseException as error:
            state['cleanup_errors'].append(repr(error))
    try:
        final = verify()
        need(not path.exists() and not path.is_symlink() and not wpt.git('ls-files', '--', DEST), 'test cleanup/ownership')
        save('FINAL.json', final)
        state['restored'] = final == before and not state['cleanup_errors']
    except BaseException as error:
        state['cleanup_errors'].append(repr(error))
    state['status'] = 'terminal'
    save('STATE.json', state)
print(json.dumps(state, indent=2))
raise SystemExit(0 if state.get('complete') and state['restored'] and 'failure' not in state else 1)
