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
    for name in ('INPUTS.json', 'FREEZE.json'):
        file = HERE / name
        if file.exists():
            entries = json.loads(file.read_text())
            if name == 'FREEZE.json':
                entries = entries['files']
            for path, expected in entries.items():
                if sha(HERE / path) != expected:
                    raise SystemExit('Integrity failure: ' + path)
    binding = json.loads((HERE / 'SOURCE-PINS.json').read_text())
    for path, expected in binding['pins'].items():
        assert sha(HERE / path) == expected
    assert sha(HERE / binding['indexed_parser']) == binding['indexed_parser_sha256']
    receipt = json.loads((HERE / 'evidence/baseline-v2-receipt.json').read_text())
    assert receipt['all_inputs_unchanged'] and receipt['suite_end_count'] == 1
    for local, native in [('custom_properties.rs', 'custom_properties.rs'),
                          ('properties__cascade.rs', 'properties/cascade.rs')]:
        assert sha(HERE / 'source' / local) == receipt['pins_before']['servo/components/style/' + native]
    assert receipt['counts']['/css/css-values/attr-fallback-readiness.html'] == {'FAIL': 3, 'PASS': 3, 'OK': 1}
    correspondence = json.loads((HERE / 'PARSER-CORRESPONDENCE.json').read_text())
    for row in correspondence:
        assert sha(HERE / row['local_snapshot']) == row['local_sha256']
        assert sha(HERE / row['indexed_snapshot']) == row['indexed_sha256']
        assert ((HERE / row['local_snapshot']).read_bytes() ==
                (HERE / row['indexed_snapshot']).read_bytes()) == row['byte_identical']
    actual_parser = (HERE / 'source/properties_and_values__value.rs').read_text()
    assert 'Some(id) => context.with_property_declaration(id, parse_components)' in actual_parser
    actual_caller = (HERE / 'source/properties__mod.rs').read_text()
    assert 'let longhand_id = self.id;' in actual_caller
    assert 'match unparsed.from_shorthand' in actual_caller
    assert 'None => NonCustomPropertyId::from(longhand_id)' in actual_caller
    cascade = (HERE / 'source/properties__cascade.rs').read_text()
    assert 'primary_valid = !v.has_references();' in cascade
    assert 'LonghandId::LineHeight => ReferenceFlags::LH_UNITS | ReferenceFlags::FONT_UNITS' in cascade
    assert '.push(v.value.clone());' in cascade
    assert 'NonCustomReferenceMap<Vec<Arc<UnparsedValue>>>' in cascade


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--lean', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    verify()
    if not args.lean:
        print(json.dumps({'integrity_source_binding': 'PASS'}))
        return
    lean = args.lean.resolve()
    assert sha(lean) == LEAN_SHA
    assert args.output and not args.output.exists()
    output = args.output.resolve()
    output.mkdir(parents=True)
    rows = []
    with tempfile.TemporaryDirectory(prefix='typed-fallback-lean-') as temporary:
        work = Path(temporary)
        env = dict(os.environ, LEAN_PATH=str(work))
        for name in ('AttributeEligibility', 'Audit'):
            source = (HERE / (name + '.lean')).read_text()
            assert not re.search(r'\b(sorry|admit|axiom|native_decide)\b', source)
            (work / (name + '.lean')).write_text(source)
            process = subprocess.run([str(lean), '-o', name + '.olean', name + '.lean'],
                cwd=work, env=env, text=True, capture_output=True)
            log = process.stdout + process.stderr
            (output / (name + '.log')).write_text(log)
            assert process.returncode == 0 and 'sorryAx' not in log, log
            rows.append({'module': name, 'exit': process.returncode})
        audit = (output / 'Audit.log').read_text()
        names = re.findall(r'^#print axioms (.*)$', (HERE / 'Audit.lean').read_text(), re.M)
        assert len(names) == 15
        assert all("'" + name + "'" in audit for name in names)
        for group in re.findall(r'depends on axioms: \[([^]]*)\]', audit):
            assert not ({x.strip() for x in group.split(',')} - {'propext', 'Classical.choice', 'Quot.sound'})
        mutations = []
        file = work / 'AttributeEligibility.lean'
        original = file.read_text()
        for name, old, new in [
            ('readiness-only', '| .ready value => (parse context descriptor value).isSome', '| .ready _ => true'),
            ('unconditional-fallback', 'if eligible parse context descriptor slot then [] else fallback', 'fallback')]:
            assert original.count(old) == 1
            file.write_text(original.replace(old, new))
            process = subprocess.run([str(lean), '-o', name + '.olean', file.name],
                cwd=work, env=env, text=True, capture_output=True)
            (output / (name + '.log')).write_text(process.stdout + process.stderr)
            assert process.returncode != 0
            mutations.append({'mutation': name, 'rejected': True, 'exit': process.returncode})
        file.write_text(original)
    result = {'status': 'LOCAL_ELIGIBILITY_COMPONENT_PASS_NATIVE_COMPOSITION_OPEN',
        'lean_sha256': LEAN_SHA, 'modules': rows, 'theorem_audits': len(names), 'mutations': mutations}
    (output / 'RESULT.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result))

if __name__ == '__main__':
    main()
