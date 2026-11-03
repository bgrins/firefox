import hashlib, json, shutil, subprocess, tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
data = (HERE / 'candidate/servo/components/style/data.rs').read_text()
traversal = (HERE / 'candidate/servo/components/style/traversal.rs').read_text()
start = data.index('fn needs_to_recascade_self(')
end = data.index('\nimpl ElementData', start)
predicate = data[start:end]
start = traversal.index('    let has_animations = !flags.for_animation_only()')
end = traversal.index('    let restyle_kind = ', start)
query = traversal[start:end]
assert data.count('needs_to_recascade_self(hint, style, has_animations)') == 1
assert data.count('needs_to_recascade_self(hint, style, false)') == 1
assert traversal.count('data.restyle_kind(context.shared, has_animations)') == 1
prelude = r'''
use std::cell::Cell;
#[derive(Clone, Copy)] struct Bits(u8);
impl Bits {
    const RECASCADE_SELF: Self = Self(1);
    const RECASCADE_SELF_IF_INHERIT_RESET_STYLE: Self = Self(2);
    const RESTYLE_IF_AFFECTED_BY_WM_OR_ANCESTOR_FONT: Self = Self(4);
    const INHERITS_RESET_STYLE: Self = Self(2);
    const USES_FONT_OR_WM_RELATIVE_UNITS: Self = Self(4);
    fn intersects(self, other: Self) -> bool { self.0 & other.0 != 0 }
    fn contains(self, other: Self) -> bool { self.0 & other.0 == other.0 }
}
type RestyleHint = Bits;
type ComputedValueFlags = Bits;
struct ComputedValues { flags: Bits }
struct Data { hint: Bits }
struct Flags(bool);
impl Flags { fn for_animation_only(&self) -> bool { self.0 } }
struct Context { shared: () }
struct Element { calls: Cell<u32>, relevant: Cell<bool> }
impl Element {
    fn has_animations(&self, _: ()) -> bool {
        self.calls.set(self.calls.get() + 1);
        self.relevant.get()
    }
}
'''
tests = r'''
#[test] fn animated_target_without_style_bit_is_admitted() {
    let style = ComputedValues { flags: Bits(0) };
    assert!(needs_to_recascade_self(Bits(4), &style, true));
    assert!(!needs_to_recascade_self(Bits(4), &style, false));
}
#[test] fn ordinary_relative_and_other_recascade_paths_survive() {
    assert!(needs_to_recascade_self(Bits(4), &ComputedValues { flags: Bits(4) }, false));
    assert!(needs_to_recascade_self(Bits(1), &ComputedValues { flags: Bits(0) }, false));
    assert!(needs_to_recascade_self(Bits(2), &ComputedValues { flags: Bits(2) }, false));
    assert!(!needs_to_recascade_self(Bits(2), &ComputedValues { flags: Bits(0) }, true));
    assert!(!needs_to_recascade_self(Bits(0), &ComputedValues { flags: Bits(4) }, true));
}
#[test] fn query_requires_normal_pass_and_font_hint() {
    let element = Element { calls: Cell::new(0), relevant: Cell::new(true) };
    let context = Context { shared: () };
    assert!(!query(&Data { hint: Bits(0) }, &Flags(false), &element, &context));
    assert!(!query(&Data { hint: Bits(4) }, &Flags(true), &element, &context));
    assert_eq!(element.calls.get(), 0);
    assert!(query(&Data { hint: Bits(4) }, &Flags(false), &element, &context));
    assert_eq!(element.calls.get(), 1);
}
#[test] fn membership_is_requeried_after_removal_and_retarget() {
    let element = Element { calls: Cell::new(0), relevant: Cell::new(true) };
    let context = Context { shared: () };
    let data = Data { hint: Bits(4) };
    assert!(query(&data, &Flags(false), &element, &context));
    element.relevant.set(false);
    assert!(!query(&data, &Flags(false), &element, &context));
    element.relevant.set(true);
    assert!(query(&data, &Flags(false), &element, &context));
    assert_eq!(element.calls.get(), 3);
}
'''
source = prelude + predicate + '\nfn query(data: &Data, flags: &Flags, element: &Element, context: &Context) -> bool {\n' + query + 'has_animations\n}\n' + tests
variants = {
    'positive': source,
    'omit_animation_admission': source.replace('has_animations\n            || style', 'false\n            || style'),
    'omit_ordinary_dependency': source.replace('has_animations\n            || style\n                .flags\n                .contains(ComputedValueFlags::USES_FONT_OR_WM_RELATIVE_UNITS)', 'has_animations'),
    'query_animation_only': source.replace('!flags.for_animation_only()', 'true'),
    'omit_hint_gate': source.replace('hint.intersects(RestyleHint::RESTYLE_IF_AFFECTED_BY_WM_OR_ANCESTOR_FONT)', 'true'),
}
scratch = Path(tempfile.mkdtemp(prefix='css-keyframe-font-unit-extracted-'))
results = {}
try:
    for name, text in variants.items():
        if name != 'positive': assert text != source
        rust = scratch / (name + '.rs')
        binary = scratch / name
        rust.write_text(text)
        compile_result = subprocess.run(['rustc', '--edition=2024', '--test', str(rust), '-o', str(binary)], capture_output=True, text=True)
        (HERE / (name + '-compile.log')).write_text(compile_result.stdout + compile_result.stderr)
        assert compile_result.returncode == 0
        run = subprocess.run([str(binary)], capture_output=True, text=True)
        (HERE / (name + '-run.log')).write_text(run.stdout + run.stderr)
        assert run.returncode == (0 if name == 'positive' else 101)
        results[name] = {'compile': compile_result.returncode, 'run': run.returncode}
finally:
    shutil.rmtree(scratch)
(HERE / 'EXTRACTED.rs').write_text(source)
result = {'results': results, 'scratch': str(scratch), 'scratch_removed': not scratch.exists(),
          'native_compilation': False, 'scope': 'Exact predicate and query; flags and effect membership are explicit doubles, not Gecko lifetime validation',
          'inputs': {str(p.relative_to(HERE)): hashlib.sha256(p.read_bytes()).hexdigest() for p in [HERE / 'candidate/servo/components/style/data.rs', HERE / 'candidate/servo/components/style/traversal.rs', HERE / 'check_extracted.py']}}
(HERE / 'EXTRACTED-CHECK.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
