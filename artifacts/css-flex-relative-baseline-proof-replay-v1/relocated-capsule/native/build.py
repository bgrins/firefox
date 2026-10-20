import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit('require isolated nonoptimized Python without site')
sys.dont_write_bytecode=True
from pathlib import Path
import argparse,hashlib,importlib.util,json,os,subprocess
ROOT=Path(__file__).resolve().parent.parent
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
cases=load('case_schema',ROOT/'native/cases.py');rows=cases.read()
source=load('source_bindings',ROOT/'source_bindings.py');bindings=source.bindings()
if bindings!=json.loads((ROOT/'SOURCE-BINDINGS.json').read_text()):raise ValueError('source binding')
bodies={r['name']:r['body'] for r in bindings}
anchors=['if (const FlexLine& line = StartmostLine(aFlr.mLines, aAxisTracker);','if (const FlexLine& line = EndmostLine(aFlr.mLines, aAxisTracker);']
stages={variant:[source.body(bodies[name],a) for a in anchors] for variant,name in [('original','original-publication'),('candidate','standalone-publication')]}
cfg=json.loads((ROOT/'TOOLCHAIN.json').read_text())
for name in ['lean','clang']:
    if hashlib.sha256(Path(cfg[name]).read_bytes()).hexdigest()!=cfg[name+'_sha256']:raise ValueError('tool pin')
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--olean',type=Path,required=True);args=p.parse_args();out=args.output.resolve()
if not args.output.is_absolute() or out.exists() or out.is_relative_to(ROOT):raise ValueError('absent external output')
out.mkdir(parents=True)
env={k:v for k,v in os.environ.items() if not k.startswith(('PYTHON','LEAN_'))};env['LEAN_PATH']=str(args.olean.resolve());commands=[]
def run(cmd):
    r=subprocess.run(cmd,env=env,cwd=out,capture_output=True,text=True);commands.append({'command':cmd,'exit':r.returncode,'stdout':r.stdout,'stderr':r.stderr});(out/'COMMANDS.json').write_text(json.dumps(commands,indent=2)+'\n')
    if r.returncode or r.stderr:raise RuntimeError(r.stdout+r.stderr)
    return r.stdout
def b(value):return 'true' if value else 'false'
def point(value,lean=False):return ('⟨' if lean else '{')+','.join(map(str,value))+('⟩' if lean else '}')
calls=[];leanRows=[]
for row in rows:
    cpp=[];lean=[]
    for i in row['items']:
        prop='std::nullopt' if i['property'] is None else 'std::optional<nsPoint>{nsPoint'+point(i['property'])+'}'
        cpp.append('{{'+','.join([str(i['identity']),point(i['actual']),prop,'{'+point(i['size'])+'}'])+'},'+str(i['first'])+','+str(i['last'])+'}')
        propLean='none' if i['property'] is None else 'some '+point(i['property'],True)
        lean.append('⟨'+','.join([str(i['identity']),point(i['actual'],True),propLean,point(i['normal'],True),point(i['size'],True),str(i['first']),str(i['last'])])+'⟩')
    calls.append('run('+str(row['id'])+',{'+str(row['mode'])+','+b(row['inlineReverse'])+'},'+b(row['reverse'])+','+str(row['old'])+',FlexLine{{'+','.join(cpp)+'}});')
    leanRows.append('('+','.join([str(row['id']),['Mode.horizontal','Mode.verticalLR','Mode.verticalRL'][row['mode']],b(row['reverse']),str(row['old']),'['+','.join(lean)+']'])+')')
template=(ROOT/'native/facade.cpp').read_text()
def rendered(first,last,normal=None,logical=None):
    fields={'LOGICAL':logical or bodies['logical-point'],'NORMAL':normal or bodies['normal-position'],'NORMAL_LOGICAL':bodies['logical-normal-position'],'FIRST':first,'LAST':last,'CASES':'\n'.join(calls)}
    s=template
    for key,value in fields.items():
        marker='/* '+key+' */'
        if s.count(marker)!=1:raise ValueError('facade marker')
        s=s.replace(marker,value)
    return s
