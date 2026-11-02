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
provider=(H/'candidate/servo/components/style/custom_properties.rs').read_text()
a=provider.index('/// Set of flags to references this custom property makes.');b=provider.index('/// A map from NonCustomReferenceMap to a T.',a)
parts['flags']=provider[a:b].replace(', MallocSizeOf, ToShmem','')
source=(H/'TestSupport.rs').read_text()+'\n'+parts['names']+parts['types']+parts['staged']+parts['drain']+parts['target']+parts['inventory']+parts['completion']+parts['flags']+'\nimpl Cascade<\'_>{\n'+parts['ordinary_ensure']+parts['ordinary_apply']+'}\nimpl Context<\'_,\'_>{\n'+parts['methods']+parts['actual_context_apply']+'}\n'+parts['walk']+parts['algorithms']+'\n'+(H/'Tests.rs').read_text()
source=re.sub(r"fn (\w+)<'a, 'b, 'c, 'd>",r'fn \1',source).replace("Context<'a, 'b, 'c, 'd>",'Context').replace('.entry_ref(name)', '.entry(name.clone())').replace('SmallVec::new()', 'Vec::new()')
def mutate(old,new):
 assert source.count(old)==1,(old,source.count(old))
 return source.replace(old,new,1)
variants={'positive':source,
 'foreign_boundary_as_css_edge':mutate('Err(VisitResult::SemanticOpen(index)) if index < semantic_floor =>', 'Err(VisitResult::SemanticOpen(index)) if false && index < semantic_floor =>').replace('if *index < semantic_floor {','if false && *index < semantic_floor {'),
 'foreign_saved_reply_consumed':mutate('if *index < semantic_floor {','if false && *index < semantic_floor {'),
 'nested_action_overwrites_outer':mutate('if depth == 0 {','if true {'),
 'side_completion_loses_root':mutate('if self.frames.len() == depth {\n                    return result;','if self.frames.len() == depth {\n                    self.frame_root = None;\n                    return result;'),
 'wrong_consumer_property':mutate('Some(state.value.substitution_property_id(state.longhand))','None'),
 'ignore_post_walk_flags':mutate('|| state.flags != self.computed_context.included_cascade_flags\n        })','|| false\n        })'),
 'skip_actual_reference_walk':mutate('let complete = loop {','let complete = loop { break true;'),
 'ignore_local_rollback':mutate('state.revert.is_some_and(|(priority, kind)|','false && state.revert.is_some_and(|(priority, kind)|'),
    'ignore_ordinary_claim':mutate('if completion.claimed.contains(id) || completion.active.contains(id) {\n        return ComputationStatus::Pending;','if completion.active.contains(id) {\n        return ComputationStatus::Pending;'),
    'fresh_ordinary_ledger':mutate('        self.priority_completion,\n    )','        &mut PriorityCompletion::default(),\n    )'),
    'early_ensured_bit':mutate('completion.active.insert(id);\n    let deps = id.dependencies();','completion.active.insert(id);\n    self.ensured_prioritary.insert(id);\n    let deps = id.dependencies();'),
    'lose_active_unwind':mutate('completion.active.remove(id);\n            return ComputationStatus::Pending;','return ComputationStatus::Pending;'),
    'consume_pending_payload':mutate('if self.apply_prioritary_property(id, attr_tracker) == ComputationStatus::Pending {\n            return ComputationStatus::Pending;','if self.apply_prioritary_property(id, attr_tracker) == ComputationStatus::Pending {\n            self.var_info[index].publication.take_ready(true).unwrap();\n            return ComputationStatus::Pending;'),
    'repeat_ordinary_application':mutate('if self.ensured_prioritary.contains(id) {\n        return ComputationStatus::Ready;','if false && self.ensured_prioritary.contains(id) {\n        return ComputationStatus::Ready;'),
}
records={}
with tempfile.TemporaryDirectory(prefix='metric-selected-reference-') as directory:
 scratch=Path(directory);lib=scratch/'libbitflags.rlib'
 bitflags=H.parents[1]/'third_party/rust/bitflags/src/lib.rs'
 library=subprocess.run([str(rustc),'--edition=2021','--crate-name','bitflags','--crate-type','rlib',str(bitflags),'-o',str(lib)],capture_output=True,text=True)
 assert library.returncode==0,library.stderr
 for name,body in variants.items():
  src=scratch/(name+'.rs');src.write_text(body);binary=scratch/name
  cmd=[str(rustc),'--edition=2024','-C','debug-assertions=no','--test',str(src),'--extern','bitflags='+str(lib),'-o',str(binary)]
  r=subprocess.run(cmd,capture_output=True,text=True);row={'source_sha256':sha(body.encode()),'compile_command':cmd,'compile_exit':r.returncode,'compile_stderr':r.stderr}
  if not r.returncode:
   v=subprocess.run([str(binary)],capture_output=True,text=True);row.update(run_exit=v.returncode,stdout=v.stdout,stderr=v.stderr)
  records[name]=row
report={'test_inputs_sha256':{name:sha((H/name).read_bytes()) for name in ['test.py','TestSupport.rs','Tests.rs']},'candidate_sha256':sha(s.encode()),'parts_sha256':{k:sha(v.encode()) for k,v in parts.items()},'provider_sha256':sha(provider.encode()),'rustc_sha256':sha(rustc.read_bytes()),'bitflags_sha256':sha(bitflags.read_bytes()),'scratch':str(scratch),'scratch_removed':not scratch.exists(),'records':records}
(H/'TEST-RESULT.json').write_text(json.dumps(report,indent=2)+'\n')
for name,row in records.items():
 assert row['compile_exit']==0,(name,row['compile_stderr'])
 assert (row['run_exit']==0)==(name=='positive'),(name,row)
print(json.dumps({'records':len(records),'positive':records['positive']['stdout'],'scratch_removed':not scratch.exists()}))
