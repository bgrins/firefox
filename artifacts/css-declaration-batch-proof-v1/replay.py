import sys
assert sys.flags.isolated and sys.flags.no_site
import argparse,gzip,hashlib,json,os,re,subprocess,time
from pathlib import Path
R=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--record',action='store_true');a=p.parse_args()
# Authenticate the complete closure before executing any local Python source.
subprocess.run([sys.executable,'-I','-S',str(R/'check.py')],check=True,capture_output=True,text=True)
out=a.output.resolve();assert not out.is_relative_to(R) and not out.exists();out.mkdir(parents=True)
cfg=json.loads((R/'TOOLCHAIN.json').read_text())
for tool in ['rustc','lean']:assert hashlib.sha256(Path(cfg[tool]).read_bytes()).hexdigest()==cfg[tool+'_sha256']
env={k:v for k,v in os.environ.items() if not k.startswith(('PYTHON','LEAN_'))};env['LEAN_PATH']=str(out)
commands=[]
def run(cmd,ok=(0,)):
 start=time.monotonic();r=subprocess.run(cmd,cwd=out,env=env,capture_output=True,text=True)
 commands.append({'command':cmd,'exit':r.returncode,'seconds':time.monotonic()-start,'stdout':r.stdout if len(r.stdout)<20000 else '(retained separately)','stderr':r.stderr})
 (out/'COMMANDS.json').write_text(json.dumps(commands,indent=2)+'\n')
 assert r.returncode in ok,(cmd,r.returncode,r.stderr,r.stdout[:3000]);return r
modules=['AllOrder','BatchIndices','BatchBase','BatchOrder','BatchStorage','BatchRank','BatchSchedule','BatchInterface','Publication','BatchPublication','BatchWitnesses']
all_names=[];counts={}
for module in modules:
 source=(R/'lean'/f'{module}.lean').read_text();assert not re.search(r'\b(sorry|axiom|admit|native_decide)\b',source)
 names=[module+'.'+n for n in re.findall(r'^theorem\s+(\w+)',source,re.M)];counts[module]=len(names);all_names+=names
 (out/f'{module}.lean').write_text(source)
 run([cfg['lean'],'-o',str(out/f'{module}.olean'),str(out/f'{module}.lean')])
assert all_names==json.loads((R/'THEOREMS.json').read_text())
(out/'Audit.lean').write_text(''.join('import '+m+'\n' for m in modules)+''.join('#print axioms '+n+'\n' for n in all_names))
ax=run([cfg['lean'],str(out/'Audit.lean')]).stdout
rows=re.findall(r"^'([^']+)' (?:depends on axioms: \[([^]]*)\]|does not depend on any axioms)$",ax,re.M)
assert [n for n,_ in rows]==all_names
for _,group in rows:assert set(re.findall(r'[A-Za-z_][\w.]*',group))<={'propext','Quot.sound','Classical.choice'}
(out/'AXIOMS.txt').write_text(ax)
run([sys.executable,'-I','-S',str(R/'native/build.py'),str(out/'native')])
def load(name):
 path=R/'native'/name;n={'__file__':str(path),'__name__':'authenticated_module'};exec(compile(path.read_text(),str(path),'exec'),n);return n
checker=load('check_rows.py');providers=json.loads((out/'native/PROVIDERS.json').read_text());binding=json.loads((out/'native/BINDING.json').read_text())
assert binding['original_complete_items']==37 and binding['candidate_complete_items']==38 and binding['ordinary_update_body_identical']
ordinary={n:ids for n,ids in providers['shorthands'].items() if n!='all'}
assert len(ordinary)==94 and max(map(len,ordinary.values()))==19
for ids in ordinary.values():
 assert len(ids)==len(set(ids))
 assert not any(checker['opposite'](providers,a,b) for a in ids for b in ids)
variants=['original','candidate','mutant_ascending','mutant_rank_omitted','mutant_rank_plus','mutant_remove_bits','mutant_replace_bits']
results={};digests={}
witness=['ascending_removal_witness','omitted_rank_witness','positive_rank_bounds_witness','missing_removal_bits_witness','wrong_replacement_bit_witness']
for variant in variants:
 run([cfg['rustc'],'--edition=2024',str(out/'native'/f'{variant}.rs'),'-o',str(out/'native'/variant)])
 r=run([str(out/'native'/variant)]);raw=r.stdout
 (out/'native'/f'{variant}.tsv.gz').write_bytes(gzip.compress(raw.encode(),mtime=0))
 stats=checker['verify'](raw,providers,variant)
 if variant.startswith('mutant_'):
  stats['kernel_witness']='BatchWitnesses.'+witness[variants.index(variant)-2]
  assert stats['kernel_witness'] in all_names
 results[variant]=stats;digests[variant]=hashlib.sha256(raw.encode()).hexdigest()
guards=load('guard_rows.py')['controls'](checker['verify'],gzip.decompress((out/'native/candidate.tsv.gz').read_bytes()).decode(),providers)
(out/'ROW-GUARDS.json').write_text(json.dumps(guards,indent=2)+'\n')
receipt={'theorem_counts':counts,'total_theorems':len(all_names),'batch_component_theorems':len(all_names)-counts['AllOrder']-counts['Publication'],'reused_root_index_helpers':3,'newly_authored_theorems':len(all_names)-counts['AllOrder']-counts['Publication']-3,'ordinary_metadata_providers':len(ordinary),'max_expansion':19,'source_binding':binding,'variants':results,'raw_sha256':digests,'row_guards':guards,'source_only':True}
(out/'RESULT.json').write_text(json.dumps(receipt,indent=2)+'\n')
if not a.record:
 assert json.loads((R/'receipts/RESULT.json').read_text())==json.loads((out/'RESULT.json').read_text())
 for variant in variants:
  assert gzip.decompress((R/'receipts'/f'{variant}.tsv.gz').read_bytes())==gzip.decompress((out/'native'/f'{variant}.tsv.gz').read_bytes())
 for name in ['PROVIDERS.json','BINDING.json','original-extraction.json','candidate-extraction.json']:
  assert (R/'receipts'/name).read_bytes()==(out/'native'/name).read_bytes()
 run([sys.executable,'-I','-S',str(R/'guard_capsule.py'),'--output',str(out/'capsule-guards')])
 assert (out/'capsule-guards/RESULT.json').read_bytes()==(R/'receipts/CAPSULE-GUARDS.json').read_bytes()
print(json.dumps({'theorems':len(all_names),'batch_component_theorems':receipt['batch_component_theorems'],'newly_authored_theorems':receipt['newly_authored_theorems'],'native_rows_per_variant':18,'compiled_mutants':5,'all_pass':True}))
