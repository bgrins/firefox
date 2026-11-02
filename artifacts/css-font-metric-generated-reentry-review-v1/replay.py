import hashlib,json,re,subprocess,tempfile,textwrap
from pathlib import Path
H=Path(__file__).resolve().parent
P=H.parent/'css-font-metric-selected-reference-producer-v1'
sha=lambda x:hashlib.sha256(x).hexdigest()
rustc=Path('/Users/bgrins/.rustup/toolchains/1.97.1-aarch64-apple-darwin/bin/rustc')
s=(P/'candidate/servo/components/style/properties/cascade.rs').read_text()
def block(a,b):return textwrap.dedent(s[s.index(a):s.index(b,s.index(a))])
def function(marker):
 start=s.index(marker);a=s.index('{',start);depth=1;i=a+1
 while depth:depth+=(s[i]=='{')-(s[i]=='}');i+=1
 return textwrap.dedent(s[start:i])
parts={
 'names':block('    #[derive(Clone, Eq, PartialEq, Debug)]\n    enum VarType','    enum ClosedValue'),
 'types':block('    enum ClosedValue','    /// Context struct for traversing'),
 'methods':block('        fn reset(&mut self)','        fn map(&self)'),
 'walk':block('    #[derive(Clone, Copy, Eq, PartialEq)]\n    enum ReferenceReadiness','    /// Traverse a single dependency'),
 'algorithms':block('    fn visit_link<','    let mut context = Context'),
 'staged':block('struct PreparedMetricDeclaration {','#[derive(Clone, Copy, Debug, Eq, PartialEq)]\nenum ComputationStatus'),
 'drain':block('#[derive(Clone, Copy, Debug, Eq, PartialEq)]\nenum ComputationStatus','pub(crate) struct Cascade'),
 'target':block('#[derive(Clone, Copy, Debug)]\nenum FontTarget','struct PreparedMetricDeclaration'),
 'inventory':block('fn next_unprepared_font_input','#[derive(Clone, Copy, Debug)]\nenum FontTarget'),
 'completion':block('fn priority_has_dynamic_declarations','fn next_unprepared_font_input'),
 'ordinary_ensure':function('    fn refresh_priority_completion(')+function('    fn ensure_prioritary_property('),
 'ordinary_apply':function('    fn apply_one_prioritary_property('),
 'actual_context_apply':function('        fn apply_prioritary_property('),
}
provider=(P/'candidate/servo/components/style/custom_properties.rs').read_text()
a=provider.index('/// Set of flags to references this custom property makes.');b=provider.index('/// A map from NonCustomReferenceMap to a T.',a)
parts['flags']=provider[a:b].replace(', MallocSizeOf, ToShmem','')
source=(H/'TestSupport.rs').read_text()+'\n'+parts['names']+parts['types']+parts['staged']+parts['drain']+parts['target']+parts['inventory']+parts['completion']+parts['flags']+'\nimpl Cascade<\'_>{\n'+parts['ordinary_ensure']+parts['ordinary_apply']+'}\nimpl Context<\'_,\'_>{\n'+parts['methods']+parts['actual_context_apply']+'}\n'+parts['walk']+parts['algorithms']+'\n'+(H/'Tests.rs').read_text()
source=re.sub(r"fn (\w+)<'a, 'b, 'c, 'd>",r'fn \1',source).replace("Context<'a, 'b, 'c, 'd>",'Context').replace('.entry_ref(name)', '.entry(name.clone())').replace('SmallVec::new()', 'Vec::new()')

def mutate(old,new):
 assert source.count(old)==1,(old,source.count(old))
 return source.replace(old,new,1)
variants={
 'positive':source,
 'remove_weight_generated_edge':mutate(' | (1 << PrioritaryPropertyId::FontWeight as u8)',''),
 'old_context_apply_stub':mutate(parts['actual_context_apply'],"fn apply_prioritary_property(&mut self,id:PrioritaryPropertyId,_:&mut AttributeTracker){self.cascade.completed_prioritary.insert(id);}"),
 'certify_dynamic_ordinary_completion':mutate('&& !priority_has_dynamic_declarations(decls, id)','&& true'),
}
records={}
with tempfile.TemporaryDirectory(prefix='metric-generated-reentry-') as directory:
 scratch=Path(directory);lib=scratch/'libbitflags.rlib'
 bitflags=H.parents[1]/'third_party/rust/bitflags/src/lib.rs'
 library=subprocess.run([str(rustc),'--edition=2021','--crate-name','bitflags','--crate-type','rlib',str(bitflags),'-o',str(lib)],capture_output=True,text=True)
 assert library.returncode==0,library.stderr
 for name,body in variants.items():
  src=scratch/(name+'.rs');src.write_text(body);binary=scratch/name
  cmd=[str(rustc),'--edition=2024','-C','debug-assertions=no','--test',str(src),'--extern','bitflags='+str(lib),'-o',str(binary)]
  r=subprocess.run(cmd,capture_output=True,text=True);row={'source_sha256':sha(body.encode()),'compile_command':cmd,'compile_exit':r.returncode,'compile_stderr':r.stderr}
  if not r.returncode:
   v=subprocess.run([str(binary),'--nocapture'],capture_output=True,text=True);row.update(run_exit=v.returncode,stdout=v.stdout,stderr=v.stderr)
  records[name]=row
report={'test_inputs_sha256':{name:sha((H/name).read_bytes()) for name in ['replay.py','TestSupport.rs','Tests.rs']},'candidate_sha256':sha(s.encode()),'parts_sha256':{k:sha(v.encode()) for k,v in parts.items()},'provider_sha256':sha(provider.encode()),'rustc_sha256':sha(rustc.read_bytes()),'bitflags_sha256':sha(bitflags.read_bytes()),'scratch':str(scratch),'scratch_removed':not scratch.exists(),'records':records}
(H/'RESULT.json').write_text(json.dumps(report,indent=2)+'\n')
for name,row in records.items():
 assert row['compile_exit']==0,(name,row['compile_stderr'])
 assert (row['run_exit']==0)==(name=='positive'),(name,row)
print(json.dumps({'records':len(records),'positive':records['positive']['stdout'],'scratch_removed':not scratch.exists()}))
