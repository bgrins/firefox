import hashlib
import importlib.util
import json
from pathlib import Path
import sys
assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
read = lambda path: json.loads(path.read_bytes())
for path, digest in read(HERE / 'REFERENCES.json').items():
    assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == digest, path
path = ROOT / 'artifacts/css-explicit-taint-typed-reparse-publication-v1/evidence.py'
spec = importlib.util.spec_from_file_location('saved_publication_evidence', path)
evidence = importlib.util.module_from_spec(spec)
spec.loader.exec_module(evidence)
result = evidence.verify(ROOT, read(HERE / 'PAIR-BINDING.json'), read(HERE / 'STAGE.json'))
assert result['target_candidate_PASS'] == 4 and result['preserved_control_callbacks'] == 75
assert result['full_baseline_signatures_preserved'] and result['root_live_restoration_verified']
assert not result['native_publication_performed']
print(json.dumps(result, indent=2, sort_keys=True))
