import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
freeze = json.loads((ROOT/'FREEZE.json').read_text())
assert digest(ROOT/'FILES.json') == freeze['manifest_sha256']
assert digest(ROOT/'REPORT.md') == freeze['report_sha256']
assert digest(ROOT/'replay.py') == freeze['replay_sha256']
assert digest(ROOT/'verify.py') == freeze['verify_sha256']
rows = json.loads((ROOT/'FILES.json').read_text())
wanted = {'FILES.json','FREEZE.json'} | {row['path'] for row in rows}
assert len(wanted) == len(rows) + 2
actual = {str(p.relative_to(ROOT)) for p in ROOT.rglob('*') if p.is_file()}
assert actual == wanted
directories = {str(p.relative_to(ROOT)) for p in ROOT.rglob('*') if p.is_dir()}
expected_dirs = {str(p) for name in wanted for p in Path(name).parents if str(p) != '.'}
assert directories == expected_dirs
assert not any(p.is_symlink() for p in ROOT.rglob('*'))
for row in rows:
    p = ROOT/row['path']
    assert p.stat().st_size == row['size'] and digest(p) == row['sha256']
print(json.dumps({'closed':True,'files':len(rows),'decision':freeze['decision']}))
