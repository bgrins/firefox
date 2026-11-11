import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = ROOT / 'artifacts/css-document-schema-design-20261110-v1'
LEAN = ROOT / 'artifacts/stylo-bloom-tools/lean-4.35.0-rc4-darwin_aarch64/bin/lean'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    inputs = json.loads((SOURCE / 'SOURCE-ONLY.json').read_text())
    for path, expected in inputs.items():
        assert sha(SOURCE / path) == expected
    preserved = json.loads((SOURCE / 'PRESERVED.json').read_text())['sha256']
    for path, expected in preserved.items():
        assert sha(ROOT / 'artifacts/css-first-order-library-integration-20261110-v1/overlay' / path) == expected
    commands = {}
    with tempfile.TemporaryDirectory(prefix='source-only-', dir=HERE) as directory:
        work = Path(directory)
        for path in inputs:
            destination = work / path
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes((SOURCE / path).read_bytes())
        (work / 'SOURCE-ONLY.json').write_bytes((SOURCE / 'SOURCE-ONLY.json').read_bytes())
        (work / 'Boundary.lean').write_bytes((HERE / 'Boundary.lean').read_bytes())
        def run(label, argv):
            result = subprocess.run([str(x) for x in argv], cwd=work,
                env=dict(os.environ, LEAN_PATH=str(work), PYTHONDONTWRITEBYTECODE='1'),
                capture_output=True, text=True)
            output = result.stdout + result.stderr
            (HERE / (label + '.log')).write_text(output)
            commands[label] = {'exit': result.returncode, 'sha256': hashlib.sha256(output.encode()).hexdigest()}
            assert result.returncode == 0, (label, output)
            assert not re.search(r'(?m)^(?:[^\n]*:\d+:\d+: )?(?:warning:|error:|error\()', output), (label, output)
            return output
        run('source-replay', [sys.executable, '-B', 'check.py', '--lean', LEAN, '--out', HERE / 'author-replay'])
        for path in list(preserved) + ['Model.lean', 'Prototype.lean', 'Boundary.lean']:
            run('build-' + path.replace('/', '-'), [LEAN, '-o', path[:-5] + '.olean', path])
        (work / 'Audit.lean').write_text('import Boundary\n' + ''.join('#print axioms CssDerivation.DocumentReview.' + name + '\n'
            for name in ['accepted_body_evaluates_without_tail_capture', 'different_tail_shapes_and_values_do_not_matter']))
        output = run('independent-audits', [LEAN, 'Audit.lean'])
        audits = {}
        for line in re.sub(r',\n\s*', ', ', output).splitlines():
            match = re.fullmatch(r"'([^']+)' (does not depend on any axioms|depends on axioms: \[(.*)\])", line)
            assert match, line
            axioms = set(match[3].split(', ')) if match[3] else set()
            assert axioms <= {'propext', 'Classical.choice', 'Quot.sound'} and match[1] not in audits
            audits[match[1]] = sorted(axioms)
        assert len(audits) == 2
    for path, expected in inputs.items():
        assert sha(SOURCE / path) == expected
    original = json.loads((HERE / 'author-replay/report.json').read_text())
    assert original['status'] == 'pass' and len(original['audits']) == 24
    report = {'status': 'pass', 'source_manifest_sha256': sha(SOURCE / 'SOURCE-ONLY.json'),
              'input_sha256': inputs, 'lean_sha256': sha(LEAN), 'commands': commands,
              'author_replay_audits': len(original['audits']), 'independent_audits': audits,
              'temporary_builds_removed': True, 'no_native_or_canonical_changes': True}
    (HERE / 'CHECK.json').write_text(json.dumps(report, indent=2) + '\n')
    print('PASS: 24 source-only audits, four cases, semantic mutant, two independent generic boundary proofs')


if __name__ == '__main__':
    main()
