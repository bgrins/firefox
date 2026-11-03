import ast,hashlib,json,re,subprocess,tempfile,textwrap
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
 'staged':block('fn size_input_prefix_is_stable(','#[derive(Clone, Copy, Debug, Eq, PartialEq)]\nenum ComputationStatus'),
 'drain':block('#[derive(Clone, Copy, Debug, Eq, PartialEq)]\nenum ComputationStatus','pub(crate) struct Cascade'),
 'target':block('#[derive(Clone, Copy, Debug)]\nenum FontTarget','fn size_input_prefix_is_stable('),
 'inventory':block('fn next_unprepared_font_input','#[derive(Clone, Copy, Debug)]\nenum FontTarget'),
 'completion':block('fn priority_has_dynamic_declarations','fn next_unprepared_font_input'),
 'ordinary_ensure':function('    fn refresh_priority_completion(')+function('    fn ensure_prioritary_property('),
 'ordinary_apply':function('    fn apply_one_prioritary_property('),
 'actual_context_apply':function('        fn apply_prioritary_property('),
}
final_loop = function('            for id in PrioritaryPropertyId::each() {')
parts['final_loop'] = "fn finish_ordinary(&mut self, context: &mut computed::Context, decls: &Declarations, shorthand_cache: &mut ShorthandsWithPropertyReferencesCache, attribute_tracker: &mut AttributeTracker, mut priority_completion: &mut PriorityCompletion) {\n" + final_loop + "\n}\n"
gecko_path=H.parents[1]/'servo/components/style/properties/gecko.mako.rs'
gecko=gecko_path.read_text()
assert sha(gecko.encode())=='dc1ed0998684fd252bd59eefe8b01dc9bdb7af02e93d61133adda2d0e3eba628'
def native_function(text,marker):
 start=text.index(marker);a=text.index('{',start);depth=1;i=a+1
 while depth:depth+=(text[i]=='{')-(text[i]=='}');i+=1
 return textwrap.dedent(text[start:i])
parts['font_set']=native_function(gecko,'    pub fn set_font_size(')
parts['font_unzoom']=native_function(gecko,'    pub fn unzoom_fonts(')
parts['unzoom_hook']=function('    fn unzoom_fonts_if_needed(')
hooks=(H/'HookSupport.rs').read_text().replace('__FONT_METHODS__',parts['font_set']+parts['font_unzoom']).replace('__UNZOOM_HOOK__',parts['unzoom_hook'])
provider=(H/'candidate/servo/components/style/custom_properties.rs').read_text()
a=provider.index('/// Set of flags to references this custom property makes.');b=provider.index('/// A map from NonCustomReferenceMap to a T.',a)
parts['flags']=provider[a:b].replace(', MallocSizeOf, ToShmem','')
source=(H/'TestSupport.rs').read_text()+'\n'+parts['names']+parts['types']+parts['staged']+parts['drain']+parts['target']+parts['inventory']+parts['completion']+parts['flags']+'\nimpl Cascade<\'_>{\n'+parts['ordinary_ensure']+parts['ordinary_apply']+parts['final_loop']+'}\nimpl Context<\'_,\'_>{\n'+parts['methods']+parts['actual_context_apply']+'}\n'+parts['walk']+parts['algorithms']+'\n'+hooks+'\n'+(H/'Tests.rs').read_text()
source=re.sub(r"fn (\w+)<'a, 'b, 'c, 'd>",r'fn \1',source).replace("Context<'a, 'b, 'c, 'd>",'Context').replace('.entry_ref(name)', '.entry(name.clone())').replace('SmallVec::new()', 'Vec::new()')
data_path = H.parents[1] / "servo/components/style/properties/data.py"
data_bytes = data_path.read_bytes()
assert sha(data_bytes) == "946b6ce730f8e79ea7ac4d7fc3c122b2922cdf37b38bf34d9ba9b02b84470d3d"
template = H.parents[1] / "servo/components/style/properties/properties.mako.rs"
assert sha(template.read_bytes()) == "9f76a0ffd6839178c95e4e260ef7ca10fd1b569fe051db7ead0a67bbf319bdd2"
assert "lambda dep, p=p: dep.name in PRIORITARY_PROPERTY_DEPENDENCIES[p.name]" in template.read_text()
tree = ast.parse(data_bytes)
dependencies = next(ast.literal_eval(n.value) for n in tree.body if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "PRIORITARY_PROPERTY_DEPENDENCIES" for t in n.targets))
names = {key: "".join(x.capitalize() for x in key.split("-")) for key in dependencies}
names["-x-lang"] = "XLang"
names["-x-text-scale"] = "XTextScale"
ids = list(names.values())
extras = ["FontSynthesisWeight", "FontSynthesisStyle", "FontSynthesisSmallCaps", "FontSynthesisPosition", "FontFeatureSettings"]
source = re.sub(r"pub enum LonghandId \{[^}]+\}", "pub enum LonghandId {" + ",".join(ids + extras) + "}", source, count=1)
source = re.sub(r"pub enum PrioritaryPropertyId \{[^}]+\}", "pub enum PrioritaryPropertyId {" + ",".join(ids) + "}", source, count=1)
source = source.replace("struct PrioritaryPropertyIdSet(u16)", "struct PrioritaryPropertyIdSet(u32)")
source = re.sub(r"let ids=\[[^;]+; let bits=", "let ids=[" + ",".join("PrioritaryPropertyId::" + x for x in ids) + "]; let bits=", source, count=1)
start = source.index("impl PrioritaryPropertyId {")
end = source.index("\nimpl LonghandId {", start)
impl = "impl PrioritaryPropertyId {\nfn to_longhand(self)->LonghandId {match self {" + ",".join("Self::" + x + "=>LonghandId::" + x for x in ids) + "}}\n"
impl += "fn from_longhand(id:LonghandId)->Option<Self>{match id {" + ",".join("LonghandId::" + x + "=>Some(Self::" + x + ")" for x in ids) + ",_=>None}}\n"
impl += "fn dependencies(self)-> &'static PrioritaryPropertyIdSet {match self {"
for key, value in dependencies.items():
    mask = sum(1 << ids.index(names[x]) for x in value)
    impl += "Self::" + names[key] + "=> &PrioritaryPropertyIdSet(" + str(mask) + "),"
