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
 'state':block('    enum NodePublication<T>','    #[derive(Clone, Copy, Debug, Eq, PartialEq)]\n    enum VisitResult'),
 'action':block('    #[derive(Clone, Copy)]\n    enum PublicationDemand','    #[derive(Clone, Copy)]\n    enum FramePhase'),
 'methods':block('        fn pending_metric_action','        fn visited('),
}
assert parts['drain'] in s
parts['enqueue']=braces('FrameStep::Pending(prerequisite) =>')
parts['guard']=braces('if let Some(action) = &self.metric_action')
source=(H/'TestSupport.rs').read_text()+'\n'+parts['staged']+parts['drain']+parts['state']+parts['action']+'\nimpl Context<\'_,\'_>{\n'+parts['methods']+'\nfn enqueue_action(&mut self,frame:TraversalFrame,prerequisite:Option<PrioritaryPropertyId>)->VisitResult {\n'+parts['enqueue']+'}\nfn poll_checkpoint(&self)->VisitResult {if let Some(action)=&self.metric_action {\n'+parts['guard']+'}\nVisitResult::Complete\n}\n}\n'+(H/'Tests.rs').read_text()
source=source.replace('SmallVec<[PreparedMetricDeclaration; 2]>','Vec<PreparedMetricDeclaration>').replace('SmallVec::new()','Vec::new()')
def mutate(old,new):
 assert source.count(old)==1,(old,source.count(old))
 return source.replace(old,new,1)
def mutate_pattern(pattern,new):
 value,count=re.subn(pattern,new,source)
 assert count==1,(pattern,count)
 return value
variants={'positive':source,
 'foreign_identity':mutate('!std::ptr::eq(current.identity.as_ref(), action.identity.as_ref())','false'),
 'bypass_pending_action':mutate('return VisitResult::ComputationPending(action.index);','return VisitResult::Complete;'),
 'ensured_is_complete':mutate_pattern(r'if self\s*\.priority_completion\s*\.complete\s*\.contains\(action.prerequisite\)', 'if self.cascade.ensured_prioritary.contains(action.prerequisite)'),
 'clear_generated_wait':mutate_pattern(r'MetricDrainStep::Prerequisite\(id\) => \{\s*MetricActionProgress::GeneratedPrerequisite\(id\)', 'MetricDrainStep::Prerequisite(id) => { self.metric_action = None; MetricActionProgress::GeneratedPrerequisite(id)'),
 'clear_reference_wait':mutate_pattern(r'MetricDrainStep::References\(id, value\) => \{\s*MetricActionProgress::References\(id, value\)', 'MetricDrainStep::References(id, value) => { self.metric_action = None; MetricActionProgress::References(id, value)'),
 'stale_frame':mutate('matches!(frame.phase, FramePhase::Publish)','true'),
}
records={}
with tempfile.TemporaryDirectory(prefix='metric-action-') as directory:
 scratch=Path(directory)
 for name,body in variants.items():
  src=scratch/(name+'.rs');src.write_text(body);binary=scratch/name
  cmd=['/Users/bgrins/.rustup/toolchains/1.97.1-aarch64-apple-darwin/bin/rustc','--edition=2024','-C','debug-assertions=no','--test',str(src),'-o',str(binary)]
  r=subprocess.run(cmd,capture_output=True,text=True);row={'source_sha256':sha(body.encode()),'compile_command':cmd,'compile_exit':r.returncode,'compile_stderr':r.stderr}
  if not r.returncode:
   v=subprocess.run([str(binary)],capture_output=True,text=True);row.update(run_exit=v.returncode,stdout=v.stdout,stderr=v.stderr)
  records[name]=row
report={'candidate_sha256':sha(s.encode()),'rustc_sha256':sha(Path(records['positive']['compile_command'][0]).read_bytes()),'parts_sha256':{k:sha(v.encode()) for k,v in parts.items()},'scratch':str(scratch),'scratch_removed':not scratch.exists(),'records':records}
(H/'TEST-RESULT.json').write_text(json.dumps(report,indent=2)+'\n')
for name,row in records.items():
 assert row['compile_exit']==0,(name,row['compile_stderr'])
 assert (row['run_exit']==0)==(name=='positive'),(name,row)
print(json.dumps({'tests':6,'compiled_behavioral_mutants':len(variants)-1,'literal_action_executes_preparation_and_publication':True,'scratch_removed':not scratch.exists()}))
