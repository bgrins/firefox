import argparse
import gzip
import hashlib
import json
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument('--package', type=Path, required=True)
p.add_argument('--freeze', required=True)
p.add_argument('--manifest', required=True)
p.add_argument('--output', type=Path, required=True)
a = p.parse_args()
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(a.package / 'FREEZE.json') == a.freeze
assert sha(a.package / 'MANIFEST.json') == a.manifest
for entry in json.loads((a.package / 'MANIFEST.json').read_text()):
    q = a.package / entry['path']
    assert q.is_file() and not q.is_symlink() and sha(q) == entry['sha256']
module = {'__file__': str(a.package / 'native/check_rows.py'), '__name__': 'independent_challenge_target'}
exec(compile((a.package / 'native/check_rows.py').read_text(), module['__file__'], 'exec'), module)
providers = json.loads((a.package / 'receipts/PROVIDERS.json').read_text())
text = gzip.decompress((a.package / 'receipts/candidate.tsv.gz').read_bytes()).decode()
assert not module['verify'](text, providers, 'candidate', 0)['failures']
lines = text.splitlines()
records = []

def altered(field, change):
    changed = lines.copy()
    row = changed[0].split('\t')
    row[field] = change(row[field])
    changed[0] = '\t'.join(row)
    return '\n'.join(changed) + '\n'

def check(name, changed, variant='candidate', status=0):
    try:
        module['verify'](changed, providers, variant, status)
    except (AssertionError, ValueError, IndexError) as error:
        records.append({'name': name, 'result': 'REJECTED', 'error_type': type(error).__name__, 'reason': str(error)[:2000], 'input_sha256': hashlib.sha256(changed.encode()).hexdigest()})
    else:
        raise AssertionError('accepted corruption: ' + name)

check('bits trailing junk', altered(9, lambda s: s + 'junk'))
check('longhand set trailing junk', altered(10, lambda s: s + 'junk'))
check('custom set trailing junk', altered(11, lambda s: s + 'junk'))
check('nonbinary gate', altered(3, lambda s: '2'))
check('extra field', '\n'.join([lines[0] + '\textra'] + lines[1:]) + '\n')
check('missing final case', '\n'.join(lines[:-1]) + '\n')
check('wrong name', altered(1, lambda s: s + '-wrong'))
check('wrong initial state', altered(5, lambda s: '[Row { key: 99999, value: 1, important: false }]'))
check('candidate prefix falsely labelled exit42', '\n'.join(lines[:1]) + '\n', status=42)
changed = lines.copy()
row = changed[0].split('\t')
for i in [6, 7, 8]:
    assert 'value: 0,' in row[i]
    row[i] = row[i].replace('value: 0,', 'value: 999,', 1)
changed[0] = '\t'.join(row)
check('self-consistent altered action and results', '\n'.join(changed) + '\n')
a.output.mkdir(parents=True, exist_ok=False)
(a.output / 'CHECK.json').write_text(json.dumps({'result': 'PASS', 'rejections': len(records), 'records': records}, indent=2) + '\n')