impl += "}}\nfn each()->impl Iterator<Item=Self>{[" + ",".join("Self::"+x for x in ids) + "].into_iter()}\n}\n"
source = source[:start] + impl + source[end:]
source = source.replace("[DeclarationPosition;11]", f"[DeclarationPosition;{len(ids)}]").replace(" };11]", f" }};{len(ids)}]").replace(";11]",f";{len(ids)}]")

def mutate(old,new):
 assert source.count(old)==1,(old,source.count(old))
 return source.replace(old,new,1)
variants={'positive':source,
 'omit_logger_header':mutate('"CSS_METRIC_PENDING result={result:?}', '"OMITTED result={result:?}'),
 'wrong_facet_presence':mutate('self.priority_completion.computed_size.is_some(),\n        self.size_node,','false,\n        self.size_node,'),
}

records={}
with tempfile.TemporaryDirectory(prefix='sizeforms-diagnostic-', dir='/private/tmp') as directory:
 scratch=Path(directory);lib=scratch/'libbitflags.rlib'
 bitflags=H.parents[1]/'third_party/rust/bitflags/src/lib.rs'
 library=subprocess.run([str(rustc),'--edition=2021','--crate-name','bitflags','--crate-type','rlib',str(bitflags),'-o',str(lib)],capture_output=True,text=True)
 assert library.returncode==0,library.stderr
 dependency=H.parents[1]/'third_party/rust/stable_deref_trait/src/lib.rs'
 servo=H.parents[1]/'servo/components/servo_arc/lib.rs'
 for args in [
  [str(rustc),'--edition=2021','--crate-name','stable_deref_trait','--crate-type','rlib',str(dependency),'-o',str(scratch/'libstable_deref_trait.rlib')],
  [str(rustc),'--edition=2024','--crate-name','servo_arc','--crate-type','rlib',str(servo),'--extern','stable_deref_trait='+str(scratch/'libstable_deref_trait.rlib'),'-o',str(scratch/'libservo_arc.rlib')]]:
  compiled=subprocess.run(args,capture_output=True,text=True);assert compiled.returncode==0,compiled.stderr
 for name,body in variants.items():
  src=scratch/(name+'.rs');src.write_text(body);binary=scratch/name
  cmd=[str(rustc),'--edition=2024','-C','debug-assertions=no','--test',str(src),'--extern','bitflags='+str(lib),'--extern','servo_arc='+str(scratch/'libservo_arc.rlib'),'-L','dependency='+str(scratch),'-o',str(binary)]
  r=subprocess.run(cmd,capture_output=True,text=True);row={'source_sha256':sha(body.encode()),'compile_command':cmd,'compile_exit':r.returncode,'compile_stderr':r.stderr}
  if not r.returncode:
   v=subprocess.run([str(binary)],capture_output=True,text=True);row.update(run_exit=v.returncode,stdout=v.stdout,stderr=v.stderr)
  records[name]=row
report={'test_inputs_sha256':{name:sha((H/name).read_bytes()) for name in ['test.py','TestSupport.rs','Tests.rs','HookSupport.rs']},'candidate_sha256':sha(s.encode()),'parts_sha256':{k:sha(v.encode()) for k,v in parts.items()},'provider_sha256':sha(provider.encode()),'gecko_font_source_sha256':sha(gecko.encode()),'rustc_sha256':sha(rustc.read_bytes()),'bitflags_sha256':sha(bitflags.read_bytes()),'servo_arc_sha256':sha(servo.read_bytes()),'stable_deref_trait_sha256':sha(dependency.read_bytes()),'generated_dependencies':dependencies,'generated_data_sha256':sha(data_bytes),'scratch':str(scratch),'scratch_removed':not scratch.exists(),'records':records}
(H/'TEST-RESULT.json').write_text(json.dumps(report,indent=2)+'\n')
for name,row in records.items():
 assert row['compile_exit']==0,(name,row['compile_stderr'])
 assert (row['run_exit']==0)==(name=='positive'),(name,row)
print(json.dumps({'records':len(records),'positive':records['positive']['stdout'],'scratch_removed':not scratch.exists()}))
