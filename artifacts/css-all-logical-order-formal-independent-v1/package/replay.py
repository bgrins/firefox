import sys
assert sys.flags.isolated and sys.flags.no_site
import argparse,gzip,hashlib,json,os,re,subprocess,time
from pathlib import Path
R=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--record',action='store_true');a=p.parse_args()
out=a.output.resolve();assert not out.is_relative_to(R);out.mkdir(parents=True,exist_ok=False)
cfg=json.loads((R/'TOOLCHAIN.json').read_text())
for tool in ['rustc','lean']:assert hashlib.sha256(Path(cfg[tool]).read_bytes()).hexdigest()==cfg[tool+'_sha256']
env={k:v for k,v in os.environ.items() if not k.startswith(('LEAN_','PYTHON'))};env['LEAN_PATH']=str(out)
commands=[]
def run(cmd,ok=(0,)):
 start=time.monotonic();r=subprocess.run(cmd,cwd=out,env=env,capture_output=True,text=True)
 commands.append({'command':cmd,'exit':r.returncode,'seconds':time.monotonic()-start,'stdout':r.stdout if len(r.stdout)<20000 else '(retained separately)','stderr':r.stderr})
 (out/'COMMANDS.json').write_text(json.dumps(commands,indent=2)+'\n')
 assert r.returncode in ok,(cmd,r.returncode,r.stderr,r.stdout[:1000]);return r
source=(R/'lean/AllOrder.lean').read_text();assert not re.search(r'\b(sorry|axiom|admit|native_decide)\b',source)
names=['AllOrder.'+n for n in re.findall(r'^theorem\s+(\w+)',source,re.M)]
assert names==json.loads((R/'THEOREMS.json').read_text())
(out/'AllOrder.lean').write_text(source)
run([cfg['lean'],'-o',str(out/'AllOrder.olean'),str(out/'AllOrder.lean')])
(out/'Audit.lean').write_text('import AllOrder\n'+''.join('#print axioms '+n+'\n' for n in names))
ax=run([cfg['lean'],str(out/'Audit.lean')]).stdout
for n in names:assert ax.count("'"+n+"'")==1
for group in re.findall(r'depends on axioms:\s*\[([^\]]*)\]',ax):assert set(re.findall(r'[A-Za-z_][\w.]*',group))<={'propext','Quot.sound','Classical.choice'}
assert ax.count('depends on axioms:')+ax.count('does not depend on any axioms')==len(names)
(out/'AXIOMS.txt').write_text(ax)
run([sys.executable,'-I','-S',str(R/'native/build.py'),str(out/'native')])
module={'__file__':str(R/'native/check_rows.py'),'__name__':'retained_checker'}
exec(compile((R/'native/check_rows.py').read_text(),str(R/'native/check_rows.py'),'exec'),module)
providers=json.loads((out/'native/PROVIDERS.json').read_text())
variants=['original','candidate','mutant_legacy_update','mutant_legacy_gate','mutant_no_order','mutant_importance','mutant_move_bits','mutant_membership']
witness_names=['legacy_update_witness','legacy_gate_witness','missing_order_check_witness','priority_downgrade_witness','missing_move_bit_removal_witness','missing_membership_insert_witness']
results={};digests={}
for variant in variants:
 src=out/'native'/f'{variant}.rs';exe=out/'native'/variant
 run([cfg['rustc'],'--edition=2024',str(src),'-o',str(exe)])
 run_result=run([str(exe)],ok=(0,42) if variant.startswith('mutant_') else (0,))
 text=run_result.stdout;compressed=gzip.compress(text.encode(),mtime=0)
 (out/'native'/f'{variant}.tsv.gz').write_bytes(compressed)
 stats=module['verify'](text,providers,variant,run_result.returncode);stats['execution_exit']=run_result.returncode
 results[variant]=stats;digests[variant]=hashlib.sha256(text.encode()).hexdigest()
 if variant=='candidate':assert not stats['failures']
 elif variant=='original':assert stats['failures'] and all(r['name'].startswith('all-') for r in stats['failures'])
 else:
  assert stats['failures'];stats['kernel_witness']='AllOrder.'+witness_names[variants.index(variant)-2]
  assert stats['kernel_witness'] in names
guards={'__file__':str(R/'native/guard_rows.py'),'__name__':'row_controls'}
exec(compile((R/'native/guard_rows.py').read_text(),str(R/'native/guard_rows.py'),'exec'),guards)
negative=guards['controls'](module['verify'],gzip.decompress((out/'native/candidate.tsv.gz').read_bytes()).decode(),providers)
(out/'ROW-GUARDS.json').write_text(json.dumps(negative,indent=2)+'\n')
receipt={'theorems':len(names),'metadata_longhands':len(providers['longhands']),'all_expansion':len(providers['all']),'source_only':True,'row_guards':negative,'variants':results,'raw_sha256':digests}
(out/'RESULT.json').write_text(json.dumps(receipt,indent=2)+'\n')
if not a.record:
 run([sys.executable,'-I','-S',str(R/'guard_capsule.py'),'--output',str(out/'capsule-guards')])
 assert (out/'capsule-guards/RESULT.json').read_bytes()==(R/'receipts/CAPSULE-GUARDS.json').read_bytes()
 reference=json.loads((R/'receipts/RESULT.json').read_text());assert reference==receipt
 for variant in variants:
  assert gzip.decompress((R/'receipts'/f'{variant}.tsv.gz').read_bytes())==gzip.decompress((out/'native'/f'{variant}.tsv.gz').read_bytes())
 for name in ['PROVIDERS.json','original-extraction.json','candidate-extraction.json']:
  assert (R/'receipts'/name).read_bytes()==(out/'native'/name).read_bytes()
print(json.dumps({'theorems':len(names),'counts':{k:v['counts'] for k,v in results.items()},'all_mutants_witnessed':True}))
