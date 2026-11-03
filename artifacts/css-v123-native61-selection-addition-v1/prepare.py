import hashlib
import json
import os
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
BASE = ROOT / 'artifacts/css-research-checkpoint-20261103-v123'
HEAD = 'e86b64866cdc5e2260ba9be08c45756fd96e21bb'
ENV = dict(os.environ, GIT_OPTIONAL_LOCKS='0')
GIT = ['git', '--no-optional-locks', '-c', 'core.fsmonitor=false']
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_bytes())
save = lambda n, value: (HERE / n).write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')
assert subprocess.check_output(GIT + ['rev-parse', 'HEAD'], cwd=ROOT, env=ENV).decode().strip() == HEAD
base = read(BASE / 'SELECTION.json')
assert len(base) == 2719
base_bindings = read(BASE / 'BINDINGS.json')
assert sha(BASE / 'SELECTION.json') == base_bindings['selection_sha256']
required, origins, conflict = {}, {}, []
excluded, missing, tracked, added, existing = {}, {}, {}, {}, {}
manifests, parsed, completed = {}, set(), {}
partial_records = {}
blocked = ('artifacts/css-keyframe-font-unit-raw-index-refresh-', 'artifacts/css-checkpoint-admission-memo')

def demand(path, digest, origin):
    if not isinstance(path, str) or not path.startswith('artifacts/'):
        return
    if not isinstance(digest, str) or not re.fullmatch('[0-9a-f]{64}', digest):
        return
    if path.startswith(blocked) or '/backups/' in path or '/.git/' in path or '/objdir' in path or '.app/' in path:
        excluded[path] = {'reason': 'active refresh, backup, binary, or memo exclusion', 'origin': origin}
        return
    if path in required and required[path] != digest:
        conflict.append({'path': path, 'old': required[path], 'new': digest, 'origin': origin})
        return
    required[path] = digest
    origins.setdefault(path, []).append(origin)

def discover(value, origin):
    if isinstance(value, list):
        for row in value:
            discover(row, origin)
    elif isinstance(value, dict):
        if isinstance(value.get('path'), str):
            demand(value['path'], value.get('sha256'), origin)
        if isinstance(value.get('directory'), str):
            demand(value['directory'] + '/FILES.json', value.get('manifest_sha256'), origin)
        for key, row in value.items():
            if isinstance(key, str) and key.startswith('artifacts/'):
                demand(key, row if isinstance(row, str) else row.get('sha256') if isinstance(row, dict) else None, origin)
            discover(row, origin)

seeds = {
    'css-keyframe-font-unit-candidate-browser-v3': 'b8369329',
    'css-keyframe-font-unit-candidate-browser-runtime-v1': '4e5fdea1',
    'css-keyframe-font-unit-native-root-audit-v2': 'd0bf7246',
    'css-keyframe-font-unit-native61-outcome-v2': 'b0046130',
    'css-keyframe-font-unit-original61-v1': None,
    'css-keyframe-font-unit-native-current-capture-v2': 'e89506c7',
    'css-keyframe-font-unit-dependency-fix-v1': 'bc707600',
}
for number in range(169, 173):
    seeds[f'css-continuation-roadmap-20261103-v{number}'] = None
for name, prefix in seeds.items():
    path = f'artifacts/{name}/FILES.json'
    digest = sha(ROOT / path)
    assert prefix is None or digest.startswith(prefix), (path, digest)
    demand(path, digest, 'explicit completed seed')
individuals = [
    'css-keyframe-font-unit-native-current-v2.json',
    'css-keyframe-font-unit-native-current-root-terminal-v2.json',
    'css-keyframe-font-unit-native-current-root-capture-v2.log',
    'css-keyframe-font-unit-candidate-browser-root-run-v1.log',
    'css-keyframe-font-unit-candidate-browser-root-launch-v1.json',
    'css-keyframe-font-unit-native-root-audit-root-run-v2.log',
    'css-keyframe-font-unit-native61-outcome-root-run-v2.log',
]
for name in individuals:
    path = 'artifacts/' + name
    demand(path, sha(ROOT / path), 'explicit closed operational record')
activation = ROOT / 'artifacts/css-keyframe-font-unit-candidate-browser-root-activation-v1'
for path in sorted(activation.rglob('*')):
    if path.is_file() and not path.is_symlink():
        demand(str(path.relative_to(ROOT)), sha(path), 'completed native activation preimage')

