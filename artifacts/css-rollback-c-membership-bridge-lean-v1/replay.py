#!/usr/bin/env python3
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
BASE = ROOT / 'artifacts/css-shadow-context-order-proof-v1/cutoff-native-review-v1/proof'
LEAN = ROOT / 'artifacts/stylo-bloom-tools/lean-4.35.0-rc4-darwin_aarch64/bin/lean'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    ordered = []
    visited = set()

    def visit(name):
        if name == 'Std' or name in visited:
            return
        visited.add(name)
        path = (ROOT / 'artifacts/css-rollback-native-consumer-bridge-lean-v1/ConsumerBridge.lean'
                if name == 'ConsumerBridge' else BASE / (name + '.lean'))
        for dep in re.findall(r'^import (\w+)', path.read_text(), re.M):
            visit(dep)
        ordered.append(path)

    for dep in re.findall(r'^import (\w+)', (HERE / 'ColdMembership.lean').read_text(), re.M):
        visit(dep)
    records = [{'path': str(p.relative_to(ROOT)), 'sha256': digest(p)} for p in ordered]
    pins = HERE / 'IMPORTS.json'
    if pins.exists():
        assert json.loads(pins.read_text()) == records, 'Dependency pins changed'
    else:
        pins.write_text(json.dumps(records, indent=2) + '\n')
    commands = []
    exit_code = 0
    with tempfile.TemporaryDirectory(prefix='css-rollback-c-membership-', dir='/private/tmp') as scratch:
        env = dict(os.environ, LEAN_PATH=scratch)
        with (HERE / 'lean.log').open('w') as log:
            for path in [*ordered, HERE / 'ColdMembership.lean']:
                shutil.copy2(path, Path(scratch) / path.name)
                command = [str(LEAN), '-o', path.stem + '.olean', path.name]
                log.write('$ ' + ' '.join(command) + '\n')
                log.flush()
                result = subprocess.run(command, cwd=scratch, env=env, stdout=log, stderr=subprocess.STDOUT)
                commands.append({'module': path.stem, 'exit_code': result.returncode})
                if result.returncode:
                    exit_code = result.returncode
                    break
    result = {'compiler': str(LEAN.relative_to(ROOT)), 'compiler_sha256': digest(LEAN),
              'source_sha256': digest(HERE / 'ColdMembership.lean'),
              'commands': commands, 'exit_code': exit_code, 'scratch_removed': True}
    (HERE / 'RESULT.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))
    raise SystemExit(exit_code)


if __name__ == '__main__':
    main()
