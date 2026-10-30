import hashlib,json,subprocess,tempfile,textwrap
from pathlib import Path
H=Path(__file__).resolve().parent
sha=lambda x:hashlib.sha256(x).hexdigest()
rustc=Path('/Users/bgrins/.rustup/toolchains/1.97.1-aarch64-apple-darwin/bin/rustc')
s=(H/'candidate/servo/components/style/properties/cascade.rs').read_text()
def between(a,b):return s[s.index(a):s.index(b,s.index(a))]
blocks={
 'types':between('    enum ClosedValue {','    #[derive(Debug, Default)]\n    struct OrderIndexMap'),
 'reset':between('        fn reset(&mut self)', '        fn visited('),
 'methods':between('        fn visited(', '        fn map(&self)'),
 'pop':between('        // This is the root of a strong-connected component.', '        let publication = match var {'),
 'link':between('        let next_index = match traverse(var, non_custom_references, context, attr_tracker)', '        let next_info = &context.var_info[next_index];'),
}
blocks['link']=blocks['link'].replace('match traverse(var, non_custom_references, context, attr_tracker)','match result').replace('=> return,', '=> return None,')
source=(H/'TestSupport.rs').read_text()+'\n'+textwrap.dedent(blocks['types'])+'\nimpl Context<\'_> {\n'+blocks['reset']+blocks['methods']+'}\nfn pop_component(context: &mut Context, index: usize, var: VarType, self_ref: bool) -> VisitResult {\n'+blocks['pop']+'VisitResult::Complete\n}\nfn link_result(result: VisitResult) -> Option<usize> {\n'+blocks['link']+'Some(next_index)\n}\n'+(H/'Tests.rs').read_text()
cases={'positive':source}
mutations={
 'ignore_readiness':('if !prerequisites_ready {','if false && !prerequisites_ready {'),
 'early_computed':('Self::CycleUnsettled | Self::Pending(_) | Self::Applying => {\n                NodeReadiness::ComputationPending','Self::CycleUnsettled | Self::Pending(_) | Self::Applying => {\n                NodeReadiness::Complete'),
 'discard_pending_root':('.all(|info| info.publication.can_retire())','.all(|_| true)'),
 'pending_as_ready':('unreachable!("Recursive traversal cannot resume a suspended publication")','return None'),
 'cycle_before_settlement':('Self::CycleUnsettled | Self::Pending(_) | Self::Applying => {','Self::CycleUnsettled => NodeReadiness::CycleSettled,\n        Self::Pending(_) | Self::Applying => {'),
 'missing_publication':('self.var_info[index].publication.finish();',''),
}
for name,(old,new) in mutations.items():
 assert source.count(old)==1,(name,old)
 cases[name]=source.replace(old,new)
records={}
with tempfile.TemporaryDirectory(prefix='semantic-publication-') as directory:
 scratch=Path(directory)
 for name,body in cases.items():
  src=scratch/(name+'.rs');src.write_text(body);binary=scratch/name
  cmd=[str(rustc),'--edition=2021','-C','debug-assertions=no','--test',str(src),'-o',str(binary)]
  r=subprocess.run(cmd,capture_output=True,text=True)
  row={'source_sha256':sha(body.encode()),'compile_command':cmd,'compile_exit':r.returncode,'compile_stderr':r.stderr}
  if not r.returncode:
   v=subprocess.run([str(binary)],capture_output=True,text=True);row.update(run_exit=v.returncode,stdout=v.stdout,stderr=v.stderr)
  records[name]=row
report={'candidate_sha256':sha(s.encode()),'blocks_sha256':{k:sha(v.encode()) for k,v in blocks.items()},'rustc_sha256':sha(rustc.read_bytes()),'scratch':str(scratch),'scratch_removed':not scratch.exists(),'records':records}
(H/'TEST-RESULT.json').write_text(json.dumps(report,indent=2)+'\n')
assert all(r['compile_exit']==0 for r in records.values()),records
assert all(r['run_exit']==(0 if name=='positive' else 101) for name,r in records.items()),records
print(json.dumps({'tests':5,'compiled_false_controls':len(mutations),'scratch_removed':not scratch.exists()}))
