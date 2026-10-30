import hashlib,json,re,subprocess,tempfile,textwrap
from pathlib import Path
H=Path(__file__).resolve().parent
sha=lambda x:hashlib.sha256(x).hexdigest()
rustc=Path('/Users/bgrins/.rustup/toolchains/1.97.1-aarch64-apple-darwin/bin/rustc')
s=(H/'candidate/servo/components/style/properties/cascade.rs').read_text()
def block(a,b):return textwrap.dedent(s[s.index(a):s.index(b,s.index(a))])
parts={
 'names':block('    #[derive(Clone, Eq, PartialEq, Debug)]\n    enum VarType','    enum ClosedValue'),
 'types':block('    enum ClosedValue','    /// Context struct for traversing'),
 'methods':block('        fn reset(&mut self)','        fn map(&self)'),
 'walk':block('    #[derive(Clone, Copy, Eq, PartialEq)]\n    enum ReferenceReadiness','    /// Traverse a single dependency'),
 'algorithms':block('    fn visit_link<','    let mut context = Context'),
}
# Include the actual eager reference walker before the retained ReferenceWalk block.
source=(H/'TestSupport.rs').read_text()+'\n'+parts['names']+parts['types']+'\nimpl Context<\'_>{\n'+parts['methods']+'}\n'+parts['walk']+parts['algorithms']+'\n'+(H/'Tests.rs').read_text()
source=re.sub(r"fn (\w+)<'a, 'b, 'c, 'd>",r'fn \1',source).replace("Context<'a, 'b, 'c, 'd>",'Context').replace('.entry_ref(name)', '.entry(name.clone())').replace('SmallVec::new()', 'Vec::new()')
cases={'positive':source}
mutations={
 'ignore_publication_gate':('if !publication_ready(&self.var) {','if false && !publication_ready(&self.var) {'),
 'lose_parent_cursor':('self.frames.push(frame);\n                return VisitResult::ComputationPending(index);','self.frames.first_mut().unwrap().walk = None;\n                self.frames.push(frame);\n                return VisitResult::ComputationPending(index);'),
 'lose_lowlink_on_reply':('if let VisitResult::SemanticOpen(next_index) = result {','self.lowlink = self.index;\n        if let VisitResult::SemanticOpen(next_index) = result {'),
 'semantic_open_as_settled':('VisitResult::SemanticOpen(_) => ReferenceReadiness::SemanticOpen,','VisitResult::SemanticOpen(_) => ReferenceReadiness::SemanticCycle,'),
 'allow_foreign_root':('assert_eq!(*root, var);','let _ = root;'),
 'lose_prepared_parent':('FrameStep::Pending => {\n                let index = frame.index;','FrameStep::Pending => {\n                for parent in &mut self.frames { parent.prepared_custom = None; }\n                let index = frame.index;'),
 'fallback_fifo':('self.queued.pop()','(if self.queued.is_empty() { None } else { Some(self.queued.remove(0)) })'),
 'wrong_reply_accepted':('*waiting != target || matches!(result, VisitResult::ComputationPending(_))','matches!(result, VisitResult::ComputationPending(_))'),
}
for name,(old,new) in mutations.items():
 assert source.count(old)==1,(name,old,source.count(old))
 cases[name]=source.replace(old,new)
records={}
with tempfile.TemporaryDirectory(prefix='metric-parent-frame-') as directory:
 scratch=Path(directory)
 for name,body in cases.items():
  src=scratch/(name+'.rs');src.write_text(body);binary=scratch/name
  cmd=[str(rustc),'--edition=2024','-C','debug-assertions=no','--test',str(src),'-o',str(binary)]
  r=subprocess.run(cmd,capture_output=True,text=True);row={'source_sha256':sha(body.encode()),'compile_command':cmd,'compile_exit':r.returncode,'compile_stderr':r.stderr}
  if not r.returncode:
   v=subprocess.run([str(binary)],capture_output=True,text=True);row.update(run_exit=v.returncode,stdout=v.stdout,stderr=v.stderr)
  records[name]=row
report={'candidate_sha256':sha(s.encode()),'parts_sha256':{k:sha(v.encode()) for k,v in parts.items()},'rustc_sha256':sha(rustc.read_bytes()),'scratch':str(scratch),'scratch_removed':not scratch.exists(),'records':records}
(H/'TEST-RESULT.json').write_text(json.dumps(report,indent=2)+'\n')
assert all(row['compile_exit']==0 for row in records.values()), records
assert all(row['run_exit']==(0 if name=='positive' else 101) for name,row in records.items()), records
print(json.dumps({'tests':7,'acyclic_dags':8,'compiled_false_controls':len(mutations),'recursive_eager_and_frame_eager_and_paused_comparison':True,'scratch_removed':not scratch.exists()}))
