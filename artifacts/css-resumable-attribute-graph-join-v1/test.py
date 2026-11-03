import hashlib,importlib.util,json,subprocess,tempfile,sys
from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parents[1]
s=(H/'candidate/servo/components/style/properties/cascade.rs').read_text()
p=(H/'candidate/servo/components/style/custom_properties.rs').read_text()
spec=importlib.util.spec_from_file_location('reader',R/'artifacts/css-variable-origin-proof-v2/native/rust_reader.py');reader=importlib.util.module_from_spec(spec);spec.loader.exec_module(reader)
parts={}
def full(text,marker):
 start=text.index(marker);tokens=reader.tokens(text[start:]);i=next(i for i,t in enumerate(tokens) if t[0]=='{');j=reader.pair(tokens,i);body=text[start:start+tokens[j][2]];parts[marker]=hashlib.sha256(body.encode()).hexdigest();return body
code=(H/'TestSupport.rs').read_text()
for marker in ['    enum ClosedValue {','    enum NodePublication<T> {','    #[derive(Clone, Copy, Debug, Eq, PartialEq)]\n    enum NodeReadiness','    impl<T> NodePublication<T> {','    #[derive(Clone, Copy, Debug, Eq, PartialEq)]\n    enum VisitResult','    struct VarInfo {']:
 code+='\n'+full(s,marker)
code+='\n'+full(p,'pub fn handle_invalid_at_computed_value_time(')
code+='\nimpl Context{\n'
for marker in ['        fn poll_frames(','        fn publish_closed(','        fn handle_loop(','        fn metric_action_is_current(','        fn resolve_metric_lookup_inner(']:code+=full(s,marker)+'\n'
code+='}\nimpl TraversalFrame {\nfn accepts_computed_size(&self,_:bool)->bool{false}\n'+full(s,'        fn receive(')+'\n'
code+='''fn step(&mut self,_:&NonCustomPropertyReferences,context:&mut Context,attribute_tracker:&mut AttributeTracker,_:&mut impl FnMut(FontDependencyDemand,&PrioritaryPropertyIdSet,Option<LonghandId>)->PublicationDemand)->FrameStep {
 loop {match self.phase {
 FramePhase::References=>{
  if self.reference_reply.take().is_some(){self.next+=1;}
  if let Some(target)=self.links.get(self.next).cloned(){self.waiting=Some((target.clone(),LinkPurpose::Reference));return FrameStep::Link(target);}
  self.phase=FramePhase::Close;
 },
'''
code+=full(s,'                    FramePhase::Close => {')+',\n'
code+='''FramePhase::Publish=>{assert!(context.publish_closed(self.index,attribute_tracker)==ComputationStatus::Ready);return FrameStep::Complete(VisitResult::Complete);}
 }}}
}\n'''
code+='type LonghandId=u8;\n'+(H/'Tests.rs').read_text()
(H/'EXTRACTED.rs').write_text(code)
def mutate(old,new):
 assert code.count(old)==1,(old,code.count(old));return code.replace(old,new,1)
cases={'positive':code,
 'attribute_barrier_removed':mutate('attribute_attempt.is_some() && matches!(target, VarType::Attr(..))','false'),
 'foreign_floor_removed':code.replace('*index < semantic_floor','false').replace('index < semantic_floor','false'),
 'registered_default_lost':mutate('} else if let Some(ref initial_value) = registration.initial_value','} else if let Some(ref initial_value) = None::<Initial>'),
 'scc_lost':mutate('self.lowlink = cmp::min(self.lowlink, next_index);','self.lowlink = self.index;'),
}
rustc=Path('/Users/bgrins/.rustup/toolchains/1.97.1-aarch64-apple-darwin/bin/rustc');records=[]
def run(cmd):
 r=subprocess.run(cmd,capture_output=True,text=True,timeout=60);records.append({'command':list(map(str,cmd)),'exit':r.returncode,'stdout':r.stdout,'stderr':r.stderr});return r
with tempfile.TemporaryDirectory(prefix='attribute-graph-join-',dir='/private/tmp') as d:
 scratch=Path(d)
 try:
  for name,path,deps in [('stable_deref_trait',R/'third_party/rust/stable_deref_trait/src/lib.rs',[]),('servo_arc',R/'servo/components/servo_arc/lib.rs',['stable_deref_trait'])]:
   cmd=[rustc,'--crate-name',name,'--crate-type','rlib','--edition','2024',path,'-o',scratch/f'lib{name}.rlib']
   for dep in deps:cmd+=['--extern',f'{dep}={scratch}/lib{dep}.rlib']
   assert run(cmd).returncode==0,records[-1]
  for name,body in cases.items():
   src=scratch/(name+'.rs');src.write_text(body)
   assert run([rustc,'--test','--edition','2024','-L','dependency='+d,'--extern','servo_arc='+d+'/libservo_arc.rlib',src,'-o',scratch/name]).returncode==0,records[-1]
   records[-1]['variant']=name
   result=run([scratch/name,'--nocapture']);records[-1]['variant']=name
   assert (result.returncode==0)==(name=='positive'),records[-1]
 finally:
  report={'records':records,'parts':parts,'candidate_sha256':hashlib.sha256(s.encode()).hexdigest(),'provider_sha256':hashlib.sha256(p.encode()).hexdigest(),'extracted_sha256':hashlib.sha256(code.encode()).hexdigest(),'scratch':d,'inputs':{n:hashlib.sha256((H/n).read_bytes()).hexdigest() for n in ['test.py','TestSupport.rs','Tests.rs']}}
  (H/(sys.argv[1] if len(sys.argv)>1 else 'TEST-RESULT-run3.json')).write_text(json.dumps(report,indent=2)+'\n')
assert not scratch.exists();report['scratch_removed']=True;(H/(sys.argv[1] if len(sys.argv)>1 else 'TEST-RESULT-run3.json')).write_text(json.dumps(report,indent=2)+'\n');print('6 tests / 4 compiled false controls passed; scratch removed')
