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
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()


def decisive(code, log):
    return code == 1 and re.fullmatch(
        r"False\.lean:\d+:\d+: error: Tactic `decide` proved that the proposition\n[\s\S]+\nis false\n?", log
    ) is not None and log.count('error:') == 1 and not any(
        word in log for word in ('warning:', 'failed to reduce', 'Reduction got stuck', 'sorry', 'failed to synthesize'))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    output = parser.parse_args().output
    assert output.is_absolute() and not output.exists()
    inputs = json.loads((HERE / 'INPUTS.json').read_text())
    compiler = ROOT / inputs['compiler']
    assert sha(compiler) == inputs['compiler_sha256']
    for name, digest in inputs['sources'].items():
        assert sha(HERE / name) == digest
        assert not re.search(r'\b(sorry|axiom|native_decide)\b', (HERE / name).read_text())
    for name, digest in inputs['imports'].items():
        assert sha(ROOT / name) == digest
    for name, digest in json.loads((HERE / 'REFERENCES.json').read_text()).items():
        assert sha(ROOT / name) == digest
    output.mkdir()
    records = []
    with tempfile.TemporaryDirectory(prefix='registered-number-admission-', dir='/private/tmp') as temporary:
        scratch = Path(temporary)
        for name in inputs['sources']:
            shutil.copyfile(HERE / name, scratch / name)
        env = dict(os.environ, LEAN_PATH=temporary, LEAN_NUM_THREADS='1')

        def run(name, args, negative=False):
            result = subprocess.run([str(compiler), '-j1', *args], cwd=scratch, env=env,
                                    capture_output=True, text=True, timeout=45)
            log = result.stdout + result.stderr
            (output / (name + '.log')).write_text(log)
            records.append(dict(name=name, command=[str(compiler), '-j1', *args],
                                exit=result.returncode, log_sha256=sha(output / (name + '.log'))))
            assert decisive(result.returncode, log) if negative else (
                result.returncode == 0 and 'warning:' not in log and 'sorryAx' not in log), log
            return log

        version = run('version', ['--version']).strip()
        for name in ('Admission', 'Examples'):
            run(name, ['-o', name + '.olean', name + '.lean'])
        audit = run('audit', ['Audit.lean'])
        axioms = {}
        for line in audit.splitlines():
            match = re.fullmatch(r"'([^']+)' (?:depends on axioms: \[([^]]*)\]|does not depend on any axioms)", line)
            assert match, line
            assert match[1] not in axioms
            axioms[match[1]] = match[2].split(', ') if match[2] else []
            assert set(axioms[match[1]]) <= {'propext', 'Quot.sound', 'Classical.choice'}
        assert set(axioms) == set(inputs['audited_names'])
        claims = {
            'initial-seed-false-edge': 'seedMutation env invalidLength = scheduledFont (plan env invalidLength)',
            'visitor-root-false-edge': 'visitorMutation env unused = scheduledFont (plan env unused)',
            'type-mask-erases-valid-math': 'typeMaskMutation env (.value ratio) = scheduledFont (plan env (.value ratio))',
            'selected-token-before-admission': 'selectedTokenMutation env invalidLength = scheduledFont (plan env invalidLength)',
            'wrong-type-primary-retries-fallback': 'plan env (.reference 2 (.value (.number 7))) = .ready (.number 7) false',
            'pending-treated-as-invalid': 'plan env (.reference 1 (.value (.number 7))) = .ready (.number 7) false',
            'scheduling-determines-cycle-policy': '(withCyclePolicy (fun _ => .invalidate) (.ready ratio true)).2 = (withCyclePolicy (fun _ => .retain) (.ready ratio true)).2',
        }
        for name, claim in claims.items():
            source = 'import Examples\nopen RegisteredNumber RegisteredNumber.Examples\nexample : ' + claim + ' := by\n  decide +kernel\n'
            (scratch / 'False.lean').write_text(source)
            (output / (name + '.lean')).write_text(source)
            run(name, ['False.lean'], True)
        good = (output / 'initial-seed-false-edge.log').read_text()
        assert not decisive(0, good)
        assert not decisive(1, good + 'False.lean:1:1: error: unrelated\n')
        assert not decisive(1, 'False.lean:1:1: error: Tactic `decide` failed to reduce\n')
        assert not decisive(1, 'False.lean:1:1: error: Unknown identifier `false`\n')
        assert not decisive(1, good.replace('is false', 'failed to synthesize'))
    assert not scratch.exists()
    check = dict(status='REGISTERED_NUMBER_ADMISSION_MODEL_PASS', compiler=version, threads=1,
                 audited_declarations=len(axioms), closed_examples=inputs['closed_examples'],
                 decisive_false_controls=len(claims), diagnostic_gate_negatives=5,
                 axioms=axioms, records=records, owned_scratch_removed=True,
                 native_refinement=False, canonical_integration=False,
                 normative_coverage_credit=0, accepted_bug_credit=0,
                 scope='Normalized selected substitution, number grammar admission and semantic scheduling; no invalidating cycle policy')
    (output / 'CHECK.json').write_text(json.dumps(check, indent=2) + '\n')
    print(json.dumps(check))


if __name__ == '__main__':
    main()
