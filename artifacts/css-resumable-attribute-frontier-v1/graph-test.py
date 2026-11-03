import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = HERE / 'candidate/servo/components/style/custom_properties.rs'
SUPPORT = ROOT / 'artifacts/css-variable-origin-proof-v2'
spec = importlib.util.spec_from_file_location('rust_reader', SUPPORT / 'native/rust_reader.py')
reader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reader)
source = BASE.read_text()
parts = {}


def full(marker, after=0):
    start = source.index(marker, after)
    tokens = reader.tokens(source[start:])
    brace = next(i for i, token in enumerate(tokens) if token[0] == '{')
    end = reader.pair(tokens, brace)
    text = source[start:start + tokens[end][2]]
    parts[marker] = hashlib.sha256(text.encode()).hexdigest()
    return text


code = (HERE / 'GraphBase.rs').read_text()
for marker, derive in [
    ('pub struct AttrTaintedRange {', 'Clone,Debug,PartialEq'),
    ('pub struct VariableValue {', 'Clone,Debug'),
    ('pub struct VariableFallback {', 'Clone,Debug'),
    ('pub struct SubstitutionFunctionReference {', 'Clone,Debug'),
    ('pub struct References {', 'Clone,Debug,Default'),
    ('pub enum SubstitutionFunctionKind {', 'Copy,Clone,Debug,PartialEq,Eq'),
    ('enum AttributeType {', 'Clone,Debug,PartialEq'),
    ('pub struct AttributeData {', 'Clone,Debug,PartialEq'),
    ("struct Substitution<'a> {", 'Debug,Default'),
    ("pub struct SubstitutionResult<'a> {", 'Debug'),
]:
    code += '\n#[derive(' + derive + ')]\n' + full(marker) + '\n'
code += '#[derive(Clone,Debug,Default)]\npub struct AttrTaint(SmallVec<[AttrTaintedRange; 1]>);\n'
for marker in ['impl AttrTaintedRange {', 'impl AttrTaint {', 'impl AttributeData {', 'impl SubstitutionFunctionReference {']:
    code += full(marker) + '\n'
code += '#[derive(Clone,Copy,Debug,Default,PartialEq,Eq)]\npub struct ReferenceFlags(u16);\n' + full('bitflags! {')
code += '\nimpl ReferenceFlags {\n' + full('    fn from_unit(value:') + '\n'+full('    pub fn for_each_non_custom<F>')+'\n}\n'
code += 'struct NoCalcLength;\nimpl NoCalcLength {\n'
length = (SUPPORT / 'source/length.rs').read_text()
for name in ['EM','EX','CH','CAP','IC','LH','REM','REX','RCH','RCAP','RIC','RLH']:
    found = re.findall(r"    pub const " + name + r": &'static str = \"[^\"]+\";", length)
    assert len(found) == 1
    code += found[0] + '\n'
code += '}\nimpl VariableValue {\n'
for marker in ['    fn empty(url_data:', '    pub fn new(\n        css: String,', '    fn push(\n', '    pub fn parse(\n', '    pub fn has_references(&self)']:
    code += full(marker) + '\n'
code += '}\nimpl References {\n' + full('    fn has_references(&self)', source.index('impl References {')) + '\n}\n'
for marker in ['pub fn parse_name(', 'fn parse_declaration_value(', 'fn parse_declaration_value_block(', 'fn parse_attr_type(', 'fn parse_attr_number', 'fn quoted_css_string(']:
    code += full(marker) + '\n'
start = source.index("impl<'a> Substitution<'a> {")
code += "impl<'a> Substitution<'a> {\n" + full('    fn from_value(', start) + '\n' + full('    fn new(', start) + '\n}\n'
cascade=(HERE/'candidate/servo/components/style/properties/cascade.rs').read_text()
def native_block(text,marker):
    start=text.index(marker);tokens=reader.tokens(text[start:]);brace=next(i for i,t in enumerate(tokens) if t[0]=='{');end=reader.pair(tokens,brace)
    body=text[start:start+tokens[end][2]];parts[marker]=hashlib.sha256(body.encode()).hexdigest();return body
code += source[source.index('#[derive(Clone, Copy, Debug, PartialEq)]\npub(crate) enum SubstitutionLookupKind'):]
code += (HERE/'GraphSupport.rs').read_text()
for marker in ['enum PreparedCustomKind {','pub(crate) struct PreparedCustomValue {','impl PreparedCustomValue {','pub(crate) fn prepare_completed_custom_value(','fn prepare_custom_substitution(','pub fn handle_invalid_at_computed_value_time(']:
    code += full(marker)+'\n'
for marker in ['    enum ClosedValue {','    enum NodePublication<T> {','    #[derive(Clone, Copy, Debug, Eq, PartialEq)]\n    enum NodeReadiness','    impl<T> NodePublication<T> {','    #[derive(Clone, Copy, Debug, Eq, PartialEq)]\n    enum VisitResult','    struct VarInfo {','    struct GuardedCustomFrame {']:
    code += native_block(cascade,marker)+'\n'
code += 'impl Context{\n'
for marker in ['        fn poll_frames(','        fn publish_closed(','        fn handle_loop(','        fn captured_environment(','        fn capture_attribute_input(','        fn owned_lookup_value(','        fn metric_action_is_current(','        fn resolve_metric_lookup_inner(']:
    code += native_block(cascade,marker)+'\n'
