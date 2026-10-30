from pathlib import Path
import difflib
import hashlib
import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
spec = importlib.util.spec_from_file_location('composition', HERE / 'generate.py')
g = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g)
roles = json.loads((HERE / 'SOURCE-ROLES.json').read_bytes())

for parent, digest in [(g.V3, '832d247da7050b1038bcf1b96a8fa72fa2cef9f63c2f514da37fc182de9cfbc6'),
                       (g.A, '8c9697943910f1c90341e6a24d5d5e447e052123fda96e7c7f8d60e5db67e740')]:
    assert sha(parent / 'FILES.json') == digest
    for name, row in json.loads((parent / 'FILES.json').read_bytes()).items():
        assert sha(parent / name) == row['sha256'] and (parent / name).stat().st_size == row['bytes']
for row in json.loads((HERE / 'REFERENCES.json').read_bytes()):
    assert sha(ROOT / row['path']) == row['sha256']
assert sha(g.FORMAT) == 'ab19d01d0a7a3a901c62b6b013a98452d38084b5d7f446ccb20c5e83c10db99f'
assert (HERE / 'rustfmt.toml').read_bytes() == (g.A / 'rustfmt.toml').read_bytes()
v3 = (g.V3 / 'candidate' / g.REL).read_text()
source = (g.A / 'candidate' / g.REL).read_text()
merged = (HERE / 'candidate' / g.REL).read_text()
result = subprocess.run([str(g.FORMAT), '--emit', 'stdout', '--config-path', str(HERE / 'rustfmt.toml')],
                        input=g.compose(v3, source), capture_output=True, text=True)
assert result.returncode == 0 and not result.stderr and result.stdout == merged
marker = '        } else if let VarType::NonCustom(longhand) = var {'
assert g.span(v3, marker, '        context.var_info[index].lowlink = lowlink;') == g.span(
    merged, marker, '        if let VarType::Custom(ref name) = var {\n            let cyclic')
assert g.span(v3, '        // This is the root of a strong-connected component.', '        // Not in a loop, apply the value.') == g.span(
    merged, '        // This is the root of a strong-connected component.', '        // Not in a loop, apply the value.')
assert g.span(v3, 'fn find_non_custom_references(', '/// Resolves the custom properties') == g.span(
    merged, 'fn find_non_custom_references(', '/// Resolves the custom properties')
assert 'may_reference_image' not in merged
for rel, row in roles.items():
    for pin in row.values():
        assert sha(ROOT / pin['path']) == pin['sha256']
    if rel != g.REL:
        assert row['candidate']['sha256'] == row['color_only']['sha256']
    result = subprocess.run([str(g.FORMAT), '--check', '--config-path', str(HERE / 'rustfmt.toml'), str(HERE / 'candidate' / rel)], capture_output=True, text=True)
    assert result.returncode == 0 and not result.stderr
for name, key in [('native.patch', 'base'), ('V3-DELTA.patch', 'v3'), ('A-DELTA.patch', 'color_only')]:
    expected = []
    for rel, row in roles.items():
        before, after = ROOT / row[key]['path'], ROOT / row['candidate']['path']
        expected.extend(difflib.unified_diff(before.read_text().splitlines(True), after.read_text().splitlines(True), fromfile='a/' + rel, tofile='b/' + rel))
    assert (HERE / name).read_text() == ''.join(expected)
    with tempfile.TemporaryDirectory(prefix='css-selection-color-compose-') as temporary:
        tree = Path(temporary)
        for rel, row in roles.items():
            target = tree / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / row[key]['path'], target)
        for reverse in [False, True]:
            command = ['patch'] + (['-R'] if reverse else []) + ['-p1', '-i', str(HERE / name)]
            result = subprocess.run(command, cwd=tree, capture_output=True, text=True)
            assert result.returncode == 0, result
            for rel, row in roles.items():
                assert sha(tree / rel) == row[key if reverse else 'candidate']['sha256']
    assert not tree.exists()
print(json.dumps({'source_pairs': 3, 'exact_parent_and_base_deltas': 3, 'patch_roundtrips': 3,
                  'formatted_files': 3, 'v3_priority_selection_and_scc_publication_unchanged': True,
                  'original_COLOR_admission_unchanged': True, 'pure_image_eligibility_added': False,
                  'provider_value_exact_A': True, 'scratch_removed': True,
                  'native_compile': False, 'browser_execution': False, 'composition_semantics_proven': False}))
