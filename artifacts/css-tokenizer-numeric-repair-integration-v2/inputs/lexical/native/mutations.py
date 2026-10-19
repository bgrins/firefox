import argparse,hashlib,json,os,shutil,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--baseline',type=Path,required=True);p.add_argument('--modules',type=Path,required=True);p.add_argument('--lean',required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
a.output.mkdir(parents=True,exist_ok=False)
rustc=json.loads((R/'inputs/scanner/scanner/TOOLCHAIN.json').read_text())['rustc']
original=(a.baseline/'vendor/cssparser/src/tokenizer.rs').read_text()
start=original.index('fn consume_numeric(') if 'fn consume_numeric(' in original else original.index("fn consume_numeric<'a>")
end=original.index('\n#[inline]',start)
body=original[start:end]
lex=(R/'lean/NumericLexical.lean').read_text().split('\ntheorem ')[0]
units=(R/'lean/NumericUnits.lean').read_text().split('\ntheorem ')[0]
mutants=[
 ('sign-field',body.replace('            has_sign,','            has_sign: false,'),'+1',lex.replace('integral.digits,frac.digits,expo.digits,NumericEntry.hasSign xs,','integral.digits,frac.digits,expo.digits,false,',1),'NumericLexical','(native [43,49]).hasSign'),
 ('fraction-type',body.replace('is_integer = false;','is_integer = true;',1),'1.0',lex.replace('!frac.used && !expo.used','!expo.used',1),'NumericLexical','!(native [49,46,48]).isInteger'),
 ('exponent-type',body[:body.index('let mut value')]+body[body.index('let mut value'):].replace('is_integer = false;','is_integer = true;',1),'1e0',lex.replace('!frac.used && !expo.used','!frac.used',1),'NumericLexical','!(native [49,101,48]).isInteger'),
 ('lh-flags',body,'1lh',units.replace('then 5','then 1',1),'NumericUnits','nativeFlags [108,104] == 5'),
]
results=[]
for name,changed,css,leantext,namespace,expr in mutants:
 d=a.output/name;d.mkdir();vendor=d/'cssparser';shutil.copytree(a.baseline/'vendor/cssparser',vendor)
 (vendor/'src/tokenizer.rs').write_text(original[:start]+changed+original[end:])
 commands=[]
 def run(cmd,cwd,stdin=None):
  r=subprocess.run(cmd,cwd=cwd,input=stdin,env={**os.environ,'LEAN_PATH':str(a.modules.resolve())},capture_output=True,text=True)
  commands.append({'cmd':cmd,'cwd':str(cwd),'exit':r.returncode,'stdout':r.stdout,'stderr':r.stderr});assert r.returncode==0,commands[-1]
  return r.stdout
 cmd=[rustc,'--crate-name','cssparser','--crate-type','rlib','--edition','2024','-C','opt-level=1','-L','dependency='+str(a.baseline.resolve()),str(vendor.resolve()/'src/lib.rs'),'-o',str(d.resolve()/'libcssparser.rlib')]
 for dep in ['dtoa_short','itoa','smallvec']:cmd+=['--extern',dep+'='+str(a.baseline.resolve()/('lib'+dep+'.rlib'))]
 run(cmd,d)
 harness=(a.baseline/'harness.rs').read_text()
 if name=='lh-flags':
  old='return Self::FONT_UNITS | Self::LH_UNITS;';assert harness.count(old)==1;harness=harness.replace(old,'return Self::FONT_UNITS;')
 (d/'harness.rs').write_text(harness)
 run([rustc,'--edition','2024','-C','opt-level=1','-L','dependency='+str(a.baseline.resolve()),'--extern','cssparser='+str(d.resolve()/'libcssparser.rlib'),'--extern','bitflags='+str(a.baseline.resolve()/'libbitflags.rlib'),str(d.resolve()/'harness.rs'),'-o',str(d.resolve()/'native')],d)
 observed=run([str(d.resolve()/'native')],d,css.encode().hex()+'\n')
 baseline=run([str(a.baseline.resolve()/'numeric')],d,css.encode().hex()+'\n')
 assert observed!=baseline,(name,observed)
 (d/'Mutant.lean').write_text(leantext+'\n#eval '+expr+'\nend '+namespace+'\n')
 answer=run([a.lean,str(d.resolve()/'Mutant.lean')],a.modules)
 assert answer.strip()=='false',(name,answer)
 results.append({'name':name,'input':css,'baseline':baseline,'mutant':observed,'lean_mutant':'compiled; semantic witness false','commands':commands})
 (a.output/'RESULT.json').write_text(json.dumps(results,indent=2)+'\n')
print(json.dumps({'status':'PASS','compiled_native_semantic_mutants':len(results),'compiled_lean_semantic_mutants':len(results)}))
