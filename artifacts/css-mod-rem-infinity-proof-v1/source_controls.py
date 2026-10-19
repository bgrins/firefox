import hashlib
import json
from pathlib import Path
import shutil
import sys

import check


BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[1]
RELATIVE_SOURCE = Path('servo/components/style/values/generics/calc.rs')
COPIES = ['old-dispatch.rs', 'proposed-dispatch.rs', 'SOURCE-v1.json',
          'SPEC-v1.json', 'values4-round-infinities.txt', 'values4-calc-ieee.txt']


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    if sys.flags.optimize or len(sys.argv) != 2:
        raise RuntimeError('Usage: python3 source_controls.py NEW_OUTPUT_DIRECTORY')
    out = Path(sys.argv[1]).resolve()
    out.mkdir()
    inputs = [BASE / name for name in COPIES + ['source_controls.py', 'check.py']]
    inputs += [ROOT / RELATIVE_SOURCE]
    before = {str(path): sha(path) for path in inputs}
    old = (BASE / 'old-dispatch.rs').read_text()
    proposed = (BASE / 'proposed-dispatch.rs').read_text()
    records = []

    def fixture(name, source, expected_candidate, error=None, change=None):
        directory = out / name
        root = directory / 'root'
        base = directory / 'companion'
        base.mkdir(parents=True)
        source_path = root / RELATIVE_SOURCE
        source_path.parent.mkdir(parents=True)
        source_path.write_text(source)
        for filename in COPIES:
            shutil.copyfile(BASE / filename, base / filename)
        if change is not None:
            change(base)
        check.ROOT, check.BASE = root, base
        record = {'name': name, 'expected_candidate': expected_candidate}
        try:
            result = check.source_binding()
            if result['live_candidate_verified'] != expected_candidate:
                raise RuntimeError('Candidate classification mismatch')
        except RuntimeError as exception:
            if str(exception) != error:
                raise
            record['rejected'] = str(exception)
        else:
            if error is not None:
                raise RuntimeError('Accepted corrupted source fixture: ' + name)
            record['accepted'] = result
        records.append(record)

    def replace_once(text, old_text, new_text):
        if text.count(old_text) != 1:
            raise RuntimeError('Mutation cardinality mismatch')
        return text.replace(old_text, new_text)

    def corrupt(filename):
        def change(base):
            path = base / filename
            path.write_bytes(path.read_bytes() + b'\nmodified\n')
        return change

    fixture('old-companion', old, False)
    fixture('candidate-companion', proposed, True)
    fixture('candidate-downgrade', old, True, 'Candidate classification mismatch')
    fixture('missing-finite-guard', replace_once(proposed,
            'dividend.is_finite() && divisor.is_infinite()', 'divisor.is_infinite()'),
            True, 'Unreviewed native helper')
    fixture('wrong-identity-value', replace_once(proposed, 'return dividend;', 'return 0.0;'),
            True, 'Unreviewed native helper')
    fixture('wrong-operation', replace_once(proposed,
            'matches!(self, Self::Mod)', 'matches!(self, Self::Rem)'),
            True, 'Unreviewed native helper')
    fixture('duplicate-helper', proposed + '\n' + proposed,
            True, 'Ambiguous native helper')
    fixture('missing-helper', '', True, 'Ambiguous native helper')
    fixture('old-snapshot-tampered', proposed, True, 'Source snapshot changed',
            corrupt('old-dispatch.rs'))
    fixture('proposed-snapshot-tampered', proposed, True, 'Source snapshot changed',
            corrupt('proposed-dispatch.rs'))
    fixture('exception-spec-tampered', proposed, True, 'Spec excerpt changed',
            corrupt('values4-round-infinities.txt'))
    fixture('nan-spec-tampered', proposed, True, 'Spec excerpt changed',
            corrupt('values4-calc-ieee.txt'))
    check.ROOT, check.BASE = ROOT, BASE
    live = check.source_binding()
    if not live['live_candidate_verified']:
        raise RuntimeError('Live candidate absent')
    if before != {str(path): sha(path) for path in inputs}:
        raise RuntimeError('Inputs changed during source controls')
    report = {'status': 'pass', 'source_controls': records, 'live': live,
              'inputs': before,
              'outputs': {str(path.relative_to(out)): sha(path)
                          for path in out.rglob('*') if path.is_file()}}
    (out / 'report.json').write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
    print(json.dumps({'status': 'pass', 'accepted_fixtures': 2, 'rejected_controls': 10,
                      'live_candidate_verified': True}))


if __name__ == '__main__':
    main()
