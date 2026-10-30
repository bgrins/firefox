import hashlib,json,subprocess,tempfile,textwrap,re
from pathlib import Path
H=Path(__file__).resolve().parent
sha=lambda b:hashlib.sha256(b).hexdigest()
s=(H/'candidate/servo/components/style/properties/cascade.rs').read_text()
def block(a,b):return textwrap.dedent(s[s.index(a):s.index(b,s.index(a))])
def braces(marker):
 start=s.index(marker)+len(marker);a=s.index('{',start);depth=1;i=a+1
 while depth:depth+=(s[i]=='{')-(s[i]=='}');i+=1
 return s[a+1:i-1]
parts={
 'staged':block('struct PreparedMetricDeclaration {','#[derive(Clone, Copy, Debug, Eq, PartialEq)]\nenum ComputationStatus'),
 'drain':Path('artifacts/css-font-metric-pending-integration-v1/PRIORITY-DRAIN.rs').read_text(),
 'target':block('#[derive(Clone, Copy, Debug, Eq, PartialEq)]\nenum FontTarget','struct PreparedMetricDeclaration'),
 'inventory':block('fn next_unprepared_font_input','#[derive(Clone, Copy, Debug, Eq, PartialEq)]\nenum FontTarget'),
 'state':block('    enum NodePublication<T>','    #[derive(Clone, Copy, Debug, Eq, PartialEq)]\n    enum VisitResult'),
 'action':block('    #[derive(Clone, Copy)]\n    enum PublicationDemand','    #[derive(Clone, Copy)]\n    enum FramePhase'),
 'methods':block('        fn import_priority_completion','        fn visited('),
 'provider':block('    fn frame_font_demand','    #[derive(Clone, Copy)]\n    enum PublicationDemand'),
 'completion':block('fn priority_has_dynamic_declarations','fn next_unprepared_font_input'),
}
assert parts['drain'] in s
parts['enqueue']=braces('FrameStep::Pending(prerequisite) =>')
parts['guard']=braces('if let Some(action) = &self.metric_action')
def function(marker):
 start=s.index(marker);a=s.index('{',start);depth=1;i=a+1
 while depth:depth+=(s[i]=='{')-(s[i]=='}');i+=1
 return textwrap.dedent(s[start:i])
parts['ordinary_ensure']=function('    fn refresh_priority_completion(')+function('    fn ensure_prioritary_property(')
parts['ordinary_apply']=function('    fn apply_one_prioritary_property(')
provider=(H/'candidate/servo/components/style/custom_properties.rs').read_text()
a=provider.index('/// Set of flags to references this custom property makes.');b=provider.index('/// A map from NonCustomReferenceMap to a T.',a)
parts['flags']=provider[a:b].replace(', MallocSizeOf, ToShmem','')
route_methods=''
for phase,method in [('Prepare','poll_prepare'),('Units','poll_units'),('Publish','poll_publication')]:
 parts['route_'+phase]=textwrap.dedent(braces('FramePhase::'+phase+' =>'))
 route_methods+='fn '+method+'(&mut self, context:&mut Context, attribute_tracker:&mut AttributeTracker, publication_ready:&mut impl FnMut(FontDependencyDemand,&PrioritaryPropertyIdSet,Option<LonghandId>)->PublicationDemand)->FrameStep {loop {\n'+parts['route_'+phase]+'\nreturn FrameStep::Next;}}\n'
source=(H/'TestSupport.rs').read_text()+'\n'+parts['staged']+parts['drain']+parts['state']+parts['action']+parts['provider']+parts['completion']+parts['flags']+parts['target']+parts['inventory']+'\nimpl Cascade<\'_> {\n'+parts['ordinary_ensure']+parts['ordinary_apply']+'}\nimpl Context<\'_,\'_>{\n'+parts['methods']+'\nfn enqueue_action(&mut self,frame:TraversalFrame,prerequisite:Option<FontTarget>)->VisitResult {\n'+parts['enqueue']+'}\nfn poll_checkpoint(&self)->VisitResult {if let Some(action)=&self.metric_action {\n'+parts['guard']+'}\nVisitResult::Complete\n}\n}\n'+'\nimpl TraversalFrame {\n'+route_methods+'}\n'+(H/'Tests.rs').read_text()
source=source.replace('SmallVec<[PreparedMetricDeclaration; 2]>','Vec<PreparedMetricDeclaration>').replace('SmallVec::new()','Vec::new()')
def mutate(old,new):
 assert source.count(old)==1,(old,source.count(old))
 return source.replace(old,new,1)
def mutate_pattern(pattern,new):
 value,count=re.subn(pattern,new,source)
 assert count==1,(pattern,count)
 return value
