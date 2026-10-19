import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text())


def authenticate(root, pins=None):
    if pins:
        for name, digest in pins.items():
            assert sha(root / name) == digest, name
    manifest = read(root / 'MANIFEST.json')
    rows = manifest if isinstance(manifest, list) else [{'path': k, 'sha256': v} for k, v in manifest.items()]
    names = set()
    for row in rows:
        name = row['path']
        path = PurePosixPath(name)
        assert str(path) == name and not path.is_absolute() and '..' not in path.parts and name not in names
        names.add(name)
        target = root / name
        assert target.is_file() and all(not x.is_symlink() for x in [target, *target.parents])
        assert sha(target) == row['sha256'], name
    actual = {x.relative_to(root).as_posix() for x in root.rglob('*') if x.is_file()}
    assert actual == names | {'MANIFEST.json', 'FREEZE.json'}
    assert not any(x.is_symlink() for x in root.rglob('*'))
    return names


def observations(output):
    result = read(output / 'RESULT.json')
    variants = ['original', 'candidate', 'omit-rewind', 'reject-whole', 'ignore-structure', 'lose-positive-query']
    assert result['variants'] == variants
    valid = {'{var(--x)}', 'var(--x)', 'serif [var(--x)]', 'serif f({var(--x)})', 'serif', '', ' ', '/*comment*/', ' {var(--x)} '}
    all_rows = {}
    for variant in variants:
        rows = read(output / variant / 'ROWS.json')
        assert len(rows) == 57
        keyed = {(r['mode'], r['value']): r for r in rows}
        assert len(keyed) == 57
        assert {k[0] for k in keyed} == {'single', 'comma', 'consume-success'}
        assert all(row['curly_rule'] == (row['value'] in valid) for row in rows)
        all_rows[variant] = keyed
    original, candidate = all_rows['original'], all_rows['candidate']
    assert sum(r['gateway'] and not r['curly_rule'] for r in original.values()) == 18
    assert not any(r['gateway'] and not r['curly_rule'] for r in candidate.values())
    assert sum(original[k] != candidate[k] for k in original) == 18
    witnesses = [('omit-rewind', 'comma', 'serif {var(--x)}', False, True), ('reject-whole', 'comma', '{var(--x)}', True, False), ('ignore-structure', 'comma', 'serif {var(--x)}', False, True), ('lose-positive-query', 'consume-success', 'var(--x)', True, False)]
    for variant, mode, value, control, mutant in witnesses:
        assert candidate[(mode, value)]['gateway'] == control
        assert all_rows[variant][(mode, value)]['gateway'] == mutant
    commands = read(output / 'COMMANDS.json')
    assert commands and all(c['exit'] == 0 for c in commands)
    return {'theorems': 27, 'rows_per_variant': 57, 'variants': 6, 'native_mutants': 4, 'original_forbidden_gateways': 18, 'candidate_forbidden_gateways': 0}


def audits(source, output):
    expected = read(ROOT / 'THEOREMS-REVIEWED.json')
    text = (source / 'lean/DeclarationCurly.lean').read_text()
    assert ['DeclarationCurly.' + n for n in re.findall(r'^theorem\s+(\w+)', text, re.M)] == expected
    assert read(source / 'THEOREMS.json') == expected
    assert not re.search(r'\b(sorry|admit|axiom|native_decide)\b', text)
    audit = (output / 'AXIOMS.txt').read_text()
    assert audit.count('depends on axioms:') + audit.count('does not depend on any axioms') == len(expected) == 27
    for name in expected:
        assert audit.count("'" + name + "'") == 1
    for group in re.findall(r'depends on axioms:\s*\[([^\]]*)\]', audit):
        assert set(re.findall(r'[A-Za-z_][\w.]*', group)) <= {'propext', 'Quot.sound', 'Classical.choice'}


def main():
    assert sys.flags.isolated and sys.flags.no_site
    parser = argparse.ArgumentParser()
    parser.add_argument('--producer', type=Path, default=ROOT.parent / 'css-declaration-curly-proof-v1')
    parser.add_argument('--replay', type=Path)
    args = parser.parse_args()
    own = authenticate(ROOT)
    names = authenticate(args.producer, read(ROOT / 'PRODUCER-PINS.json'))
    original = (args.producer / 'evidence/audit/evidence/source/servo/components/style/properties/mod.rs').read_text()
    candidate = (args.producer / 'evidence/candidate-properties.rs').read_text()
    old_comment = '    // Look for var(), env() and top-level curly blocks after the error.\n'
    new_comment = '    input.reset(start);\n\n    // Look for var(), env() and top-level curly blocks in the whole value.\n'
    assert original.count(old_comment) == 1 and original.replace(old_comment, new_comment) == candidate
    assert sha(args.producer / 'evidence/candidate-properties.rs') == '6754d46e612a369fa6b3853151dc6179a60a92beb25a0a2dc1b8827b80669f92'
    helper = (args.producer / 'evidence/audit/evidence/helper.rs').read_text()
    start = original.index('fn parse_non_custom_property_declaration_value_into(')
    end = original.index('impl PropertyDeclaration', start)
    assert original[start:end].strip() == helper.strip()
    gates = read(ROOT / 'evidence/TAMPER.json')
    assert [x['mode'] for x in gates] == ['changed-lean', 'shadow-module', 'symlink', 'duplicate', 'escape']
    assert all(x['exit'] != 0 and not x['replay_started'] and 'AssertionError' in x['stderr'] for x in gates)
    audits(args.producer, ROOT / 'evidence/replay')
    result = observations(ROOT / 'evidence/replay')
    result.update(authenticated_producer=len(names), authenticated_review=len(own))
    if args.replay:
        output = args.replay.resolve()
        assert not output.exists() and not output.is_relative_to(ROOT) and not output.is_relative_to(args.producer.resolve())
        output.mkdir(parents=True)
        capsule = output / 'capsule'
        for name in sorted(names | {'MANIFEST.json', 'FREEZE.json'}):
            target = capsule / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(args.producer / name, target)
        with (output / 'driver.log').open('w') as log:
            subprocess.run([sys.executable, '-I', '-S', str(capsule / 'check.py'), '--output', str(output / 'replay')], cwd=output, stdout=log, stderr=subprocess.STDOUT, check=True)
        audits(capsule, output / 'replay')
        result['fresh'] = observations(output / 'replay')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
