from pathlib import Path
import difflib,hashlib,json,subprocess,tempfile
P=Path(__file__).resolve().parent
ROOT=P.parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
roles=json.loads((P/'SOURCE-ROLES.json').read_text())
def strip_diagnostics(s):
 for label in ['selection-flags','static-prerequisite-prefix','static-prerequisite-application','family-complete-before-appearance','family-claimed-active-or-applied','family-selection-flags','orientation-prefix-or-application','orientation-incomplete']:
  line=next(line for line in s.splitlines(True) if f'readset={label}' in line)
  s=s.replace(line,'',1)
 start=s.index('                    progress => {',s.index('let mut run_one ='))
 end=s.index('\n                }\n            }\n        } else {',start)
 s=s[:start]+'                    _ => break result,'+s[end:]
 start=s.index('        if !matches!(result, VisitResult::Complete | VisitResult::CycleSettled) {',s.index('let mut run_one ='))
 end=s.index('        assert!(matches!(\n            result,',start)
 return s[:start]+s[end:]
parent_patch='';native_patch=''
for name,row in roles.items():
 for role in ['base','parent','candidate']:assert sha(ROOT/row[role]['path'])==row[role]['sha256']
 base=(ROOT/row['base']['path']).read_text();parent=(ROOT/row['parent']['path']).read_text();candidate=(ROOT/row['candidate']['path']).read_text()
 assert (strip_diagnostics(candidate) if name.endswith('/cascade.rs') else candidate)==parent
 parent_patch+=''.join(difflib.unified_diff(parent.splitlines(True),candidate.splitlines(True),fromfile='a/'+name,tofile='b/'+name))
 native_patch+=''.join(difflib.unified_diff(base.splitlines(True),candidate.splitlines(True),fromfile='a/'+name,tofile='b/'+name))
assert (P/'PARENT-DELTA.patch').read_text()==parent_patch
assert (P/'native.patch').read_text()==native_patch
for patch,old in [('PARENT-DELTA.patch','parent'),('native.patch','base')]:
 with tempfile.TemporaryDirectory(prefix='css-minimum-diagnostic-',dir='/private/tmp') as td:
  scratch=Path(td)
  for name,row in roles.items():
   q=scratch/name;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes((ROOT/row[old]['path']).read_bytes())
  for reverse in [False,True]:
   args=['patch','--fuzz=0','-p1','-i',str(P/patch)]
   if reverse:args.append('-R')
   result=subprocess.run(args,cwd=scratch,capture_output=True,text=True);assert result.returncode==0,(result.stdout,result.stderr)
   assert 'offset' not in result.stdout and 'fuzz' not in result.stdout
   for name,row in roles.items():assert sha(scratch/name)==row[old if reverse else 'candidate']['sha256']
 assert not scratch.exists()
for name,pin in json.loads((P/'REFERENCES.json').read_text()).items():assert sha(ROOT/name)==pin,name
cascade=(ROOT/roles['servo/components/style/properties/cascade.rs']['candidate']['path']).read_text()
assert 'type DeclarationIndex = u32;' in cascade
parent=(ROOT/roles['servo/components/style/properties/cascade.rs']['parent']['path']).read_text()
assert strip_diagnostics(cascade.replace('VisitResult::Complete | VisitResult::CycleSettled\n        ));','VisitResult::Complete\n        ));',1))!=parent
assert strip_diagnostics(cascade.replace('self.metric_action = None;','self.metric_action = None; self.size_preparation = None;',1))!=parent
subprocess.run(['rustfmt','--edition','2024','--config','skip_children=true','--check',str(ROOT/roles['servo/components/style/properties/cascade.rs']['candidate']['path'])],check=True)
print(json.dumps({'exact_three_source_bindings':True,'diagnostics_removed_equals_parent_bytes':True,'parent_and_native_patch_zero_fuzz_roundtrips':True,'capacity_u32_preserved':True,'provider_and_mod_unchanged':True,'assertion_removal_and_state_write_controls_rejected':2,'rustfmt_passed':True,'scratch_removed':True,'native_compiled':False,'browser_executed':False}))
