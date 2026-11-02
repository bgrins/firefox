import difflib
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = ROOT / 'artifacts/css-font-metric-synthesis-producer-v1/base/servo/components/style/properties/cascade.rs'
PIN = '5b7204f81c999516c617ac05ab619258eb18a05d628845cc1c424f8256013573'
sha = lambda b: hashlib.sha256(b).hexdigest()
source = SOURCE.read_bytes()
assert sha(source) == PIN
text = source.decode()
start = text.index('/// We track the index only for prioritary properties.')
end = text.index('\n#[derive(Default)]\nstruct RevertedSet', start)
body = text[start:end]
assert sha(body.encode()) == 'ee38718f9092c5159727aee1f42165c9bc530504ea8a31082ea7e9df9f8751e4'
HEADER = r'''
trait Array { type Item; }
impl<T, const N: usize> Array for [T; N] { type Item = T; }
type SmallVec<A> = Vec<<A as Array>::Item>;
mod property_counts { pub const PRIORITARY: usize = 1; }
#[derive(Clone, Copy)]
enum PropertyDeclaration { FontSize(u32), Color }
#[derive(Clone, Copy)]
enum LonghandId { FontSize, Color }
#[derive(Clone, Copy)]
enum PrioritaryPropertyId { FontSize }
impl PrioritaryPropertyId {
    fn from_longhand(id: LonghandId) -> Option<Self> {
        match id { LonghandId::FontSize => Some(Self::FontSize), LonghandId::Color => None }
    }
}
type CascadePriority = u8;
'''
FOOTER = r'''
fn main() {
    let args: Vec<String> = std::env::args().collect();
    let count: usize = args[1].parse().unwrap();
    let first = args[2] == "first";
    let font = PropertyDeclaration::FontSize(37);
    let color = PropertyDeclaration::Color;
    let mut declarations = Declarations::default();
    if first { declarations.note_declaration(&font, 0, LonghandId::FontSize); }
    for _ in 0..count { declarations.note_declaration(&color, 0, LonghandId::Color); }
    if !first { declarations.note_declaration(&font, 0, LonghandId::FontSize); }
    let expected: Vec<u32> = declarations.longhand_declarations.iter().filter_map(|entry| {
        match entry.decl { PropertyDeclaration::FontSize(value) => Some(*value), _ => None }
    }).collect();
    let mut indexed = Vec::new();
    let mut index = declarations.prioritary_positions[0].most_important;
    if index != DeclarationIndex::MAX {
        loop {
            let entry = declarations.longhand_declarations[index as usize];
            if let PropertyDeclaration::FontSize(value) = entry.decl { indexed.push(*value); }
            if entry.next_index == 0 { break; }
            assert!(entry.next_index > index);
            index = entry.next_index;
        }
    }
    assert_eq!(expected, vec![37]);
    println!("unrelated={count} position={} indexed={indexed:?} expected={expected:?}", args[2]);
    assert_eq!(indexed, expected, "unrelated properties must not remove the sole font-size declaration");
}
'''
assert body.count('type DeclarationIndex = u16;') == 1
wide = body.replace('type DeclarationIndex = u16;', 'type DeclarationIndex = u32;', 1)
variants = {
    'original': body,
    'widened': wide,
    'restored-limit-control': wide.replace('if new_index >= DeclarationIndex::MAX as usize', 'if new_index >= u16::MAX as usize', 1),
}
cases = [(0, 'last'), (65534, 'last'), (65535, 'last'), (65536, 'last'), (65536, 'first')]
output = HERE / 'run1'
output.mkdir()
results = []
rustc = shutil.which('rustc')
assert rustc
with tempfile.TemporaryDirectory(prefix='css-declaration-capacity-', dir='/private/tmp') as tmp:
    scratch = Path(tmp)
    for name, implementation in variants.items():
        program = HEADER + implementation + FOOTER
        (output / (name + '.rs')).write_text(program)
        src = scratch / (name + '.rs')
        src.write_text(program)
        executable = scratch / name
        command = [rustc, '--edition=2024', '-O', '-A', 'dead_code', str(src), '-o', str(executable)]
        compile_result = subprocess.run(command, capture_output=True)
        (output / (name + '-compile.log')).write_bytes(compile_result.stdout + compile_result.stderr)
        assert compile_result.returncode == 0, name
        for count, position in cases:
            result = subprocess.run([str(executable), str(count), position], capture_output=True)
            filename = f'{name}-{count}-{position}.log'
            (output / filename).write_bytes(result.stdout + result.stderr)
            expected_pass = name == 'widened' or position == 'first' or count < 65535
            results.append({'variant': name, 'unrelated_declarations': count, 'position': position,
                            'exit': result.returncode, 'expected_pass': expected_pass, 'log': filename})
            assert (result.returncode == 0) == expected_pass, results[-1]
assert not scratch.exists()
patched = text.replace('type DeclarationIndex = u16;', 'type DeclarationIndex = u32;', 1)
(HERE / 'candidate.patch').write_text(''.join(difflib.unified_diff(text.splitlines(True), patched.splitlines(True),
    fromfile='a/servo/components/style/properties/cascade.rs', tofile='b/servo/components/style/properties/cascade.rs')))
report = {'source': str(SOURCE.relative_to(ROOT)), 'source_sha256': PIN,
          'extracted_body_sha256': sha(body.encode()), 'rustc': rustc,
          'rustc_version': subprocess.check_output([rustc, '--version']).decode().strip(),
          'cases': results, 'scratch_removed': True,
          'support_doubles': ['Vec storage for SmallVec', 'two-property enum and priority mapping', 'u8 CascadePriority'],
          'native_compilation': False, 'browser_execution': False, 'native_acceptance': False}
(output / 'RESULT.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps({'original_failures': 2, 'widened_passes': 5, 'restored_limit_failures': 2,
                  'native_compilation': False, 'browser_execution': False, 'scratch_removed': True}))
