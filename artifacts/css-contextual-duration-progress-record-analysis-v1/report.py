import argparse
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import re
import stat
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
PACKAGES = {
    'css-contextual-duration-progress-transport-v1': 'ecbced58a63274524761547f40823ee769c7079712dcafcf45d9777ebcb057ab',
    'css-contextual-duration-acyclic-two-hop-probe-v2': '88569c6fa37f083f17f6d26398d6f6bd32174d9780df30845c7aca7efb0fa3c3',
    'css-contextual-duration-property-only-wakeup-probe-v2': '204ce79b3a6dbdfdc092f21e1c62843b93990fbdc31cad91ec71a8b4c19fe5f0',
    'css-contextual-duration-lh-chain-probe-v1': '00741267bc9eee236c74972cffae76182c4bb03e0170264f1e549c7b23589d99',
}
KINDS = [suite + '-' + mode for suite in ('two-hop', 'property-only', 'lh-chain')
         for mode in ('literal', 'ordinary', 'animated')]
sha = lambda body: hashlib.sha256(body).hexdigest()


def reject_constant(value):
    raise ValueError('Non-JSON constant: ' + value)


def finite_float(text):
    value = float(text)
    if not math.isfinite(value):
        raise ValueError('Overflowing JSON number')
    return value


def validators():
    for name, digest in PACKAGES.items():
        directory = ROOT / 'artifacts' / name
        manifest = (directory / 'FILES.json').read_bytes()
        assert sha(manifest) == digest, name
        for path, record in json.loads(manifest).items():
            relative = Path(path)
            assert not relative.is_absolute() and '..' not in relative.parts
            target = directory / relative
            assert not target.is_symlink()
            body = target.read_bytes()
            assert sha(body) == record['sha256'] and len(body) == record['bytes'], path
    modules = {}
    for suite, package, name in [
        ('shared', 'css-contextual-duration-progress-transport-v1', 'duration-progress-record.py'),
        ('lh-chain', 'css-contextual-duration-lh-chain-probe-v1', 'duration-lh-progress-record.py')]:
        spec = importlib.util.spec_from_file_location('progress_' + suite, ROOT / 'artifacts' / package / name)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        modules[suite] = module
    return modules


def numeric(value):
    return type(value) in (int, float) and math.isfinite(value)


def comparison(actual, expected, tolerance, asserted):
    valid = numeric(actual)
    return {'actual': actual, 'expected': expected, 'difference': actual - expected if valid else None,
            'tolerance': tolerance, 'within_tolerance': abs(actual - expected) <= tolerance if valid else None,
            'numeric_value_available': valid, 'fixture_asserts_this_stage': asserted}


def flat(snapshot):
    result = {}
    for key, value in snapshot.items():
        if isinstance(value, dict):
            result.update({key + '.' + nested: item for nested, item in value.items()})
        else:
            result[key] = value
    return result


def oracle(suite, mode, time):
    if suite == 'property-only':
        return {'width': (32 + 64 * time / 2000, .02), 'cssDuration': (2000, .05),
                'parentFont': (32, 0), 'duration': (2000, 0), 'progress': (time / 2000, .000001),
                'time': (time, 0)}
    middle = 16 + 16 * time / 2000
    duration = 1375 if mode == 'literal' else middle / 16 * 1000
    result = {'childOpacity': (time / duration, .0001), 'childDuration': (duration, .1),
              'middleDuration': (2000, .05), 'middle.duration': (2000, .05),
              'child.duration': (duration, .1), 'child.progress': (time / duration, .0001),
              'middle.time': (time, 0), 'child.time': (time, 0)}
    if suite == 'two-hop':
        result.update(rootFont=(32, .02), middleFont=(middle, .02))
    else:
        result.update(parentFont=(32, .02), middleLineHeight=(middle, .02), childLineHeight=(middle, .02))
    return result