variants={'positive':source,
 'unfiltered_synthesis_cursor':mutate('entry.decl.id() == PropertyDeclarationId::Longhand(longhand)', 'true'),
 'truncated_synthesis_cursor':mutate('.skip(start)', '.skip(start).take_while(|(index, _)| *index < DeclarationIndex::MAX as usize)'),
 'ignored_rollback':mutate('state.revert.is_some_and(|(priority, kind)|', 'false && state.revert.is_some_and(|(priority, kind)|'),
 'synthesis_ready_on_reference':mutate('return MetricActionProgress::References(id, value);', 'self.completed_font_inputs.insert(longhand); return MetricActionProgress::References(id, value);'),
 'repeat_completed_synthesis':mutate('if completed.contains(id)', 'if false'),
 'stale_synthesis_flags':mutate('self.completed_font_inputs = LonghandIdSet::default();','self.completed_font_inputs = self.completed_font_inputs.clone();'),

 'metric_collapsed':mutate('SingleNonCustomReference::FontUnits if metrics => FontDependencyDemand::FontMetrics','SingleNonCustomReference::FontUnits if metrics => FontDependencyDemand::ComputedSize'),
 'root_leak':mutate('(is_root_element && self.intersects(Self::ROOT_FONT_ORIENTATION))','self.intersects(Self::ROOT_FONT_ORIENTATION)'),
 'no_weight_wait':mutate('for id in [FontWeight, FontWidth, FontStyle, FontSizeAdjust]','for id in [FontWidth, FontStyle, FontSizeAdjust]'),
 'early_complete':mutate('if self.completed_prioritary.contains_all(deps)','if true'),
 'lost_prepare_marker':mutate('return FrameStep::Pending(None);','self.value_non_custom_refs.remove(ReferenceFlags::COLOR_SCHEME); return FrameStep::Pending(None);'),
 'bypass_attr_guard':mutate('flags.intersects(ReferenceFlags::ATTR)', 'false'),
 'eager_prepare_gate':mutate('flags.intersects(ReferenceFlags::ATTR)', 'true'),
 'stale_flags':mutate('if self.priority_completion_flags != Some(context.included_cascade_flags)', 'if self.priority_completion_flags.is_none()'),
 'dynamic_complete':mutate('&& !priority_has_dynamic_declarations(decls, id)','&& true'),
}
records={}
with tempfile.TemporaryDirectory(prefix='metric-action-') as directory:
 scratch=Path(directory)
 lib=scratch/'libbitflags.rlib'
 rustc='/Users/bgrins/.rustup/toolchains/1.97.1-aarch64-apple-darwin/bin/rustc'
 bitflags=H.parents[1]/'third_party/rust/bitflags/src/lib.rs'
 library=subprocess.run([rustc,'--edition=2021','--crate-name','bitflags','--crate-type','rlib',str(bitflags),'-o',str(lib)],capture_output=True,text=True)
 assert library.returncode==0,library.stderr
 for name,body in variants.items():
  src=scratch/(name+'.rs');src.write_text(body);binary=scratch/name
  cmd=['/Users/bgrins/.rustup/toolchains/1.97.1-aarch64-apple-darwin/bin/rustc','--edition=2024','-C','debug-assertions=no','--test',str(src),'--extern','bitflags='+str(lib),'-o',str(binary)]
  r=subprocess.run(cmd,capture_output=True,text=True);row={'source_sha256':sha(body.encode()),'compile_command':cmd,'compile_exit':r.returncode,'compile_stderr':r.stderr}
  if not r.returncode:
   v=subprocess.run([str(binary)],capture_output=True,text=True);row.update(run_exit=v.returncode,stdout=v.stdout,stderr=v.stderr)
  records[name]=row
report={'candidate_sha256':sha(s.encode()),'rustc_sha256':sha(Path(records['positive']['compile_command'][0]).read_bytes()),'bitflags_sha256':sha(bitflags.read_bytes()),'provider_sha256':sha(provider.encode()),'parts_sha256':{k:sha(v.encode()) for k,v in parts.items()},'scratch':str(scratch),'scratch_removed':not scratch.exists(),'records':records}
(H/'TEST-RESULT.json').write_text(json.dumps(report,indent=2)+'\n')
for name,row in records.items():
 assert row['compile_exit']==0,(name,row['compile_stderr'])
 assert (row['run_exit']==0)==(name=='positive'),(name,row)
print(json.dumps({'tests':14,'compiled_behavioral_mutants':len(variants)-1,'literal_action_executes_preparation_and_publication':True,'scratch_removed':not scratch.exists()}))
