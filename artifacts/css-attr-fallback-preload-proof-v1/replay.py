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
PRODUCER_SHA = '80ec502c400e5810708f53ca5cc8021697457c7590e4cf38844bc4095a0f8ade'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def verify():
    for name in ('INPUTS.json', 'FREEZE.json'):
        file = HERE / name
        if file.exists():
            entries = json.loads(file.read_text())
            if name == 'FREEZE.json':
                entries = entries['files']
            for path, expected in entries.items():
                if sha(HERE / path) != expected:
                    raise SystemExit('Integrity failure: ' + path)
    assert sha(HERE / 'native/MANIFEST.json') == PRODUCER_SHA
    producer = json.loads((HERE / 'native/MANIFEST.json').read_text())['files']
    for path in (HERE / 'native').rglob('*'):
        if path.is_file() and path.name != 'MANIFEST.json':
            assert sha(path) == producer[str(path.relative_to(HERE / 'native'))]
    pins = json.loads((HERE / 'native/PINS.json').read_text())
    for file, phase in [('baseline-v3-receipt.json', 'original'), ('candidate-v3-receipt.json', 'candidate')]:
        receipt = json.loads((HERE / 'runtime' / file).read_text())
        assert receipt['all_inputs_unchanged'] and receipt['suite_end_count'] == 1
        for name, native in [('cascade.rs', 'properties/cascade.rs'), ('custom_properties.rs', 'custom_properties.rs')]:
            assert receipt['pins_before']['servo/components/style/' + native] == pins[phase][name]
    with tempfile.TemporaryDirectory(prefix='preload-source-') as temporary:
        work = Path(temporary)
        native = work / 'servo/components/style/properties/cascade.rs'
        native.parent.mkdir(parents=True)
        shutil.copyfile(HERE / 'native/original/cascade.rs', native)
        for reverse in (False, True):
            command = ['patch', '--batch', '--fuzz=0', '-p1', '-i', str(HERE / 'native/recursive-preload.patch')]
            if reverse:
                command.append('-R')
            process = subprocess.run(command, cwd=work, text=True, capture_output=True)
            assert process.returncode == 0, process.stdout + process.stderr
            phase = 'original' if reverse else 'candidate'
            assert native.read_bytes() == (HERE / 'native' / phase / 'cascade.rs').read_bytes()
    cascade = (HERE / 'native/candidate/cascade.rs').read_text()
    start = cascade.index('    pub fn update_attributes_map(')
    stop = cascade.index('    /// Computes the map of applicable custom properties', start)
    body = cascade[start:stop]
    assert body.index('refs_stack.push(&fallback.references)') < body.index('if !next.is_attr_with_type()')
    assert '.entry(namespace)' in body and '.insert(&next.name)' in body
    assert '&value.url_data' in body and 'visit_link(' not in body
    custom = (HERE / 'native/candidate/custom_properties.rs').read_text()
    assert 'references.flags |= fb.references.flags;' in custom
    return len(json.loads((HERE / 'MODULES.json').read_text())['audits'])

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--lean', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    audits = verify()
    if not args.lean:
        print(json.dumps({'integrity_source_reconstruction': 'PASS', 'theorem_audits': audits}))
        return
    lean = args.lean.resolve()
    assert sha(lean) == LEAN_SHA
    assert args.output and not args.output.exists()
    output = args.output.resolve()
    output.mkdir(parents=True)
    modules = json.loads((HERE / 'MODULES.json').read_text())
    rows = []
    mutations = []
    with tempfile.TemporaryDirectory(prefix='preload-lean-') as temporary:
        work = Path(temporary)
        env = dict(os.environ, LEAN_PATH=str(work))
        for file in HERE.glob('*.lean'):
            source = file.read_text()
            assert not re.search(r'\b(sorry|admit|axiom|native_decide)\b', source, re.M)
            shutil.copyfile(file, work / file.name)
        for name in modules['order']:
            result = subprocess.run([str(lean), '-o', name + '.olean', name + '.lean'],
                cwd=work, env=env, text=True, capture_output=True)
            log = result.stdout + result.stderr
            (output / (name + '.log')).write_text(log)
            assert result.returncode == 0 and 'sorryAx' not in log, log
            rows.append({'module': name, 'exit': result.returncode})
        audit = (output / 'Audit.log').read_text()
        assert all("'" + name + "'" in audit for name in modules['audits'])
        assert audits == 54 and len(modules['new_audits']) == 38
        for group in re.findall(r'depends on axioms: \[([^]]*)\]', audit):
            assert not ({x.strip() for x in group.split(',')} - {'propext', 'Classical.choice', 'Quot.sound'})
        queue = 'match ref.fallback with | none => stack | some refs => refs :: stack'
        specs = [
            ('fifo-instead-of-lifo', 'FallbackSchedule', queue,
                'match ref.fallback with | none => stack | some refs => stack ++ [refs]'),
            ('skip-var-fallback', 'FallbackSchedule', queue,
                'if ref.info.kind = .var then stack else ' + queue),
            ('namespace-alias', 'PreparationExecution',
                '| .typedAttr => resolveKey info.name info.ns',
                '| .typedAttr => resolveKey info.name (info.ns.map (fun _ => 0))'),
            ('drop-seen-dedup', 'PreparationExecution',
                'if key ∈ state.cache.seen then state else',
                'if False then state else'),
        ]
        for name, module, old, new in specs:
            file = work / (module + '.lean')
            original = file.read_text()
            assert original.count(old) == 1
            file.write_text(original.replace(old, new))
            result = subprocess.run([str(lean), '-o', name + '.olean', file.name],
                cwd=work, env=env, text=True, capture_output=True)
            log = result.stdout + result.stderr
            (output / (name + '.log')).write_text(log)
            file.write_text(original)
            assert result.returncode != 0
            assert 'unsolved goals' in log or 'Type mismatch' in log or 'type mismatch' in log, log
            mutations.append({'mutation': name, 'rejected': True, 'exit': result.returncode})
    result = {'status': 'FINITE_WORKLIST_AND_PREPARATION_PASS_FULL_COMPOSITION_OPEN',
        'lean_sha256': LEAN_SHA, 'modules': rows, 'new_audits': len(modules['new_audits']),
        'total_audits': audits, 'mutations': mutations}
    (output / 'RESULT.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result))

if __name__ == '__main__':
    main()