driver='''import RelativeBaseline
set_option maxHeartbeats 4000000
set_option maxRecDepth 4096
open FlexRelativeBaseline
def cases : List (Nat × Mode × Bool × Int × List Frame) := [CASES]
def main (args : List String) : IO Unit := do
  let candidate ← match args with
    | ["candidate"] => pure true
    | ["original"] => pure false
    | _ => throw (IO.userError "unsupported variant")
  for (identity,mode,reversed,old,items) in cases do
    let result := fun last => if candidate then native last reversed mode ⟨160,80⟩ old items
      else fallback (originalDistance last mode ⟨160,80⟩) old (donor last reversed items)
    let reads := if candidate then propertyReads false reversed old items ++ propertyReads true reversed old items else []
    let trace := String.intercalate "," (reads.map fun (id,present) => toString id++":"++(if present then "1" else "0"))
    IO.println (String.intercalate "|" [toString identity,toString (result false),toString (result true),trace])
'''.replace('CASES',',\n'.join(leanRows))
(out/'Cases.lean').write_text(driver)
expected={}
for variant in ['original','candidate']:
    expected[variant]=[cases.encode(cases.oracle(row,variant=='candidate')) for row in rows]
    (out/(variant+'-expected.txt')).write_text('\n'.join(expected[variant])+'\n')
    cpp=out/(variant+'.cpp');cpp.write_text(rendered(*stages[variant]))
    for mode,flags in [('debug',['-O0','-DDEBUG']),('release',['-O2']),('ubsan',['-O1','-fsanitize=undefined','-fno-sanitize-recover=all'])]:
        exe=out/(variant+'-'+mode);run([cfg['clang'],'-std=c++17',*flags,str(cpp),'-o',str(exe)]);actual=run([str(exe)]);(out/(variant+'-'+mode+'.txt')).write_text(actual)
        if actual.splitlines()!=expected[variant]:raise ValueError(variant+' '+mode+' mismatch')
    actual=run([cfg['lean'],'--run',str(out/'Cases.lean'),variant]);(out/(variant+'-lean.txt')).write_text(actual)
    if actual.splitlines()!=expected[variant]:raise ValueError('Lean mismatch')
def once(s,a,b):
    if s.count(a)!=1:raise ValueError('mutation anchor')
    return s.replace(a,b)
first,last=stages['candidate']
mutants=[('first-actual',once(first,'GetLogicalNormalPosition','GetLogicalPosition'),last,None,None),
 ('last-actual',first,once(last,'GetLogicalNormalPosition','GetLogicalPosition'),None,None),
 ('discard-property',first,last,once(bodies['normal-position'],'return hasProperty ? normalPosition : GetPosition();','return GetPosition();'),None),
 ('last-orientation',first,once(last,'desiredSizeInFlexWM.BSize(flexWM) - lastAscent','lastAscent'),None,None),
 ('overwrite-shared',once(first,'aFlr.mAscent == nscoord_MIN','true'),once(last,'aFlr.mAscentForLast == nscoord_MIN','true'),None,None),
 ('vertical-rl-origin',first,last,None,once(bodies['logical-point'],'aContainerSize.width - aPoint.x;','aPoint.x;'))]
results=[]
for name,a,z,normal,logical in mutants:
    cpp=out/(name+'.cpp');cpp.write_text(rendered(a,z,normal,logical));exe=out/name;run([cfg['clang'],'-std=c++17','-O2',str(cpp),'-o',str(exe)]);actual=run([str(exe)]).splitlines()
    if len(actual)!=len(rows):raise ValueError('mutant malformed roster')
    differences=[i for i,(a,b) in enumerate(zip(actual,expected['candidate'])) if a!=b]
    valueDifferences=[i for i,(a,b) in enumerate(zip(actual,expected['candidate'])) if a.split('|')[:3]!=b.split('|')[:3]]
    if not differences or not valueDifferences:raise ValueError('surviving value mutant '+name)
    (out/(name+'.txt')).write_text('\n'.join(actual)+'\n');results.append({'name':name,'changed':differences,'value_changed':valueDifferences,'first_expected':expected['candidate'][valueDifferences[0]],'first_actual':actual[valueDifferences[0]]})
(out/'MUTANTS.json').write_text(json.dumps(results,indent=2)+'\n')
(out/'EXTRACTION.json').write_text(json.dumps({'bindings':bindings,'exact_consumer_slices':stages,'scope':'Full native normal getters and LogicalPoint constructor; exact standalone fallback slices. Synthetic property/array/frame/ascent/selected-line providers; original logical-position getter is a coordinate facade, not compiled nsIFrame implementation.'},indent=2)+'\n')
result={'cases':len(rows),'variants':['original','candidate'],'modes':['debug','release','ubsan','Lean evaluator'],'native_mutants':{r['name']:len(r['changed']) for r in results},'native_value_mutants':{r['name']:len(r['value_changed']) for r in results},'status':'PASS'}
(out/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
