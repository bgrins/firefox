import copy
from collections import Counter
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
EXEC = ROOT / 'artifacts/css-number-native-differential-review-20261110-v1/execution'
PROTOCOL = ROOT / 'artifacts/css-number-native-differential-protocol-20261110-v1'
MODEL = ROOT / 'artifacts/css-number-lexical-bridge-20261110-v1'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path):
    return json.loads(path.read_text())


def module(name):
    spec = importlib.util.spec_from_file_location(name, PROTOCOL / (name + '.py'))
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def main():
    assert sha(PROTOCOL / 'SOURCE-ONLY.json') == '85f92d0dd4674b3bd8f6b16f53b75859cc8511ce05002d0d89edf3c4ca9adadf'
    assert sha(MODEL / 'SOURCE-ONLY.json') == 'da110adb89e5f7ef20ca2cc24f92fa4b9cff428f9751a16940ecb0d9b73427ba'
    inputs = []
    for capsule in [PROTOCOL, MODEL]:
        for name, digest in load(capsule / 'SOURCE-ONLY.json').items():
            assert sha(capsule / name) == digest
            inputs.append({'path': str((capsule / name).relative_to(ROOT)), 'sha256': digest})
    files = load(PROTOCOL / 'MATERIALIZE.json')['files']
    instrument = module('instrument').instrument
    for row in files:
        data = subprocess.check_output(['git', '-c', 'core.fsmonitor=false', 'show', row['commit'] + ':' + row['path']], cwd=ROOT)
        assert hashlib.sha256(data).hexdigest() == row['sha256']
        assert (EXEC / 'scratch/materialized' / row['destination']).read_bytes() == data
        for mode in ['plain', 'instrumented']:
            expected = instrument(data.decode()).encode() if mode == 'instrumented' and row['destination'] == 'vendor/cssparser/src/tokenizer.rs' else data
            assert (EXEC / 'scratch' / mode / row['destination']).read_bytes() == expected
    assert len(files) == 64
    toolchain = load(PROTOCOL / 'inputs/legacy-toolchain.json')
    assert sha(Path(toolchain['rustc'])) == toolchain['rustc_sha256']
    result = load(EXEC / 'RESULT.json')
    assert result['status'] == 'PASS'
    artifacts = {}
    for mode in ['plain', 'instrumented']:
        assert (EXEC / 'scratch' / mode / 'driver.rs').read_bytes() == (PROTOCOL / 'driver.rs').read_bytes()
        commands = load(EXEC / (mode + '-COMMANDS.json'))
        assert len(commands) == 6 and commands == load(EXEC / 'scratch' / mode / 'COMMANDS.json')
        assert load(EXEC / (mode + '-BUILD.json')) == load(EXEC / 'scratch' / mode / 'BUILD.json')
        for row in commands:
            assert row['exit'] == 0 and row['command'][0] == toolchain['rustc']
            assert '--cfg' not in row['command'] and 'opt-level=1' in row['command']
            output = Path(row['command'][row['command'].index('-o') + 1])
            assert output.is_relative_to(EXEC / 'scratch' / mode) and output.is_file()
            artifacts[str(output.relative_to(EXEC))] = sha(output)
        assert sha(EXEC / 'scratch' / mode / 'numeric') == result['binaries'][mode]
    commands = load(EXEC / 'COMMANDS.json')
    assert len(commands) == 50 and len({row['label'] for row in commands}) == 50
    for row in commands:
        assert row['exit'] == 0
        assert sha(EXEC / (row['label'] + '.stdout')) == row['stdout_sha256']
        assert sha(EXEC / (row['label'] + '.stderr')) == row['stderr_sha256']
    model_builds = [row for row in commands if row['label'].startswith('model-') and row['label'] != 'model-rows']
    assert len(model_builds) == 44
    for name, digest in load(MODEL / 'SOURCE-ONLY.json').items():
        assert sha(EXEC / 'scratch/model' / name) == digest
    lean = ROOT / 'artifacts/stylo-bloom-tools/lean-4.35.0-rc4-darwin_aarch64/bin/lean'
    assert sha(lean) == 'd1d9c26a539f54fe839d2aa7760bf1ac1dd76a30b26e2c9684bebf2900038fcf'
    prior = load(ROOT / 'artifacts/css-number-lexical-bridge-review-20261110-v1/replay/report.json')
    for row in model_builds:
        assert row['command'][0] == str(lean)
        path = row['command'][-1]
        assert path.endswith('.lean') and (EXEC / 'scratch/model' / path).is_file()
        combined = (EXEC / (row['label'] + '.stdout')).read_bytes() + (EXEC / (row['label'] + '.stderr')).read_bytes()
        assert hashlib.sha256(combined).hexdigest() == prior['commands']['build-' + path.replace('/', '-')]['output_sha256']
    model_command = next(row for row in commands if row['label'] == 'model-rows')
    assert model_command['command'] == [str(lean), '--run', 'Runner.lean', str(MODEL / 'number.json'), str(PROTOCOL / 'prepared/model-input.json')]
    cases = load(PROTOCOL / 'prepared/CASES.json')
    assert cases == module('cases').cases()
    assert len(cases) == len({row['id'] for row in cases}) == 196
    admitted = [row for row in cases if row['bridge_eligible']]
    assert len(admitted) == 180
    assert load(PROTOCOL / 'prepared/model-ids.json') == [row['id'] for row in admitted]
    assert load(PROTOCOL / 'prepared/model-input.json') == [[row['tail'], False] for row in admitted]
    native_lines = (PROTOCOL / 'prepared/native-input.tsv').read_text().splitlines()
    assert len(native_lines) == len(cases)
    for line, case in zip(native_lines, cases):
        assert line.split('\t') == [case['id'], str(case['warmup_tokens']), str(case['prefix_utf8_bytes']), case['mode'], (case['prefix'] + case['tail']).encode().hex()]
    comparator = module('compare')
    plain = comparator.public_rows((EXEC / 'native-plain.stdout').read_text())
    instrumented = comparator.public_rows((EXEC / 'native-instrumented.stdout').read_text())
    plain_trace = comparator.trace_rows((EXEC / 'native-plain.stderr').read_text())
    trace = comparator.trace_rows((EXEC / 'native-instrumented.stderr').read_text())
    model = [json.loads(line) for line in (EXEC / 'model-rows.stdout').read_text().splitlines()]
    for row in model:
        assert type(row) is list and len(row) == 4 and type(row[0]) is str
        assert row[1] is False and row[3] is False and type(row[2]) is list and len(row[2]) == 7
        assert all(type(run) is list and all(type(byte) is int and 0 <= byte < 128 for byte in run) for run in row[2][:5])
        assert type(row[2][5]) is bool and type(row[2][6]) is bool
    compared = comparator.compare(cases, plain, instrumented, plain_trace, trace, model)
    assert compared == load(EXEC / 'COMPARISON.json') == result['comparison']
    command = [sys.executable, '-I', str(PROTOCOL / 'compare.py'), '--cases', str(PROTOCOL / 'prepared/CASES.json'), '--plain', str(EXEC / 'native-plain.stdout'), '--instrumented', str(EXEC / 'native-instrumented.stdout'), '--plain-trace', str(EXEC / 'native-plain.stderr'), '--trace', str(EXEC / 'native-instrumented.stderr'), '--model', str(EXEC / 'model-rows.stdout'), '--out', str(HERE / 'COMPARISON.json')]
    replay = subprocess.run(command, capture_output=True, text=True)
    (HERE / 'compare.stdout').write_text(replay.stdout)
    (HERE / 'compare.stderr').write_text(replay.stderr)
    assert replay.returncode == 0 and load(HERE / 'COMPARISON.json') == compared
    probes = []
    def probe(name, mutate):
        values = copy.deepcopy([cases, plain, instrumented, plain_trace, trace, model])
        mutate(values)
        try:
            comparator.compare(*values)
        except (ValueError, KeyError, IndexError, TypeError):
            rejected = True
        else:
            rejected = False
        probes.append({'name': name, 'rejected': rejected})
    key = next(key for key, value in trace.items() if value and key[1] == 'cold')
    probe('lost native sign trace', lambda v: v[4][key][0].update(has_sign=not v[4][key][0]['has_sign']))
    probe('wrong native type trace', lambda v: v[4][key][0].update(is_integer=not v[4][key][0]['is_integer']))
    probe('missing model row', lambda v: v[5].pop())
    probe('extra cached trace', lambda v: v[4][next(k for k in v[4] if k[1] == 'cached')].append(copy.deepcopy(v[4][key][0])))
    probe('missing cold trace', lambda v: v[4][key].clear())
    probe('changed reset end', lambda v: v[1][next(k for k in v[1] if k[1] == 'reparsed')].update(end=999999))
    probe('changed initial model error', lambda v: v[5][0].__setitem__(1, True))
    probe('changed final model error', lambda v: v[5][0].__setitem__(3, True))
    def float_change(v):
        for public in [v[1], v[2]]:
            for row in public.values():
                row['float_bits'] = 'deadbeef'
    probe('all corresponding float bits', float_change)
    probe('model Boolean replaced by integer', lambda v: v[5][0][2].__setitem__(5, int(v[5][0][2][5])))
    assert all(row['rejected'] for row in probes[:8])
    assert all(not row['rejected'] for row in probes[8:])
    evidence = {str(f.relative_to(EXEC)): sha(f) for f in sorted(EXEC.iterdir()) if f.is_file()}
    (HERE / 'EVIDENCE-HASHES.json').write_text(json.dumps(evidence, indent=2) + '\n')
    (HERE / 'INPUTS.json').write_text(json.dumps(inputs, indent=2) + '\n')
    (HERE / 'SOURCES.json').write_text(json.dumps(files, indent=2) + '\n')
    (HERE / 'BUILD-ARTIFACTS.json').write_text(json.dumps(artifacts, indent=2) + '\n')
    report = {'status': 'PASS', 'materialized_git_objects': 64, 'compiler_commands': 12,
              'top_level_commands': 50, 'model_modules': 44, 'comparison': compared,
              'actual_model_rows_strictly_typed': True,
              'mode_counts': dict(Counter(row['mode'] for row in cases)),
              'admitted_mode_counts': dict(Counter(row['mode'] for row in admitted)),
              'nonzero_utf8_cases': sum(bool(row['prefix']) for row in cases),
              'phase_counts': dict(Counter(phase for _, phase in plain)),
              'trace_counts_by_phase': {phase: sum(len(rows) for (_, p), rows in trace.items() if p == phase) for phase in comparator.PHASES},
              'native_kinds_cold': dict(Counter(row['kind'] for (_, phase), row in plain.items() if phase == 'cold')),
              'post_execution_record_controls': probes,
              'reviewer_compilation_or_native_execution': False,
              'original_evidence_mutated': False,
              'production_feature_equivalence': False, 'native_refinement_proved': False}
    (HERE / 'AUDIT.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
