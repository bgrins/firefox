import json
from pathlib import Path
import source_binding as binding
from candidate_check import SOURCE_NAMES

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[1]
paths = [BASE / name for name in SOURCE_NAMES + ['candidate_freeze.py']]
reports = {}
for name in ['candidate-snapshot-check-v1', 'candidate-live-check-v1']:
    directory = BASE / name
    report = json.loads((directory / 'report.json').read_text())
    if report['status'] != 'pass' or report['live_native_verified'] != ('live' in name):
        raise RuntimeError('Missing successful replay')
    for path, digest in report['pins'].items():
        if binding.digest(Path(path).read_bytes()) != digest:
            raise RuntimeError('Replay input drift: ' + path)
    paths.extend(path for path in directory.rglob('*') if path.is_file())
    reports[name] = report['live_native_verified']
paths += [ROOT / binding.MIX, ROOT / binding.FLAGS,
          ROOT / 'artifacts/stylo-bloom-tools/lean-4.35.0-rc4-darwin_aarch64/bin/lean']
for name in ['CANDIDATE-REVIEW-v1.md', 'oracle_audit.py', 'WPT-ORACLE-AUDIT-v1.json']:
    paths.append(ROOT / 'artifacts/css-color-zero-prefix-review-v1' / name)
oracle = json.loads(paths[-1].read_text())
if binding.digest((ROOT / oracle['wpt']).read_bytes()) != oracle['wpt_sha256']:
    raise RuntimeError('WPT changed since oracle audit')
paths.append(ROOT / oracle['wpt'])
record = {'status': 'producer verified candidate; root acceptance separate',
          'audits': 17, 'compiled_mutations': 4, 'record_controls': 9, 'source_controls': 15,
          'reviewed_wpt_oracles': 16, 'replays': reports,
          'source_bridge': 'manual exact-delta review, not Rust extraction',
          'pins': {str(path.relative_to(ROOT)): binding.digest(path.read_bytes()) for path in sorted(set(paths))}}
target = BASE / 'CANDIDATE-PROOF-v1.json'
if target.exists() and json.loads(target.read_text()) != record:
    raise RuntimeError('Refusing to overwrite different frozen candidate')
target.write_text(json.dumps(record, indent=2, sort_keys=True) + '\n')
print(json.dumps({'capsule': str(target.relative_to(ROOT)), 'sha256': binding.digest(target.read_bytes()), 'pins': len(record['pins'])}))