def observe(kind, value):
    suite, mode = kind.rsplit('-', 1)
    stages = []
    dimension = 'width' if suite == 'property-only' else 'opacity'
    expected = 56 if suite == 'property-only' else 6 / 11
    tolerance = .02 if suite == 'property-only' else .0001
    for index, sample in enumerate(value['samples']):
        stages.append({'stage': sample['phase'], 'raw': sample,
                       'comparisons': {dimension: comparison(sample[dimension], expected, tolerance, index == 3)},
                       'purpose': 'First-read diagnostic; not an asserted convergence boundary' if index == 0
                                  else 'Child-only sampled frame; getter can flush'})
    for key in ('beforeMembership', 'afterMembership', 'seek751', 'afterSeek'):
        time = 751 if key == 'seek751' else 750
        actual = flat(value[key])
        comparisons = {field: comparison(actual.get(field), wanted, epsilon, key != 'seek751')
                       for field, (wanted, epsilon) in oracle(suite, mode, time).items()}
        states = {field: {'actual': item, 'expected': 'paused', 'matches': item == 'paused', 'fixture_asserts_this_stage': key != 'seek751'}
                  for field, item in actual.items() if field == 'state' or field.endswith('.state')}
        stages.append({'stage': key, 'raw': value[key], 'comparisons': comparisons, 'states': states,
                       'purpose': 'Sequential read, not atomic; after child-only collection' if key == 'beforeMembership'
                                  else 'After explicit membership or seek intervention',
                       'oracle_limit': '751ms continuous arithmetic reference only; fixture does not assert it, and length quantization may affect dependent duration' if key == 'seek751' else None})
    first = stages[0]['comparisons'][dimension]['within_tolerance']
    last = stages[3]['comparisons'][dimension]['within_tolerance']
    return {'stages': stages, 'membership': value.get('membership', value.get('same')),
            'driver_timing': value['driverTiming'], 'first_sample_matches_fixed_oracle': first,
            'last_passive_sample_matches_fixed_oracle': last,
            'first_mismatch_then_last_match': first is False and last is True,
            'first_flush_correctness_claim': False, 'callback_pass_fail_inferred': False}


def read_record(path):
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    try:
        before = os.fstat(fd)
        assert stat.S_ISREG(before.st_mode) and before.st_size <= 262144, 'not a bounded regular record'
        with os.fdopen(fd, 'rb', closefd=False) as stream:
            body = stream.read(262145)
        after = os.fstat(fd)
        assert (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns) == (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns)
        assert len(body) == before.st_size
        return body
    finally:
        os.close(fd)


def analyze(directory, run_id, modules):
    assert re.fullmatch(r'[A-Za-z0-9_-]{16,128}', run_id)
    directory = Path(directory)
    directory_ok = directory.is_dir() and not directory.is_symlink()
    result = {'record_directory': str(directory), 'expected_run_id': run_id,
              'directory_available': directory_ok, 'directory_issue': None if directory_ok else ('symlink refused' if directory.is_symlink() else 'missing or not a directory'), 'records': {}, 'native_acceptance': False,
              'callback_pass_fail_inferred': False, 'first_flush_correctness_claim': False}
    result['unexpected_names'] = sorted(set(os.listdir(directory)) - {kind + '.json' for kind in KINDS}) if directory_ok else []
    for kind in KINDS:
        record = {'filename': kind + '.json', 'availability': 'missing', 'observation': None}
        path = directory / record['filename']
        if directory_ok and (path.exists() or path.is_symlink()):
            record['availability'] = 'invalid'
            try:
                body = read_record(path)
                record.update(sha256=sha(body), bytes=len(body))
                try:
                    envelope = json.loads(body, parse_constant=reject_constant, parse_float=finite_float)
                except ValueError:
                    record['raw_text'] = body.decode('utf-8', errors='replace')
                    raise
                record['raw_envelope'] = envelope
                assert isinstance(envelope, dict) and set(envelope) == {'run_id', 'kind', 'observation'}, 'envelope fields'
                assert envelope['run_id'] == run_id and envelope['kind'] == kind, 'run/kind binding'
                module = modules['lh-chain' if kind.startswith('lh-chain-') else 'shared']
                assert module.validate({key: envelope[key] for key in ('kind', 'observation')}) == kind
                record['observation'] = observe(kind, envelope['observation'])
                record.pop('raw_envelope')
                record['availability'] = 'valid'
            except (OSError, AssertionError, ValueError, TypeError, KeyError, OverflowError) as error:
                record['error'] = repr(error)
        result['records'][kind] = record
    result['missing_kinds'] = [kind for kind, record in result['records'].items() if record['availability'] == 'missing']
    result['invalid_kinds'] = [kind for kind, record in result['records'].items() if record['availability'] == 'invalid']
    result['collection_complete'] = not result['missing_kinds'] and not result['invalid_kinds'] and not result['unexpected_names']
    result['limits'] = [
        'Collection completeness is not callback PASS, convergence, or a native liveness result.',
        'First and intermediate samples remain separate even when a later value matches.',
        'A missing record does not identify whether acquisition, collection or transport failed; inspect raw WPT.',
        'Detailed snapshots are sequential getters and may flush; membership and seeks are interventions.',
        '751ms comparisons are unasserted continuous reference values; dependent length quantization may differ.',
        'Record envelope and fixture schemas are authenticated; full owner/runtime/state authenticity is separate.',
    ]
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--records', type=Path, required=True)
    parser.add_argument('--run-id', required=True)
    args = parser.parse_args()
    print(json.dumps(analyze(args.records, args.run_id, validators()), indent=2, sort_keys=True, allow_nan=False))


if __name__ == '__main__':
    main()
