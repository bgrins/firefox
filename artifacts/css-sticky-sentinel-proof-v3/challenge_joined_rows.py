import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise RuntimeError('Require python3 -I -S without optimization')
sys.dont_write_bytecode = True
import argparse
import copy
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--receipts', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    identity = json.loads((HERE / 'CAPSULE-IDENTITY.json').read_text())
    sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    capsule = HERE / 'capsule'
    assert sha(capsule / 'FILES.json') == identity['manifest_sha256']
    roster = json.loads((capsule / 'FILES.json').read_text())['files']
    for entry in roster:
        assert sha(capsule / entry['path']) == entry['sha256']
    spec = importlib.util.spec_from_file_location('closed_joined', capsule / 'joined.py')
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    text = (args.receipts / 'challenges.stdout').read_text()
    baseline = mod.rows(text, True)
    mod.validate_reference(baseline)
    args.output.mkdir(parents=True, exist_ok=False)
    def encode(rows):
        return '\n'.join(json.dumps(row) for row in rows)
    mutations = {}
    def edit(name, f):
        value = copy.deepcopy(baseline)
        f(value)
        mutations[name] = encode(value)
    edit('missing-row', lambda x: x.pop())
    edit('extra-row', lambda x: x.append(x[-1]))
    edit('wrong-name', lambda x: x[0].__setitem__('name', 'different'))
    edit('wrong-order', lambda x: x.reverse())
    edit('extra-field', lambda x: x[0].__setitem__('junk', 0))
    edit('nonboolean-domain', lambda x: x[0].__setitem__('admitted', 1))
    edit('nonboolean-exhaustion', lambda x: x[0].__setitem__('exhausted', 0))
    edit('extra-observation', lambda x: x[0]['machine'].__setitem__('junk', 0))
    edit('boolean-coordinate', lambda x: x[2]['machine']['frames'][0].__setitem__(0, True))
    edit('short-point', lambda x: x[2]['machine']['frames'].__setitem__(0, [0]))
    edit('numeric-trace', lambda x: x[2]['machine']['trace'].append(1))
    edit('changed-current', lambda x: x[2]['machine']['frames'][0].__setitem__(0, 999))
    edit('changed-reference', lambda x: x[2]['independent_frames'][0].__setitem__(0, 999))
    edit('changed-trace', lambda x: x[2]['machine']['trace'].append('invented'))
    edit('admitted-exhaustion', lambda x: x[2].__setitem__('exhausted', True))
    mutations['duplicate-field'] = text.replace('"admitted":', '"admitted":false,"admitted":', 1)
    results = []
    for name, candidate in mutations.items():
        try:
            rows = mod.rows(candidate, True)
            mod.validate_reference(rows)
        except RuntimeError as exc:
            results.append({'name': name, 'rejected': True, 'reason': str(exc)})
        else:
            raise RuntimeError('accepted corruption ' + name)
    result = {'status': 'pass', 'positive_rows': len(baseline), 'controls': results,
              'capsule_manifest_sha256': identity['manifest_sha256'],
              'input_sha256': sha(args.receipts / 'challenges.stdout')}
    (args.output / 'RESULT.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'status': 'pass', 'controls': len(results)}))

if __name__ == '__main__':
    main()
