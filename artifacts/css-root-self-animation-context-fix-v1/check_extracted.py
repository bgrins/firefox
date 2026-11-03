import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
SOURCE = HERE / 'candidate/servo/ports/geckolib/glue.rs'
text = SOURCE.read_text()
start = text.index("fn create_context_for_animation<'a>(")
end = text.index('\nstruct PropertyAndIndex', start)
helper = text[start:end].strip()
expressions = {}
for name in ('Servo_GetComputedKeyframeValues', 'Servo_GetAnimationValues', 'Servo_AnimationValue_Compute'):
    section = text[text.index('fn ' + name + '('):]
    call = section[section.index('let mut context = create_context_for_animation('):]
    call = call[:call.index(');')]
    matches = re.findall(r'^        (element\.is_root\(\).*),$', call, re.M)
    assert len(matches) == 1
    expressions[name] = matches[0]
section = text[text.index("impl<'a> ContextForSubstitution<'a>"):]
expressions['substitution'] = re.search(r'^            (self\.element\.is_root\(\).*),$', section, re.M)[1]
prefix = r'''
#![allow(dead_code)]
struct Device;
struct Stylist { device: Device }
impl Stylist { fn device(&self) -> &Device { &self.device } fn quirks_mode(&self) {} }
struct PerDocumentStyleDataImpl { stylist: Stylist }
struct ComputedValues { sentinel: u8 }
struct RuleCacheConditions;
struct ContainerSizeQuery<'a>(&'a ());
trait ElementContext {}
struct TreeCountingCaches;
struct StyleBuilder<'a> { is_root_element: bool, source: &'a ComputedValues, parent: Option<&'a ComputedValues> }
impl<'a> StyleBuilder<'a> {
    fn for_derived_style(_: &'a Device, _: Option<&'a Stylist>, style: &'a ComputedValues, parent: Option<&'a ComputedValues>) -> Self {
        Self { is_root_element: false, source: style, parent }
    }
}
struct Context<'a> { builder: StyleBuilder<'a>, smil: bool }
impl<'a> Context<'a> {
    fn new_for_animation(builder: StyleBuilder<'a>, smil: bool, _: (), _: &'a mut RuleCacheConditions, _: ContainerSizeQuery<'a>, _: &'a dyn ElementContext, _: &'a mut TreeCountingCaches) -> Self { Self { builder, smil } }
}
#[derive(Clone, Copy)]
struct Element { root: bool }
impl Element { fn is_root(&self) -> bool { self.root } }
impl ElementContext for Element {}
struct Substitution { element: Element, is_pseudo: bool }
'''
wrappers = 'fn keyframes(element: Element, pseudo: Option<()>) -> bool { ' + expressions['Servo_GetComputedKeyframeValues'] + ' }\n'
wrappers += 'fn direct(element: Element) -> bool { ' + expressions['Servo_AnimationValue_Compute'] + ' }\n'
wrappers += 'fn smil(element: Element) -> bool { ' + expressions['Servo_GetAnimationValues'] + ' }\n'
wrappers += 'impl Substitution { fn selected_root(&self) -> bool { ' + expressions['substitution'] + ' } }\n'
tests = r'''
fn apply(root: bool, smil: bool, parent_present: bool) -> (bool, bool, u8, bool) {
    let data = PerDocumentStyleDataImpl { stylist: Stylist { device: Device } };
    let style = ComputedValues { sentinel: 73 };
    let parent = ComputedValues { sentinel: 91 };
    let mut conditions = RuleCacheConditions;
    let mut caches = TreeCountingCaches;
    let element = Element { root };
    let context = create_context_for_animation(&data, &style, parent_present.then_some(&parent), root, smil, &mut conditions, ContainerSizeQuery(&()), &element, &mut caches);
    (context.builder.is_root_element, context.smil, context.builder.source.sentinel, context.builder.parent.is_some())
}
#[test] fn root_keyframes_supply_identity() {
    let root = Element { root: true };
    assert!(keyframes(root, None));
    assert_eq!(apply(keyframes(root, None), false, false), (true,false,73,false));
}
#[test] fn host_pseudo_is_not_root() {
    assert!(!keyframes(Element { root: true }, Some(())));
    assert_eq!(apply(keyframes(Element { root: true }, Some(())), false, true), (false,false,73,true));
}
#[test] fn substitution_retains_target_and_pseudo_identity() {
    assert!(Substitution { element: Element { root: true }, is_pseudo: false }.selected_root());
    assert!(!Substitution { element: Element { root: true }, is_pseudo: true }.selected_root());
    assert!(!Substitution { element: Element { root: false }, is_pseudo: false }.selected_root());
}
#[test] fn direct_and_smil_use_the_actual_element() {
    for root in [false,true] {
        assert_eq!(direct(Element { root }), root);
        assert_eq!(smil(Element { root }), root);
        assert_eq!(apply(smil(Element { root }),true,false), (root,true,73,false));
    }
}
#[test] fn parent_absence_does_not_make_a_detached_element_root() {
    assert!(!keyframes(Element { root: false },None));
    assert_eq!(apply(false,false,false),(false,false,73,false));
    assert_eq!(apply(false,false,true),(false,false,73,true));
}
'''
base = prefix + helper + '\n' + wrappers + tests
(HERE / 'EXTRACTED.rs').write_text(base)
mutations = {
    'missing_builder_identity': ('builder.is_root_element = is_root_element;', 'builder.is_root_element = false;'),
    'root_host_pseudo': ('element.is_root() && pseudo.is_none()', 'element.is_root()'),
    'substitution_host_pseudo': ('self.element.is_root() && !self.is_pseudo', 'self.element.is_root()'),
    'missing_direct_identity': ('fn direct(element: Element) -> bool { element.is_root() }', 'fn direct(element: Element) -> bool { false }'),
    'missing_smil_identity': ('fn smil(element: Element) -> bool { element.is_root() }', 'fn smil(element: Element) -> bool { false }'),
}
results = {}
with tempfile.TemporaryDirectory(prefix='css-root-self-extract-', dir='/private/tmp') as scratch:
    scratch_path = Path(scratch)
    for label, mutation in [('positive', None), *mutations.items()]:
        body = base
        if mutation:
            assert body.count(mutation[0]) == 1
            body = body.replace(*mutation)
        source = scratch_path / (label + '.rs')
        source.write_text(body)
        binary = scratch_path / label
        built = subprocess.run(['rustc', '--edition=2024', '--test', str(source), '-o', str(binary)], capture_output=True, text=True)
        (HERE / (label + '-compile.log')).write_text(built.stdout + built.stderr)
        assert built.returncode == 0
        ran = subprocess.run([str(binary)], capture_output=True, text=True)
        (HERE / (label + '-run.log')).write_text(ran.stdout + ran.stderr)
        assert ran.returncode == (0 if mutation is None else 101)
        results[label] = {'compile_exit': built.returncode, 'test_exit': ran.returncode}
assert not scratch_path.exists()
result = {'source_sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(), 'helper_exact': True, 'call_expressions': expressions, 'positive_tests': 5, 'compiled_false_controls': 5, 'results': results, 'scratch_removed': True, 'native_context_or_browser_test': False}
(HERE / 'EXTRACTED-CHECK.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result))
