import sys
sys.dont_write_bytecode=True
import importlib.util,json,re
from pathlib import Path
r=Path(__file__).resolve().parent;cap=r/'capsule'
def load(name):
 s=importlib.util.spec_from_file_location(name,cap/(name+'.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
c=load('core');e=load('engine');x=load('source_extract')
for name,rows in [('CASES',c.cases()),('NEGATIVE-CASES',c.negative_cases())]:(cap/(name+'.json')).write_text(json.dumps(rows,indent=2)+'\n')
(cap/'bindings').mkdir(exist_ok=True)
for v in ['combined-before','combined-after','standalone-before','standalone-after']:(cap/'bindings'/(v+'.json')).write_text(json.dumps(x.selected(v),indent=2)+'\n')
modules=[]
def visit(n):
 if n in modules:return
 t=(cap/'lean'/(n+'.lean')).read_text()
 for d in re.findall(r'^import (\w+)$',t,re.M):
  if d!='Std':visit(d)
 modules.append(n)
visit('WideWitnesses')
names=[n+'.'+t for n in modules for t in re.findall(r'^theorem (\w+)',(cap/'lean'/(n+'.lean')).read_text(),re.M)]
(cap/'AUDITS.json').write_text(json.dumps({'declarations':names,'allowed_axioms':['propext','Classical.choice','Quot.sound']},indent=2)+'\n')
result=e.run(cap,r/sys.argv[1],json.loads((cap/'TOOLCHAIN.json').read_text()),c,collect_headers=True)
(r/sys.argv[1]/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
