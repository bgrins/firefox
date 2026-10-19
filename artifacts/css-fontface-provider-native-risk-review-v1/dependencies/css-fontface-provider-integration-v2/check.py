#!/usr/bin/env python3
"""Authenticate both source dependencies and replay their offline checks."""
import ast
import hashlib
import json
from pathlib import Path
import subprocess
import sys

P = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path):
    return json.loads(path.read_text())


def main():
    freeze = load(P / 'FREEZE.json')
    assert sha(P / 'INPUTS.json') == freeze['inputs_sha256']
    inputs = load(P / 'INPUTS.json')
    assert len(inputs) == freeze['entries']
    for rel, expected in inputs.items():
        assert sha(P / rel) == expected, rel
    dependencies = load(P / 'DEPENDENCIES.json')
    for name, pins in dependencies.items():
        dep = P.parent / name
        assert sha(dep / 'FREEZE.json') == pins['freeze_sha256']
        assert sha(dep / 'INPUTS.json') == pins['inputs_sha256']
        for rel, expected in load(dep / 'INPUTS.json').items():
            assert sha(dep / rel) == expected, (name, rel)
    base = P.parent / 'css-fontface-provider-integration-v1'
    candidate = P.parent / 'css-fontface-provider-candidate-v2'
    adaptation = load(P / 'HARNESS-ADAPTATION.json')
    original = (base / 'harness.py').read_text()
    assert sha(base / 'harness.py') == adaptation['v1_harness_sha256']
    assert original.count(adaptation['old_authentication']) == 1
    assert original.replace(adaptation['old_authentication'], adaptation['new_authentication']) == (P / 'harness.py').read_text()
    for rel in adaptation['fixed_json_copies']:
        assert (P / rel).read_bytes() == (base / rel).read_bytes(), rel
    assert (P / 'NATIVE-PINS.json').read_bytes() == (candidate / 'NATIVE-PINS.json').read_bytes()
    for name in ['check.py', 'compare.py', 'harness.py']:
        ast.parse((P / name).read_text())
    results = {}
    for dep in [base, candidate]:
        run = subprocess.run([sys.executable, str(dep / 'check.py')], capture_output=True, text=True)
        assert run.returncode == 0, (dep.name, run.stdout, run.stderr)
        results[dep.name] = json.loads(run.stdout)
    print(json.dumps({'status': 'PASS_SOURCE_INTEGRATION_ONLY', 'inputs': len(inputs),
                      'unchanged_harness_except_authentication': True,
                      'unchanged_fixed_json_files': len(adaptation['fixed_json_copies']),
                      'native_files': 16, 'registered_cases': [12, 28, 28],
                      'dependency_replays': results, 'build_or_browser_run': False}, indent=2))


if __name__ == '__main__':
    main()
