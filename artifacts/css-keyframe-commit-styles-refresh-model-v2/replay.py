import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def decisive_false(code, log, expected=None):
    match = re.fullmatch(
        r"False\.lean:\d+:\d+: error: Tactic `decide` proved that the proposition\n"
        r"  (110 = 210|210 = 999)\nis false\n", log)
    return code == 1 and match is not None and (expected is None or match[1] == expected)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    output = parser.parse_args().output
    assert output.is_absolute() and not output.exists() and not output.is_symlink()
    inputs = json.loads((HERE / 'INPUTS.json').read_text())
    compiler = ROOT / inputs['compiler']
    assert sha(compiler) == inputs['compiler_sha256']
    for name, digest in json.loads((HERE / 'REFERENCES.json').read_text()).items():
        assert sha(ROOT / name) == digest
    for name, digest in inputs['models'].items():
        assert sha(HERE / name) == digest
        assert not re.search(r'\b(sorry|axiom|native_decide)\b', (HERE / name).read_text())
    for name in ('Context.lean', 'Sampling.lean', 'Graph.lean', 'Schedule.lean'):
        assert (HERE / name).read_bytes() == (ROOT / 'artifacts/css-keyframe-finite-dag-schedule-model-v1' / name).read_bytes()
    previous = ROOT / 'artifacts/css-keyframe-commit-styles-refresh-model-v1'
    for name in inputs['models']:
        assert (HERE / name).read_bytes() == (previous / name).read_bytes()
    historical_logs = [(previous / 'replay-4' / (name + '.log')).read_text()
        for name in ('top-only-current', 'stale-context-current', 'higher-consumer-in-stack')]
    assert all(not decisive_false(1, log) for log in historical_logs)
    output.mkdir()
    records = []
    gate_records = []
    negatives = {
        'top-only-current': 'compose stack (refresh resolve 200 [.top] old) 0 = compose stack (resolve 200) 0',
        'stale-context-current': 'compose stack (refresh resolve 100 stack old) 0 = compose stack (resolve 200) 0',
        'higher-consumer-in-stack': 'compose stack (refresh resolve 200 [.lower, .top, .higher] old) 0 = 999',
    }
    with tempfile.TemporaryDirectory(prefix='commit-refresh-lean-', dir='/private/tmp') as temporary:
        scratch = Path(temporary)
        env = dict(os.environ, LEAN_PATH=temporary, LEAN_NUM_THREADS='1')
        for name in inputs['models']:
            shutil.copyfile(HERE / name, scratch / name)

        def run(name, args, success=True):
            result = subprocess.run([str(compiler), '-j1', *args], cwd=scratch, env=env,
                                    capture_output=True, text=True, timeout=60)
            log = result.stdout + result.stderr
            (output / (name + '.log')).write_text(log)
            records.append(dict(name=name, exit=result.returncode, log_sha256=sha(output / (name + '.log'))))
            if success:
                assert result.returncode == 0 and 'warning:' not in log and 'sorryAx' not in log, log
            else:
                assert decisive_false(result.returncode, log,
                    '210 = 999' if name == 'higher-consumer-in-stack' else '110 = 210'), log
            return log

        version = run('version', ['--version']).strip()
        for name in inputs['models']:
            if name != 'Audit.lean':
                run(name[:-5], ['-o', name[:-5] + '.olean', name])
        audit = run('Audit', ['Audit.lean'])
        axioms = {}
        for line in audit.splitlines():
            match = re.fullmatch(r"'([^']+)' (?:depends on axioms: \[([^]]*)\]|does not depend on any axioms)", line)
            assert match, line
            axioms[match[1]] = match[2].split(', ') if match[2] else []
            assert set(axioms[match[1]]) <= {'propext', 'Quot.sound', 'Classical.choice'}
        for name, claim in negatives.items():
            lhs, rhs = claim.split(' = ')
            left_value, right_value = {
                'top-only-current': (110, 210),
                'stale-context-current': (110, 210),
                'higher-consumer-in-stack': (210, 999)}[name]
            text = ('import Examples\nopen CommitRefresh\nexample : ' + claim + ' := by\n' +
                    f'  have left : {lhs} = {left_value} := by decide +kernel\n' +
                    f'  have right : ({rhs} : Rat) = {right_value} := by decide +kernel\n' +
                    '  rw [left, right]\n  decide +kernel\n')
            (scratch / 'False.lean').write_text(text)
            (output / (name + '.lean')).write_text(text)
            log = run(name, ['False.lean'], False)
            gate_records.append(dict(name=name, actual_decisive_log_accepted=True))
            assert not decisive_false(1, log, '0 = 1')
            for code, bad in [(0, log), (2, log), (1, log + 'extra diagnostic\n'),
                              (1, log.replace('is false', 'is true')),
                              (1, 'False.lean:1:1: error: Unknown identifier decide_false\n'),
                              (1, 'decide false'), (1, '')]:
                assert not decisive_false(code, bad), bad
        (scratch / 'Malformed.lean').write_text('import Examples\n#check missing_identifier_decide_false\n')
        malformed = subprocess.run([str(compiler), '-j1', 'Malformed.lean'], cwd=scratch,
            env=env, capture_output=True, text=True, timeout=60)
        malformed_log = malformed.stdout + malformed.stderr
        (output / 'malformed.log').write_text(malformed_log)
        assert malformed.returncode == 1 and 'Unknown identifier' in malformed_log
        assert not decisive_false(malformed.returncode, malformed_log)
        assert not decisive_false(0, audit)
        assert all(not decisive_false(1, log) for log in historical_logs)
    assert not scratch.exists()
    check = dict(status='COMMIT_STYLES_REFRESH_MODEL_PASS', compiler=version,
        threads=1, declaration_axioms=axioms, closed_examples=6, false_claims_rejected=3,
        historical_reduction_failures_rejected=3, gate_records=gate_records,
        malformed_compiler_log_rejected=True, gate_synthetic_negatives=24,
        positive_sources_byte_identical=True,
        records=records, owned_scratch_removed=True, native_refinement=False,
        current_provider_context_proved=False, canonical_integration=False)
    (output / 'CHECK.json').write_text(json.dumps(check, indent=2) + '\n')
    print(json.dumps(check))


if __name__ == '__main__':
    main()
