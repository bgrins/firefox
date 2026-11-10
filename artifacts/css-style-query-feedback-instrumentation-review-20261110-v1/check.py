from pathlib import Path
import difflib, hashlib, json, subprocess
P = Path(__file__).resolve().parent
ROOT = P.parents[1]
r = json.loads((P / 'REVIEWED.json').read_text())
owner = ROOT / r['owner_capsule']
h = lambda b: hashlib.sha256(b).hexdigest()
patch = (P / 'reviewed.patch').read_bytes()
assert h(patch) == r['patch_sha256']
assert patch == (owner / 'instrumentation.patch').read_bytes()
parts = []
for name, pin in r['files'].items():
    base = subprocess.check_output(['git', '-c', 'core.fsmonitor=false', 'show', r['revision'] + ':' + name], cwd=ROOT)
    candidate = (owner / 'source' / name).read_bytes()
    assert h(base) == pin['base_sha256'], name
    assert h(candidate) == pin['instrumented_sha256'], name
    parts.extend(difflib.unified_diff(base.decode().splitlines(True), candidate.decode().splitlines(True), fromfile='a/' + name, tofile='b/' + name))
assert ''.join(parts).encode() == patch
assert not any(line.startswith('-') and not line.startswith('---') for line in patch.decode().splitlines())
result = {'status': 'PASS', 'base_files': 4, 'candidate_files': 4, 'patch_reconstructed': True, 'removed_original_lines': 0, 'patch_sha256': r['patch_sha256']}
(P / 'CHECK.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result))
