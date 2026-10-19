import argparse
import hashlib
import json
from pathlib import Path
import stat
import subprocess
import sys

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
ROOT = Path(__file__).absolute().parent
PRODUCER_PINS = {
    'FREEZE.json': '1e316cc64b53514fc75288cddb4e341a1edcbaf4293467fd144b2903865df20c',
    'MANIFEST.json': '0ef4607c65f7accc541dd25fde3cf0c28954854cb3b5e393775f6cf63ab760f9',
    'check.py': '4f2fee2daefad0f01fac1ba3b7466ed1b72aa75b9b60fa228e6321b543e9b15f',
}


def unique(pairs):
    result = {}
    for key, value in pairs:
        assert key not in result
        result[key] = value
    return result


def read(path):
    return json.loads(path.read_text(), object_pairs_hook=unique)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def authenticate():
    assert not any(p.is_symlink() for p in [ROOT, *ROOT.parents])
    seal = read(ROOT / 'FREEZE.json')
    assert sha(ROOT / 'MANIFEST.json') == seal['manifest_sha256']
    assert sha(ROOT / 'check.py') == seal['checker_sha256']
    manifest = read(ROOT / 'MANIFEST.json')
    expected = set(manifest) | {'FREEZE.json', 'MANIFEST.json'}
    dirs = {str(d) for n in expected for d in Path(n).parents if str(d) != '.'}
    actual = set()
    for p in ROOT.rglob('*'):
        name = str(p.relative_to(ROOT))
        mode = p.lstat().st_mode
        if stat.S_ISREG(mode):
            actual.add(name)
        elif stat.S_ISDIR(mode):
            assert name in dirs
        else:
            raise AssertionError(('nonregular', name))
    assert actual == expected
    for name, digest in manifest.items():
        n = Path(name)
        assert not n.is_absolute() and '..' not in n.parts and str(n) == name
        assert sha(ROOT / name) == digest, name
    producer = ROOT / 'inputs/producer'
    for name, digest in PRODUCER_PINS.items():
        assert sha(producer / name) == digest
    original = read(producer / 'MANIFEST.json')
    assert len(original) == 32
    for name, digest in original.items():
        assert sha(producer / name) == digest
    assert {str(p.relative_to(producer)) for p in producer.rglob('*') if p.is_file()} == set(original) | {'FREEZE.json', 'MANIFEST.json'}
    return producer, len(manifest)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--replay-output', type=Path)
    args = parser.parse_args()
    producer, count = authenticate()
    receipt = read(ROOT / 'replay-receipts/CHECK.json')
    audits = read(producer / 'AUDITS.json')
    assert receipt['inputs'] == 32 and receipt['new_axiom_reports'] == 9
    assert receipt['names'] == audits['names']
    assert receipt['compiled_modules'] == audits['modules'] and len(audits['modules']) == 13
    assert len(read(producer / 'IMPORTS.json')) == 12
    assert receipt['native_execution'] is False
    assert receipt['native_payload_quotient'] == receipt['upstream_substitution_and_gate_eligibility'] == 'OPEN'
    expected = [
        ('baseline', [True] * 7),
        ('payload-only', [True, False, False, True, False, False, True]),
        ('ignore-taint-addition', [True, False, False, True, True, True, True]),
        ('ignore-taint-removal', [True, True, True, True, False, False, True]),
    ]
    assert len(receipt['mutations']) == len(expected)
    for row, (name, values) in zip(receipt['mutations'], expected):
        pattern = '|'.join(str(v).lower() for v in values)
        assert row == dict(id=name, observed=pattern, expected=pattern, compiled=True)
    assert all(c['exit'] == 0 for c in receipt['commands'])
    guards = read(ROOT / 'GUARDS.json')
    assert [g['id'] for g in guards] == [
        'changed-proof', 'shadow-python', 'shadow-lean', 'extra-empty-directory',
        'symlink', 'fifo', 'duplicate-freeze-key', 'missing-input',
        'not-isolated', 'site-enabled', 'optimized', 'internal-output', 'existing-output']
    assert all(g['exit'] != 0 for g in guards)
    for guard in guards:
        if 'output_created' in guard:
            assert guard['output_created'] is False
        if 'expected_diagnostic' in guard:
            assert guard['expected_diagnostic'] in guard['stderr']
    if args.replay_output:
        output = args.replay_output.resolve()
        assert not output.exists() and not output.is_relative_to(ROOT.resolve()) and not ROOT.resolve().is_relative_to(output)
        subprocess.run([sys.executable, '-I', '-S', str(producer / 'check.py'), '--output', str(output)], check=True)
    print(json.dumps({'verdict': 'accept-scoped', 'manifest_inputs': count, 'new_theorem_audits': 9,
                      'compiled_Lean_mutants': 3, 'independent_guard_rejections': 13,
                      'new_native_execution': False, 'full_native_history_refinement': False}))


if __name__ == '__main__':
    main()
