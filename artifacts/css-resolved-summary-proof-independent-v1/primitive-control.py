#!/usr/bin/env python3
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--lean', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    src = ROOT / 'input'
    assert hashlib.sha256((src / 'FREEZE.json').read_bytes()).hexdigest() == '340271a5c840830aa434aab392aa790dbb95d57411bad4c9df9b836e333a8bd2'
    frozen = json.loads((src / 'FREEZE.json').read_text())
    assert hashlib.sha256((src / 'INPUTS.json').read_bytes()).hexdigest() == frozen['inputs_sha256']
    for name, expected in json.loads((src / 'INPUTS.json').read_text()).items():
        assert hashlib.sha256((src / name).read_bytes()).hexdigest() == expected, name
    lean = args.lean.resolve()
    assert hashlib.sha256(lean.read_bytes()).hexdigest() == 'd1d9c26a539f54fe839d2aa7760bf1ac1dd76a30b26e2c9684bebf2900038fcf'
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    with tempfile.TemporaryDirectory(prefix='summary-primitive-control-') as tmp:
        work = Path(tmp)
        for name in ['TokenSummary', 'SelectedOutput', 'Audit']:
            shutil.copyfile(src / (name + '.lean'), work / (name + '.lean'))
        path = work / 'TokenSummary.lean'
        original = path.read_text()
        old = '| .line => fun dep => dep == .font || dep == .line'
        new = '| .line => fun dep => dep == .line'
        assert original.count(old) == 1
        altered = original.replace(old, new)
        path.write_text(altered)
        env = dict(os.environ, LEAN_PATH=str(work))
        stages = []
        for name in ['TokenSummary', 'SelectedOutput', 'Audit']:
            result = subprocess.run([str(lean), '-o', name + '.olean', name + '.lean'],
                                    cwd=work, env=env, text=True, capture_output=True)
            (output / (name + '.log')).write_text(result.stdout + result.stderr)
            assert result.returncode == 0, (name, result.stdout, result.stderr)
            stages.append({'module': name, 'exit': result.returncode})
    result = {'status': 'EXPECTED PASS: demonstrates shared unit primitive is not independently constrained',
              'stages': stages, 'old': old, 'new': new,
              'altered_sha256': hashlib.sha256(altered.encode()).hexdigest(),
              'meaning': 'The source-inconsistent line-unit mapping preserves all composition laws; native unit classification remains an admission obligation.'}
    (output / 'RESULT.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
