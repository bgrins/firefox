from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
RUST = Path('/Users/bgrins/.rustup/toolchains/1.97.1-aarch64-apple-darwin/bin')

def run(args, cwd=None):
    result = subprocess.run([str(x) for x in args], cwd=cwd, capture_output=True, text=True)
    assert result.returncode == 0, (args, result.stdout, result.stderr)
    return result

roles = json.loads((HERE / 'SOURCE-ROLES.json').read_text())
for rel, row in roles.items():
    for path, expected in [(ROOT / row['source'], row['base_sha256']), (HERE / 'base' / rel, row['base_sha256']), (HERE / 'candidate' / rel, row['candidate_sha256'])]:
        assert hashlib.sha256(path.read_bytes()).hexdigest() == expected
    run([RUST / 'rustfmt', '--check', '--config-path', HERE / 'rustfmt.toml', HERE / 'candidate' / rel])

value = (HERE / 'candidate/servo/components/style/properties_and_values/value.rs').read_text()
start = value.index('    /// Whether computing this selected value')
end = value.index('    /// Convert a registered custom property', start)
method = value[start:end]
prelude = (HERE / 'classifier-types.rs').read_text()
tests = (HERE / 'classifier-tests.rs').read_text()
receipt = {'scope': 'Exact classifier method with substituted AST container/types; no native parser, Stylo type check, graph or CSS conformance proof', 'source_authentication': len(roles), 'syntax_files': len(roles), 'mutants': {}}
with tempfile.TemporaryDirectory(prefix='css-selected-color-check-') as tmp:
    tmp = Path(tmp)
    shutil.copytree(HERE / 'base', tmp / 'tree')
    run(['patch', '-p1', '-i', HERE / 'native.patch'], cwd=tmp / 'tree')
    for rel in roles:
        assert (tmp / 'tree' / rel).read_bytes() == (HERE / 'candidate' / rel).read_bytes()
    run(['patch', '-R', '-p1', '-i', HERE / 'native.patch'], cwd=tmp / 'tree')
    for rel in roles:
        assert (tmp / 'tree' / rel).read_bytes() == (HERE / 'base' / rel).read_bytes()
    source = prelude + '\nimpl SpecifiedValue {\n' + method + '\n}\n' + tests
    (tmp / 'classifier.rs').write_text(source)
    run([RUST / 'rustc', '--edition=2024', '--cfg', 'feature="gecko"', '--test', tmp / 'classifier.rs', '-o', tmp / 'classifier'])
    receipt['tests'] = run([tmp / 'classifier']).stdout
    mutants = {
        'all_colors_depend': ('Color::CurrentColor | Color::Absolute(_) | Color::InheritFromBodyQuirk => false', 'Color::CurrentColor | Color::Absolute(_) | Color::InheritFromBodyQuirk => true'),
        'drop_nested_origin': ('function.origin_color().is_some_and(color)', 'false'),
        'drop_image_set_items': ('set.items.iter().any(|item| image(&item.image))', 'false'),
        'drop_repeated_components': ('ValueInner::List(list) => list.components.iter().any(component)', 'ValueInner::List(list) => false'),
    }
    for name, (old, new) in mutants.items():
        assert source.count(old) == 1
        (tmp / 'mutant.rs').write_text(source.replace(old, new))
        run([RUST / 'rustc', '--edition=2024', '--cfg', 'feature="gecko"', '--test', tmp / 'mutant.rs', '-o', tmp / 'mutant'])
        result = subprocess.run([str(tmp / 'mutant')], capture_output=True, text=True)
        assert result.returncode != 0
        receipt['mutants'][name] = {'exit': result.returncode, 'output': result.stdout}
    receipt['scratch'] = str(tmp)
assert not Path(receipt['scratch']).exists()
receipt['scratch_removed'] = True
(HERE / 'STATIC-CHECK.json').write_text(json.dumps(receipt, indent=2)+'\n')
print(json.dumps(receipt, indent=2))
