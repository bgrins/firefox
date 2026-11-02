import hashlib,json,re,subprocess,tempfile,textwrap
from pathlib import Path
H=Path(__file__).resolve().parent
sha=lambda x:hashlib.sha256(x).hexdigest()
rustc=Path('/Users/bgrins/.rustup/toolchains/1.97.1-aarch64-apple-darwin/bin/rustc')
s=(H/'candidate/servo/components/style/properties/cascade.rs').read_text()
def block(a,b):return textwrap.dedent(s[s.index(a):s.index(b,s.index(a))])
def function(marker):
 start=s.index(marker);a=s.index('{',start);depth=1;i=a+1
 while depth:depth+=(s[i]=='{')-(s[i]=='}');i+=1
 return textwrap.dedent(s[start:i])
parts={
 'names':block('    #[derive(Clone, Eq, PartialEq, Debug)]\n    enum VarType','    enum ClosedValue'),
 'types':block('    enum ClosedValue','    /// Context struct for traversing'),
 'methods':block('        fn write_metric_diagnostic(','        fn map(&self)'),
 'walk':block('    #[derive(Clone, Copy, Eq, PartialEq)]\n    enum ReferenceReadiness','    /// Traverse a single dependency'),
 'algorithms':block('    fn visit_link<','    let mut context = Context'),
 'staged':block('struct PreparedMetricDeclaration {','#[derive(Clone, Copy, Debug, Eq, PartialEq)]\nenum ComputationStatus'),
 'drain':block('#[derive(Clone, Copy, Debug, Eq, PartialEq)]\nenum ComputationStatus','pub(crate) struct Cascade'),
 'target':block('#[derive(Clone, Copy, Debug)]\nenum FontTarget','struct PreparedMetricDeclaration'),
 'inventory':block('fn next_unprepared_font_input','#[derive(Clone, Copy, Debug)]\nenum FontTarget'),
 'completion':block('fn priority_has_dynamic_declarations','fn next_unprepared_font_input'),
 'ordinary_ensure':function('    fn refresh_priority_completion(')+function('    fn ensure_prioritary_property('),
 'ordinary_apply':function('    fn apply_one_prioritary_property('),
}
terminal = function('        if !matches!(result, VisitResult::Complete | VisitResult::CycleSettled) {')
terminal = terminal.replace('context.write_metric_diagnostic(', 'c.write_metric_diagnostic(').replace('&mut std::io::stderr().lock()', 'out')
parts['terminal'] = 'fn terminal_snapshot(c: &Context, out: &mut impl std::io::Write, result: VisitResult, diagnostic_progress: Option<MetricActionProgress>) {\n' + terminal + '\n}\n'
provider=(H/'candidate/servo/components/style/custom_properties.rs').read_text()
a=provider.index('/// Set of flags to references this custom property makes.');b=provider.index('/// A map from NonCustomReferenceMap to a T.',a)
parts['flags']=provider[a:b].replace(', MallocSizeOf, ToShmem','')
source=(H/'TestSupport.rs').read_text()+'\n'+parts['names']+parts['types']+parts['staged']+parts['drain']+parts['target']+parts['inventory']+parts['completion']+parts['flags']+'\nimpl Cascade<\'_>{\n'+parts['ordinary_ensure']+parts['ordinary_apply']+'}\nimpl Context<\'_,\'_>{\n'+parts['methods']+'}\n'+parts['walk']+parts['algorithms']+parts['terminal']+'\n'+(H/'Tests.rs').read_text()
source=re.sub(r"fn (\w+)<'a, 'b, 'c, 'd>",r'fn \1',source).replace("Context<'a, 'b, 'c, 'd>",'Context').replace('.entry_ref(name)', '.entry(name.clone())').replace('SmallVec::new()', 'Vec::new()')
def mutate(old,new):
 assert source.count(old)==1,(old,source.count(old))
 return source.replace(old,new,1)
