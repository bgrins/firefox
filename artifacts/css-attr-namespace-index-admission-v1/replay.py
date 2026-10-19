#!/usr/bin/env python3
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
LEAN_SHA = 'd1d9c26a539f54fe839d2aa7760bf1ac1dd76a30b26e2c9684bebf2900038fcf'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def verify():
    pins = json.loads((HERE / 'INPUTS.json').read_text())
    for name, expected in pins.items():
        path = HERE / name
        if not path.is_file() or sha(path) != expected:
            raise SystemExit('Integrity failure: ' + name)
    freeze = HERE / 'FREEZE.json'
    if freeze.exists():
        for name, expected in json.loads(freeze.read_text())['files'].items():
            if sha(HERE / name) != expected:
                raise SystemExit('Freeze integrity failure: ' + name)
    return len(pins)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--lean', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    count = verify()
    if not args.lean:
        print(json.dumps({'integrity': 'PASS', 'entries': count}))
        return
    lean = args.lean.resolve()
    if sha(lean) != LEAN_SHA:
        raise SystemExit('Unexpected Lean executable')
    if args.output is None or args.output.exists():
        raise SystemExit('--output must name a new directory')
    output = args.output.resolve()
    output.mkdir(parents=True)
    modules = json.loads((HERE / 'MODULES.json').read_text())
    rows = []
    mutations = []
    with tempfile.TemporaryDirectory(prefix='closed-lean-') as temporary:
        build = Path(temporary)
        for path in HERE.glob('*.lean'):
            text = path.read_text()
            if re.search(r'\b(sorry|admit|axiom|native_decide)\b', text):
                raise SystemExit('Forbidden proof shortcut in ' + path.name)
            shutil.copyfile(path, build / path.name)
        env = dict(os.environ, LEAN_PATH=str(build))
        for name in modules['order']:
            process = subprocess.run([str(lean), '-o', name + '.olean', name + '.lean'],
                                     cwd=build, env=env, text=True, capture_output=True)
            log = process.stdout + process.stderr
            (output / (name + '.log')).write_text(log)
            rows.append({'module': name, 'exit': process.returncode,
                         'log_sha256': sha(output / (name + '.log'))})
            if process.returncode or 'sorryAx' in log:
                (output / 'RESULT.json').write_text(json.dumps(rows, indent=2) + '\n')
                raise SystemExit('Proof failure: ' + name)
        audit = (output / 'Audit.log').read_text()
        for name in modules['new_theorem_audits']:
            if "'" + name + "'" not in audit:
                raise SystemExit('Missing audit: ' + name)
        for group in re.findall(r'depends on axioms: \[([^]]*)\]', audit):
            if {name.strip() for name in group.split(',')} - {'propext', 'Classical.choice', 'Quot.sound'}:
                raise SystemExit('Unexpected axiom set: ' + group)
        mutation_specs = [
            ('reuse-zero-index', 'IndexAllocation', 'insert state.maps node state.count', 'insert state.maps node 0'),
            ('reload-explicit-tombstone', 'ReloadState', 'if slot.isNone then', 'if (getAttr slot).isNone then'),
        ]
        for label, module, old, new in mutation_specs:
            file = build / (module + '.lean')
            original = file.read_text()
            if old not in original:
                raise SystemExit('Missing mutation anchor: ' + label)
            file.write_text(original.replace(old, new, 1))
            process = subprocess.run([str(lean), '-o', label + '.olean', file.name],
                                     cwd=build, env=env, text=True, capture_output=True)
            logpath = output / (label + '.log')
            logpath.write_text(process.stdout + process.stderr)
            file.write_text(original)
            if process.returncode == 0:
                raise SystemExit('Mutation incorrectly accepted: ' + label)
            mutations.append({'mutation': label, 'exit': process.returncode,
                              'log_sha256': sha(logpath), 'rejected': True})
    result = {'status': 'INDEX_AND_RELOAD_COMPONENTS_PASS_FULL_GRAPH_OPEN', 'integrity_entries': count,
              'lean_sha256': LEAN_SHA, 'source_only_fresh_build': True,
              'new_theorem_audits': len(modules['new_theorem_audits']), 'modules': rows, 'mutations': mutations}
    (output / 'RESULT.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'status': result['status'], 'modules': len(rows),
                      'new_theorem_audits': result['new_theorem_audits']}))

if __name__ == '__main__':
    main()