code += '}\nimpl TraversalFrame{\nfn accepts_computed_size(&self,_:bool)->bool{false}\n'
for marker in ['        fn enter_guarded_custom(','        fn guarded_references(','        fn link(','        fn receive(']:code+=native_block(cascade,marker)+'\n'
code += (HERE/'GraphStep.rs').read_text().replace('CLOSE_BODY',native_block(cascade,'                    FramePhase::Close => {')).replace('UNITS_BODY',native_block(cascade,'                    FramePhase::Units => {'))
code += '}\ntype LonghandId=u8;\n'+(HERE/'GraphTests.rs').read_text()
(HERE/'GRAPH-EXTRACTED.rs').write_text(code)
def changed(old,new):
    assert code.count(old)==1,(old,code.count(old))
    return code.replace(old,new,1)
variants={
 'positive':code,
 'shared_marks_lost':changed('guards: self.guards.clone(),','guards: self.guards.iter().map(|g| SubstitutionGuard::new(g.key.clone())).collect(),'),
 'entry_ancestry_lost':changed('frame.enter_guarded_custom(state.request.guards.clone(), self);','frame.enter_guarded_custom(Vec::new(), self);'),
 'completed_body_discarded':changed('self.prepared_custom = Some(prepared);','self.prepared_custom = None; drop(prepared);'),
 'registered_units_lost':changed('self.value_non_custom_refs |= flags;','let _ = flags;'),
 'generation_guard_lost':changed('|| !Arc::ptr_eq(&state.generation, &context.lookup_bindings.root)','|| false'),
 'flags_guard_lost':changed('state.flags != context.computed_context.included_cascade_flags','false'),
 'foreign_floor_lost':code.replace('*index < semantic_floor','false').replace('index < semantic_floor','false'),
}
rustc = Path('/Users/bgrins/.rustup/toolchains/1.97.1-aarch64-apple-darwin/bin/rustc')
records = []
result_path = HERE / (sys.argv[1] if len(sys.argv) > 1 else 'TEST-GRAPH.json')


def run(command):
    r = subprocess.run(command, capture_output=True, text=True, timeout=120)
    records.append({'command': [str(x) for x in command], 'exit': r.returncode, 'stdout': r.stdout, 'stderr': r.stderr})
    result_path.write_text(json.dumps({'records': records}, indent=2) + '\n')
    return r


with tempfile.TemporaryDirectory(prefix='resumable-substitution-', dir='/private/tmp') as temporary:
    scratch = Path(temporary)
    try:
        for name, edition, dependencies in [('dtoa','2015',[]),('dtoa-short','2015',['dtoa']),('itoa','2018',[]),('smallvec','2018',[]),('bitflags','2021',[]),('cssparser','2024',['dtoa-short','itoa','smallvec'])]:
            crate = name.replace('-', '_')
            cmd = [rustc, '--crate-name', crate, '--crate-type', 'rlib', '--edition', edition, '-L', 'dependency=' + str(scratch), SUPPORT / 'vendor' / name / 'src/lib.rs', '-o', scratch / ('lib' + crate + '.rlib')]
            for dependency in dependencies:
                dependency = dependency.replace('-', '_')
                cmd += ['--extern', dependency + '=' + str(scratch / ('lib' + dependency + '.rlib'))]
            assert run(cmd).returncode == 0, records[-1]
        for crate, path, edition, deps in [
            ('stable_deref_trait', ROOT / 'third_party/rust/stable_deref_trait/src/lib.rs', '2021', []),
            ('servo_arc', ROOT / 'servo/components/servo_arc/lib.rs', '2024', ['stable_deref_trait']),
        ]:
            cmd = [rustc, '--crate-name', crate, '--crate-type', 'rlib', '--edition', edition, path, '-o', scratch / ('lib' + crate + '.rlib')]
            for dependency in deps:
                cmd += ['--extern', dependency + '=' + str(scratch / ('lib' + dependency + '.rlib'))]
            assert run(cmd).returncode == 0, records[-1]
        for name, body in variants.items():
            path = scratch / (name + '.rs');path.write_text(body)
            cmd = [rustc, '--test', '--edition', '2024', '-C', 'debug-assertions=yes', '-L', 'dependency=' + str(scratch), path, '-o', scratch / name]
            for dependency in ['cssparser','bitflags','smallvec','servo_arc']:
                cmd += ['--extern', dependency + '=' + str(scratch / ('lib' + dependency + '.rlib'))]
            assert run(cmd).returncode == 0, records[-1]
            records[-1].update(variant=name, source_sha256=hashlib.sha256(body.encode()).hexdigest())
            result = run([scratch / name, '--nocapture'])
            records[-1]['variant'] = name
            assert (result.returncode == 0) == (name == 'positive'), records[-1]
            if name != 'positive':
                assert 'test result: FAILED' in result.stdout
    finally:
        result_path.write_text(json.dumps({'records': records, 'parts': parts, 'source_sha256': hashlib.sha256(source.encode()).hexdigest(), 'extracted_sha256': hashlib.sha256(code.encode()).hexdigest(), 'scratch': str(scratch), 'test_inputs': {n: hashlib.sha256((HERE/n).read_bytes()).hexdigest() for n in ['graph-test.py','GraphBase.rs','GraphSupport.rs','GraphStep.rs','GraphTests.rs']}, 'rustc_sha256': hashlib.sha256(rustc.read_bytes()).hexdigest()}, indent=2) + '\n')
assert not scratch.exists()
report = json.loads(result_path.read_text());report['scratch_removed'] = True
result_path.write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps({'compiled_variants':len(variants),'scratch_removed':True}))
