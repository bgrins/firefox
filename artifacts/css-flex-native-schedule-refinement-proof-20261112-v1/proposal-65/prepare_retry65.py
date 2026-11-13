import hashlib
import importlib.util
import json
import re
from pathlib import Path

root = Path(__file__).resolve().parent
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
proposal = json.loads((root / 'PROPOSED-65.json').read_text())
assert sha(root / 'PROPOSED-65.json') == '4f5d5118cd891ce68cee3b4c863556ebef5c50bfb13b8124d8263c5c015a7c9b'
assert not (root / 'development-65').exists()
for name, digest in proposal['source_hashes'].items():
    assert sha(root / 'inputs' / (name + '.v')) == digest
transport = json.loads((root / 'TRANSPORT.json').read_text())
for name, entry in transport.items():
    assert sha(root / 'inputs' / name) == entry['sha256'] == sha(root.parent.parent / entry['origin'])
target = root.parent / 'css-flex-native-schedule-refinement-target-20261112-v1'
assert sha(target / 'FILES.json') == '73297f6cfe01d319345d7506fcabc3ba729062b09569f21a527e5c3487d54b12'
assert sha(root / 'inputs/NativeJointSpec.v') == 'd0fdcb07ad81d95f34aa09a89cac9d31b8c71c126c3c8f37f2d2a55492dcf45a'
assert sha(root / 'inputs/NativeRefinementSpec.v') == 'a8e1f4666002d249e8f8a88b25e8801d5c9fc0d74c55b4802fed66dc5801ebc9'
modules = json.loads((root / 'MODULES.json').read_text())
base = json.loads((root / 'BASE-MODULES.json').read_text())
required = set(base)
dependencies = {}
def visit(name):
    assert name in modules
    if name in required:
        return
    required.add(name)
    source = (root / 'inputs' / (name + '.v')).read_text()
    local = []
    for clause in re.findall(r'Require\s+(?:Import|Export)\s+(.*?)\.(?=\s|$)', source, re.S):
        for dependency in clause.split():
            if (root / 'inputs' / (dependency + '.v')).exists():
                local.append(dependency)
                visit(dependency)
    dependencies[name] = local
for name in proposal['selection']:
    visit(name)
selected = [name for name in modules if name in required]
assert len(selected) == len(set(selected)) == len(required)
positions = {name: i for i, name in enumerate(selected)}
for name, deps in dependencies.items():
    assert all(positions[dependency] < positions[name] for dependency in deps), name
cache = root / 'development-1/output/base-cache'
cache_entries = json.loads((cache / 'CACHE.json').read_text())
assert set(cache_entries) == set(base)
for name, entry in cache_entries.items():
    assert sha(root / 'inputs' / (name + '.v')) == entry['source_sha256']
    assert sha(cache / (name + '.vo')) == entry['object_sha256']
spec = importlib.util.spec_from_file_location('prepared_audit', root / 'audit.py')
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)
roster = []
for name in selected:
    if name in base:
        continue
    source = (root / 'inputs' / (name + '.v')).read_text()
    assert not re.search(r'^\s*(?:Admitted\.|admit\.|Axioms?\s|Parameters?\s)', source, re.M), name
    roster += [name + '.' + declared for declared in re.findall(r'Print Assumptions ([\w.]+)\.', source)]
assert len(roster) == len(set(roster))
image = json.loads((root / 'IMAGE.json').read_text())['Id']
assert image == 'sha256:552c20236f2d19676d19bb7a80cf290dbd234e37f644a04b3d396b4f6ca30dbf'
assert 'timeout=120' in (root / 'check_kernel.py').read_text()
for token in ['--network=none', '--read-only', '--cap-drop=ALL', '--memory=1g', '--cpus=1', '--pids-limit=128']:
    assert token in (root / 'launch.py').read_text()
record = {
    'status': 'source-only preparation PASS; NOT executed or newly proved',
    'authorization': 'fresh explicit parent lane release required',
    'proposal_sha256': sha(root / 'PROPOSED-65.json'),
    'transported_sources_unchanged': len(transport),
    'source_sha256': {name: sha(root / 'inputs' / (name + '.v')) for name in selected},
    'selected_modules': selected, 'local_dependencies': dependencies,
    'expected_commands': [(['cache-import', name] if name in base else ['coqc', '-q', name + '.v']) for name in selected] + [['coqchk', '-silent'] + selected],
    'expected_audit_roots': roster,
    'axiom_policy': {'allowed_exact_signatures': audit.TYPES, 'per_root_actual_dependencies': 'must be parsed from successful emitted audits; not predicted or accepted here'},
    'cache_manifest_sha256': sha(cache / 'CACHE.json'), 'image': image,
    'driver_sha256': {name: sha(root / name) for name in ['launch.py', 'check_kernel.py', 'audit.py', 'MODULES.json', 'BASE-MODULES.json', 'ROOTS.json']},
    'invocation': ['python3', '-I', '-B', 'launch.py', '65', '--cache', 'development-1/output/base-cache', '--select', 'NativeProjectionOriginal'],
    'limits': {'workers': 1, 'cpu': 1, 'memory_bytes': 1073741824, 'per_command_seconds': 120, 'network': 'none'},
    'previous_accepted_checkpoint': 'CHECKPOINT-64.json',
}
previous = json.loads((root / 'PREPARED-64.json').read_text())
assert set(previous['selected_modules']).issubset(selected)
for name in previous['selected_modules']:
    assert record['source_sha256'][name] == previous['source_sha256'][name], name
for name in ['launch.py', 'check_kernel.py', 'audit.py', 'BASE-MODULES.json', 'ROOTS.json']:
    assert record['driver_sha256'][name] == previous['driver_sha256'][name], name
assert len(selected) == 126 and len(roster) == 313
record['scope_from64'] = {
    'previous_selected_sources_unchanged': len(previous['selected_modules']),
    'added_selected_modules': [name for name in selected if name not in previous['selected_modules']],
    'unchanged_endpoint': 'NativeRefinementTarget.ProjectionTarget',
    'old_endpoint_preserved': 'NativeRefinementTarget.ReverseTarget',
    'all_actual_audits_and_kernel_checks_pending': True,
}
output = root / 'PREPARED-65.json'
if output.exists():
    assert json.loads(output.read_text()) == record
else:
    output.write_text(json.dumps(record, indent=2) + '\n')
print(json.dumps({'status': 'PASS', 'modules': len(selected), 'cached': len(base), 'audit_roots': len(roster), 'transported_unchanged': len(transport), 'launched': False}))
