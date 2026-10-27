import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit('Require python3 -I -S without optimization')
sys.dont_write_bytecode = True
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import stat
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]

def need(ok, why):
    if not ok:
        raise RuntimeError(why)

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def load(name):
    spec = importlib.util.spec_from_file_location(name, HERE / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def authenticate(base, pins):
    for name, digest in pins.items():
        need(not Path(name).is_absolute() and '..' not in Path(name).parts, 'unsafe input')
        path = base / name
        need(stat.S_ISREG(path.lstat().st_mode) and sha(path) == digest, 'input changed ' + name)

def apply_insertions(original, patch):
    lines = patch.splitlines(keepends=True)
    result = {}
    index = 0
    while index < len(lines):
        need(lines[index].startswith('--- a/'), 'patch file header')
        name = lines[index][6:].rstrip('\n')
        need(name in original and name not in result, 'unexpected patch target')
        index += 1
        need(lines[index] == '+++ b/' + name + '\n', 'patch target differs')
        index += 1
        old = original[name].decode().splitlines(keepends=True)
        new = []
        cursor = 0
        while index < len(lines) and not lines[index].startswith('--- a/'):
            match = re.fullmatch(r'@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@.*\n', lines[index])
            need(match is not None, 'patch hunk header')
            start = int(match[1]) - 1
            need(cursor <= start <= len(old), 'patch hunk position')
            new.extend(old[cursor:start])
            cursor = start
            old_count = new_count = 0
            index += 1
            while index < len(lines) and not lines[index].startswith(('@@ ', '--- a/')):
                line = lines[index]
                if line.startswith(' '):
                    need(cursor < len(old) and old[cursor] == line[1:], 'patch context mismatch')
                    new.append(old[cursor])
                    cursor += 1
                    old_count += 1
                else:
                    need(line.startswith('+'), 'trace patch must contain only insertions')
                    new.append(line[1:])
                new_count += 1
                index += 1
            need(old_count == int(match[2] or 1) and new_count == int(match[4] or 1), 'hunk length')
        new.extend(old[cursor:])
        result[name] = ''.join(new).encode()
    need(set(result) == set(original), 'five patch targets required')
    return result

parser = argparse.ArgumentParser()
parser.add_argument('--inputs-sha', required=True)
parser.add_argument('--restored-float-runtime', required=True)
parser.add_argument('--prior-state-sha', required=True)
parser.add_argument('--prior-final-sha', required=True)
parser.add_argument('--execute', action='store_true')
args = parser.parse_args()
need(args.execute, 'explicit root execution required after float restoration')
need(sha(HERE / 'INPUT-FILES.json') == args.inputs_sha, 'input manifest identity')
authenticate(HERE, json.loads((HERE / 'INPUT-FILES.json').read_text()))
c = json.loads((HERE / 'CONFIG.json').read_text())
need(c.get('ready_for_execution') is True, 'disabled draft: root must review and reseal')
need(not (HERE / 'BEFORE.json').exists(), 'already started')
for name, digest in json.loads((HERE / 'DEPENDENCIES.json').read_text()).items():
    authenticate(ROOT, {name: digest})
    dependency = ROOT / name
    authenticate(dependency.parent, json.loads(dependency.read_text()))
wpt = load('run_wpt')
index_check = load('index_check')
need(wpt.CONFIG == c and len(c['guard_sources']) == 34 and len(c['sources']) == 5
     and len(c['tests']) == 1 and c['tests'] == list(c['install']), 'exact trace scope')
index_check.index_state(wpt)
before = wpt.snapshot()
need(before['head'] == c['expected_head'], 'HEAD changed')
need(set(c['original_source_pins']) == set(c['instrumented_source_pins']) == set(c['sources']), 'five source roles')
need(all(before['sources'][n] == h for n, h in c['original_source_pins'].items()), 'working original source changed')
need(len(c['mathml_source_pins']) == 6
     and all(before['sources'][n] == h for n, h in c['mathml_source_pins'].items()),
     'original MathML8 source binding changed')
need(wpt.pins(list(c['supporting_source_pins'])) == c['supporting_source_pins'], 'constructor/API source changed')
prior = (ROOT / args.restored_float_runtime).resolve()
need(ROOT / 'artifacts' in prior.parents and prior != HERE, 'prior receipt must be a separate artifact directory')
need(sha(prior / 'STATE.json') == args.prior_state_sha and sha(prior / 'FINAL.json') == args.prior_final_sha, 'prior receipt pins')
prior_state = json.loads((prior / 'STATE.json').read_text())
prior_final = json.loads((prior / 'FINAL.json').read_text())
need(prior_state.get('status') == 'terminal' and prior_state.get('restored') is True
     and prior_state.get('restore_build_exit') == 0
     and not prior_state.get('recovery_errors', []) and not prior_state.get('cleanup_errors', []), 'float not successfully restored')
need(json.loads((prior / 'BEFORE.json').read_text()) == prior_final, 'float before/final differs')
need(all(prior_final[k] == before[k] for k in ['head', 'index_diff_sha256', 'index_entries_sha256', 'native_diff_sha256'])
     and set(c['prior_guard_sources']) <= set(prior_final['sources']) <= set(before['sources'])
     and all(before['sources'][n] == h for n, h in prior_final['sources'].items()), 'restored float state differs')
need(all(not (ROOT / n).exists() and not (ROOT / n).is_symlink() for n in c['must_be_absent']), 'temporary test exists')
need(wpt.pins(c['existing_tests']) == c['existing_test_pins'], 'accepted tests changed')
need(set(wpt.git('ls-files', '--', *c['existing_tests']).decode().splitlines()) == set(c['tracked_tests']), 'accepted test ownership changed')
resources = json.loads((HERE / 'RESOURCE-EXPECTATIONS.json').read_text())
need(set(wpt.resource_paths(c['tests'], virtual=True)) <= set(resources)
     and wpt.pins(list(resources), virtual=True) == resources, 'resource expectations changed')
original = {}
for name in c['sources']:
    need(stat.S_ISREG((ROOT / name).lstat().st_mode), 'native source is not a regular file')
    original[name] = (ROOT / name).read_bytes()
proposed = apply_insertions(original, (HERE / c['instrumentation']).read_text())
need({n: hashlib.sha256(v).hexdigest() for n, v in proposed.items()} == c['instrumented_source_pins'], 'proposed source pins')
expected = {(r['test'], r['subtest']): (r['status'], r['message'])
            for r in json.loads((HERE / 'EXPECTED-OUTCOMES.json').read_text())}
need(len(expected) == 8 and sum(v[0] == 'PASS' for v in expected.values()) == 6, 'exact six-pass two-fail oracle')
for name, data in original.items():
    path = HERE / 'original' / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
wpt.save('BEFORE.json', before)
wpt.save('INPUTS.json', {'prior_runtime': str(prior.relative_to(ROOT)), 'prior_state_sha256': args.prior_state_sha,
    'prior_final_sha256': args.prior_final_sha, 'manifest_sha256': args.inputs_sha,
    'resources': resources, 'initial_binaries': wpt.pins(wpt.BINARIES), 'source_role': 'restored working originals with accepted overlays; no HEAD normalization'})
state = {'status': 'starting', 'accepted_native_repair': False, 'phases': {}, 'restored': False}
errors = []
changed = False
owned_test = False
test = c['tests'][0]
owned_test_hash = None

def epoch(sources):
    now = wpt.snapshot()
    need(all(now[k] == before[k] for k in ['head', 'index_diff_sha256', 'index_entries_sha256']), 'HEAD/index changed')
    need(now['sources'] == {**before['sources'], **sources}, '34-source guard changed')
    need(wpt.pins(c['existing_tests']) == c['existing_test_pins'], 'accepted test drift')
    need(wpt.pins(list(c['supporting_source_pins'])) == c['supporting_source_pins'], 'constructor/API source drift')

def recovery_save(name, value):
    try:
        wpt.save(name, value)
    except BaseException as error:
        errors.append({'operation': 'save ' + name, 'error': repr(error)})

try:
    for name, data in proposed.items():
        changed = True
        (ROOT / name).write_bytes(data)
    epoch(c['instrumented_source_pins'])
    state['status'] = 'building instrumented'
    wpt.save('STATE.json', state)
    state['instrumented_build_exit'] = wpt.command('instrumented-build', ['./mach', 'build', 'binaries'])
    need(state['instrumented_build_exit'] == 0, 'instrumented build failed')
    epoch(c['instrumented_source_pins'])
    instrumented_binaries = wpt.pins(wpt.BINARIES)
    need(all(instrumented_binaries.values()), 'instrumented binaries absent')
    for phase, payload in [('control', 'tests/original.html'), ('marked', 'tests/marked.html')]:
        if not owned_test:
            with (ROOT / test).open('xb') as stream:
                owned_test = True
                stream.write((HERE / payload).read_bytes())
        else:
            need(stat.S_ISREG((ROOT / test).lstat().st_mode) and sha(ROOT / test) == owned_test_hash, 'owned temporary test changed')
            (ROOT / test).write_bytes((HERE / payload).read_bytes())
        owned_test_hash = sha(ROOT / test)
        phase_resources = {**resources, test: owned_test_hash}
        epoch(c['instrumented_source_pins'])
        need(wpt.pins(list(phase_resources)) == phase_resources, 'phase resources changed')
        state['status'] = 'testing ' + phase
        record = state['phases'][phase] = {'source_role': 'instrumented restored working originals',
            'source_pins': wpt.pins(c['guard_sources']), 'binary_role': 'instrumented build',
            'binary_pins': instrumented_binaries, 'test_sha256': owned_test_hash}
        wpt.save('STATE.json', state)
        record['lint_exit'] = wpt.command(phase + '-wpt-lint',
            ['./mach', 'lint', '-l', 'wpt', *c['tests']])
        exception = c['marked_lint_exception']
        record['lint_exception_applied'] = (
            phase == 'marked' and record['lint_exit'] == exception['exit'] == 1
            and owned_test_hash == exception['fixture_sha256']
            and sha(HERE / exception['expected_output']) == exception['expected_output_sha256']
            and (HERE / (phase + '-wpt-lint.log')).read_bytes()
                == (HERE / exception['expected_output']).read_bytes())
        record['lint_policy'] = ('exact diagnostic CONSOLE exception'
            if record['lint_exception_applied'] else 'unchanged control requires lint exit zero')
        wpt.save('STATE.json', state)
        need((phase == 'control' and record['lint_exit'] == 0)
             or record['lint_exception_applied'], 'scoped WPT lint policy failed ' + phase)
        epoch(c['instrumented_source_pins'])
        need(wpt.pins(list(phase_resources)) == phase_resources, 'lint changed phase resources')
        need(wpt.pins(wpt.BINARIES) == instrumented_binaries, 'lint changed binaries')
        record['wpt'] = wpt.test_run(phase, c['tests'], phase_resources)
        run = json.loads((HERE / phase / 'RUN.json').read_text())
        rows = {(r['test'], r['subtest']): (r['status'], r.get('message')) for r in run['rows']}
        record['outcome_messages_match_original'] = rows == expected
        epoch(c['instrumented_source_pins'])
        need(wpt.pins(wpt.BINARIES) == instrumented_binaries, 'binary drift')
        wpt.save('STATE.json', state)
        need(rows == expected, 'original keyed outcomes/messages changed ' + phase)
        if phase == 'marked':
            record['extract_exit'] = wpt.command('extract-trace', ['python3', '-I', '-S',
                str(HERE / 'extract_trace.py'), str(HERE / phase / 'raw.json'), str(HERE / 'recount')])
            need(record['extract_exit'] == 0, 'incomplete native trace or copied first/repeat rows')
            record['copied_rows_role'] = 'marked original-eight fixture; unchanged control does not emit stored arrays'
except BaseException as error:
    state['failure'] = repr(error)
finally:
    state['status'] = 'restoring'
    recovery_save('STATE.json', state)
    for name, data in original.items():
        try:
            need(stat.S_ISREG((ROOT / name).lstat().st_mode), 'source path replaced')
            (ROOT / name).write_bytes(data)
        except BaseException as error:
            errors.append({'operation': 'restore ' + name, 'error': repr(error)})
    if owned_test:
        try:
            need(stat.S_ISREG((ROOT / test).lstat().st_mode), 'owned test replaced')
            (ROOT / test).unlink()
        except BaseException as error:
            errors.append({'operation': 'remove owned temporary test', 'error': repr(error)})
    if changed:
        try:
            try:
                log = (HERE / 'restore-build.log').open('w')
            except OSError as error:
                errors.append({'operation': 'open restore log', 'error': repr(error)})
                log = None
            try:
                state['restore_build_exit'] = subprocess.run(['./mach', 'build', 'binaries'],
                    cwd=ROOT, env=wpt.ENV, stdout=log, stderr=subprocess.STDOUT).returncode
            finally:
                if log is not None:
                    log.close()
        except BaseException as error:
            errors.append({'operation': 'restore build', 'error': repr(error)})
    try:
        final = wpt.snapshot()
        index_check.index_state(wpt)
        state['restored'] = (final == before and state.get('restore_build_exit') == 0
            and all(not (ROOT / n).exists() and not (ROOT / n).is_symlink() for n in c['must_be_absent'])
            and wpt.pins(list(resources), virtual=True) == resources
            and wpt.pins(c['existing_tests']) == c['existing_test_pins']
            and wpt.pins(list(c['supporting_source_pins'])) == c['supporting_source_pins']
            and sha(prior / 'STATE.json') == args.prior_state_sha
            and sha(prior / 'FINAL.json') == args.prior_final_sha)
        state['restored_binary_pins'] = wpt.pins(wpt.BINARIES)
        state['restored_binary_role'] = 'rebuilt from original working sources; byte identity with initial binaries not assumed'
        recovery_save('FINAL.json', final)
    except BaseException as error:
        errors.append({'operation': 'final verification', 'error': repr(error)})
    state['recovery_errors'] = errors
    state['status'] = 'terminal'
    recovery_save('STATE.json', state)
print(json.dumps(state, indent=2))
need('failure' not in state and not errors and state['restored'], 'diagnosis or restoration failed')
