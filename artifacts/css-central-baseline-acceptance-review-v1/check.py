import hashlib
import json
import os
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
REV = '90e7c8a3c46c5e84ec0bfffc239e52ea72b2085e'
CAPSULES = {
    'css-central-baseline-caller-exclusion-v1': 'acf13273b3510a0140a48c5c188a9eff0cbeed59ba70a4f1268a711cd5f334fd',
    'css-central-baseline-final-caller-audit-v1': '3414553882b131b09cfbd5521f12857b4c0388060b77362bd4acd795a6591e5f',
    'css-central-baseline-formal-independent-review-v1': '000560c3e989ba17bae51e884d2289e0cca6ab6730a8d7258ebe25ff1c08f7da',
    'css-central-baseline-origin-result-review-v1': '1951978e0fe3c01d57e1396635b38f853f47b4eaa9b9dd8e21eb56bfde8a3fde',
}

def read(p):
    return json.loads(p.read_text())

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

sources = {}
payload_counts = {}
for name, seal in CAPSULES.items():
    directory = ROOT / 'artifacts' / name
    assert sha(directory / 'FILES.json') == seal
    manifest = read(directory / 'FILES.json')
    for filename, expected in manifest.items():
        file = directory / filename
        assert file.is_file() and not file.is_symlink() and sha(file) == expected, filename
    payload_counts[name] = len(manifest)
    if (directory / 'SOURCE-PINS.json').exists():
        pins = read(directory / 'SOURCE-PINS.json')
        assert pins.get('head', pins.get('source_revision')) == REV
        for filename, expected in pins['sources'].items():
            assert filename not in sources or sources[filename] == expected
            sources[filename] = expected
env = dict(os.environ, GIT_OPTIONAL_LOCKS='0')
for filename, expected in sources.items():
    content = subprocess.check_output(['git', '-c', 'core.fsmonitor=false', 'show', REV + ':' + filename], cwd=ROOT, env=env)
    assert hashlib.sha256(content).hexdigest() == expected, filename
result = {'status': 'PASS', 'explicit_source_revision': REV, 'capsules': CAPSULES,
          'payload_counts': payload_counts, 'source_pins': sources,
          'moving_HEAD_used': False, 'native_browser_build_index_actions': False,
          'scope': 'Authentication of evidence; caller exclusions remain a reviewed source argument, not extracted Lean.'}
(HERE / 'CHECK.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({'status': 'PASS', 'capsules': len(CAPSULES), 'pinned_sources': len(sources), 'explicit_revision': REV}, indent=2))
