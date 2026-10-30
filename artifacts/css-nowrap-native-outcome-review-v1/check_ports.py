import copy
import importlib.util
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

ports = load('ports', HERE / 'ports.py')
assessor = load('assessor', ROOT / 'artifacts/css-nowrap-native-pair-v1/assess.py')
runtime = ROOT / 'artifacts/css-nowrap-native-pair-runtime-1'
phases = {role: runtime / (role + '-wpt-regression') for role in ['original', 'candidate']}
data = {role: ([json.loads(line) for line in (phase / 'raw.jsonl').read_text().splitlines()], json.loads((phase / 'ASSESSMENT.json').read_bytes()), json.loads((phase / 'metadata/MANIFEST.json').read_bytes())) for role, phase in phases.items()}
expected, _ = ports.normalize(*data['original'], assessor.signature)
actual, _ = ports.normalize(*data['candidate'], assessor.signature)
assert actual == expected
rejected = []
for label in ['status', 'expected', 'expected presence', 'intermittent', 'path', 'host', 'scheme', 'relation', 'non-port text', 'unbound port', 'startup absent', 'server PID', 'reference manifest', 'ordinary callback message']:
    events, assessment, manifest = copy.deepcopy(data['candidate'])
    end = next(e for e in assessment['ends'] if e['test'] in ports.KNOWN)
    if label == 'status': end['status'] = 'FAIL'
    elif label == 'expected': end['expected'] = 'FAIL'
    elif label == 'expected presence': end['expected'] = 'PASS'
    elif label == 'intermittent': end['known_intermittent'] = ['FAIL']
    elif label == 'path': end['message'] = end['message'].replace('.html', '-changed.html', 1)
    elif label == 'host': end['message'] = end['message'].replace('web-platform.test', 'other.test')
    elif label == 'scheme': end['message'] = end['message'].replace('http:', 'https:')
    elif label == 'relation': end['message'] = end['message'].replace(' == ', ' != ')
    elif label == 'non-port text': end['message'] += 'extra'
    elif label == 'unbound port': end['message'] = end['message'].replace(':57484', ':57483')
    elif label == 'startup absent': events = [e for e in events if e.get('message') != 'Starting https server on https://127.0.0.1:57484']
    elif label == 'server PID':
        next(e for e in events if e.get('message') == 'Stopped http server on 127.0.0.1:57484')['pid'] += 1
    elif label == 'reference manifest': manifest['items']['reftest']['css']['css-text']['hyphens']['hyphenate-limit-chars-001.html'][1][1][0][1] = '!='
    elif label == 'ordinary callback message': assessment['rows'][0]['message'] = 'changed'
    try:
        normalized, _ = ports.normalize(events, assessment, manifest, assessor.signature)
        assert normalized == expected
    except AssertionError:
        rejected.append(label)
    else:
        raise AssertionError('accepted mutation: ' + label)
print(json.dumps({'actual_saved_pair_matches_after_narrow_normalization': True, 'negative_controls': rejected, 'count': len(rejected), 'native_or_browser_operations': False}))