while True:
    batch = [name for name in required if name not in parsed]
    if not batch:
        break
    heads = {}
    for start in range(0, len(batch), 80):
        raw = subprocess.check_output(GIT + ['ls-tree', '-z', HEAD, '--'] + batch[start:start+80], cwd=ROOT, env=ENV)
        for entry in raw.split(b'\0'):
            if not entry:
                continue
            metadata, path = entry.split(b'\t', 1)
            mode, kind, blob = metadata.decode().split()
            assert kind == 'blob'
            heads[path.decode()] = (mode, blob)
    for name in batch:
        parsed.add(name)
        digest = required[name]
        path = ROOT / name
        if path.is_symlink():
            excluded[name] = {'reason': 'symlink, never followed', 'origins': origins[name]}
            continue
        if not path.is_file():
            missing[name] = {'expected_sha256': digest, 'reason': 'missing regular file', 'origins': origins[name]}
            continue
        actual = sha(path)
        if actual != digest:
            missing[name] = {'expected_sha256': digest, 'actual_sha256': actual, 'reason': 'hash mismatch', 'origins': origins[name]}
            continue
        if name in heads:
            mode, blob = heads[name]
            body = subprocess.check_output(GIT + ['cat-file', 'blob', blob], cwd=ROOT, env=ENV)
            if hashlib.sha256(body).hexdigest() != digest:
                missing[name] = {'reason': 'HEAD blob differs from required live artifact', 'blob': blob, 'expected_sha256': digest}
                continue
            tracked[name] = {'sha256': digest, 'bytes': len(body), 'head': HEAD, 'blob': blob, 'mode': mode}
            continue
        if name in base:
            assert base[name] == {'sha256': digest, 'bytes': path.stat().st_size}, name
            existing[name] = base[name]
            continue
        added[name] = {'sha256': digest, 'bytes': path.stat().st_size}
        if name == 'artifacts/css-keyframe-font-unit-candidate-browser-root-activation-v1/FILES.json':
            old_manifest = read(path)
            for payload, record in old_manifest.items():
                original = path.parent / payload if payload == 'POLICY.json' else ROOT / 'artifacts/css-keyframe-font-unit-candidate-browser-v3' / payload
                assert sha(original) == record['sha256']
            partial_records[name] = {'reason': 'disabled owner manifest preimage; not an activation-directory closure', 'preimage_payloads_verified_against_owner_or_saved_policy': len(old_manifest)}
            continue
        if path.name == 'FILES.json':
            manifest = read(path)
            payloads = manifest.get('files', manifest)
            rows = [(r['path'], r) for r in payloads] if isinstance(payloads, list) else list(payloads.items())
            assert len({n for n, r in rows}) == len(rows)
            manifests[name] = []
            for n, row in rows:
                assert not Path(n).is_absolute() and '..' not in Path(n).parts
                child = str((path.parent / n).relative_to(ROOT))
                pin = row if isinstance(row, str) else row['sha256']
                manifests[name].append(child)
                demand(child, pin, name)
            for n in manifest.get('verified_staging_tool_links', []):
                excluded[str((path.parent / n).relative_to(ROOT))] = {'reason': 'manifest-recorded non-followed staging symlink'}
        elif path.name in ('POLICY.json', 'BINDINGS.json', 'REFERENCES.json', 'SOURCE-ROLES.json', 'SOURCE-MAP.json', 'ORIGINS.json', 'CHECK.json', 'INPUTS.json'):
            discover(read(path), name)

projections = {}
for name, paths in manifests.items():
    if all(path in base or path in added for path in paths):
        completed[name] = required[name]
    else:
        projections[name] = {'reused_tracked': [x for x in paths if x in tracked], 'missing_or_excluded': [x for x in paths if x not in base and x not in added and x not in tracked]}
assert not set(base).intersection(added)
assert not set(added).intersection(tracked)
save('ADDITIONAL-SELECTION.json', added)
save('ADDITIONAL-COMPLETED-PACKAGES.json', completed)
save('TRACKED-DEPENDENCIES.json', tracked)
save('ALREADY-SELECTED-DEPENDENCIES.json', existing)
save('MISSING-DEPENDENCIES.json', {'missing': missing, 'conflicting_requirements': conflict})
save('EXCLUDED.json', excluded)
save('REUSED-PACKAGE-PROJECTIONS.json', projections)
save('PARTIAL-RECORDS.json', partial_records)
save('ORIGINS.json', origins)
save('PENDING.json', {'raw_refresh': 'active session70533; excluded', 'fresh_v123_capture': None, 'final_v123_epoch_controls': None, 'memo': 'unfinished; excluded'})
save('SUMMARY.json', {'head': HEAD, 'base_selection_sha256': sha(BASE / 'SELECTION.json'), 'base_paths': len(base), 'additional_paths': len(added), 'additional_bytes': sum(x['bytes'] for x in added.values()), 'new_complete_closures': len(completed), 'tracked_reused': len(tracked), 'already_selected_reused': len(existing), 'missing': len(missing), 'conflicting_requirements': len(conflict), 'excluded': len(excluded), 'partially_reused_closures': len(projections), 'v123_edited': False, 'git_read_only': ['rev-parse HEAD', 'ls-tree -z HEAD -- exact-paths', 'cat-file blob exact-object-id']})
print(json.dumps(read(HERE / 'SUMMARY.json')))
