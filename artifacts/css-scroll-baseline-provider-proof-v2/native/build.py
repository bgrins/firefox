import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit('require isolated nonoptimized Python without site')
sys.dont_write_bytecode=True
from pathlib import Path
import argparse,hashlib,importlib.util,json,os,subprocess
ROOT=Path(__file__).resolve().parent.parent

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
cases=load('case_schema',ROOT/'native/cases.py');rows=cases.read()
bind=load('source_bindings',ROOT/'source_bindings.py').bindings()
if bind!=json.loads((ROOT/'SOURCE-BINDINGS.json').read_text()):raise ValueError('source binding')
bodies={r['name']:r['body'] for r in bind}
cfg=json.loads((ROOT/'TOOLCHAIN.json').read_text())
for tool in ['lean','clang']:
    if hashlib.sha256(Path(cfg[tool]).read_bytes()).hexdigest()!=cfg[tool+'_sha256']:raise ValueError('tool pin')
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--olean',type=Path,required=True);args=p.parse_args();out=args.output.resolve()
if not args.output.is_absolute() or out.exists() or out.is_relative_to(ROOT):raise ValueError('absent external output')
out.mkdir(parents=True)
env={k:v for k,v in os.environ.items() if not k.startswith(('PYTHON','LEAN_'))};env['LEAN_PATH']=str(args.olean.resolve());commands=[]
def run(cmd,ubsan_failure=False):
    r=subprocess.run(cmd,env=env,cwd=out,capture_output=True,text=True);commands.append({'command':cmd,'exit':r.returncode,'stdout':r.stdout,'stderr':r.stderr});(out/'COMMANDS.json').write_text(json.dumps(commands,indent=2)+'\n')
    if ubsan_failure:
        if r.returncode==0 or 'runtime error: signed integer overflow' not in r.stderr:raise RuntimeError('missing intended UBSan failure '+r.stderr)
    elif r.returncode or r.stderr:raise RuntimeError(r.stdout+r.stderr)
    return r.stdout
b=lambda value:'true' if value else 'false'
cppRows=[];leanRows=[]
for r in rows:
    numbers=[str(r[k]) for k in ['outer','inner','border','fallback']]
    flags=[b(r[k]) for k in ['first','line','block','button','contain']]
    cppChild='std::nullopt' if r['child'] is None else 'std::optional<nscoord>{'+str(r['child'])+'}'
    cppRows.append('{'+','.join([str(r['id']),str(r['mode']),*flags,*numbers,cppChild])+'}')
    child='none' if r['child'] is None else 'some ('+str(r['child'])+')'
    leanRows.append('('+str(r['id'])+', ⟨'+','.join([*flags,*numbers,child])+'⟩)')

def render(method,original=False):
    s=(ROOT/'native/facade.cpp').read_text()
    for key,value in [('METHOD',method),('CSS_MIN_MAX',bodies['css-min-max']),('CASES',',\n'.join(cppRows)),('ORIGINAL',b(original))]:
        marker='/* '+key+' */'
        if s.count(marker)!=1:raise ValueError('render marker')
        s=s.replace(marker,value)
    return s

driver='''import Dispatch
set_option maxHeartbeats 4000000
set_option maxRecDepth 16384
open ScrollBaselineProvider ScrollBaselineDispatch
def cases : List (Nat × Input) := [CASES]
def event (e : Event) : Nat := match e with
 | .queryBlock => 0 | .queryButton => 1 | .fallback => 2 | .containment => 3
 | .child => 4 | .inner => 5 | .border => 6 | .outer => 7
def main (args : List String) : IO Unit := do
 let candidate ← match args with
  | ["candidate"] => pure true | ["original"] => pure false
  | _ => throw (IO.userError "unsupported variant")
 for (identity,i) in cases do
  let unsafeOld := !candidate && !legacy i && !i.contain &&
    (i.child.any fun d => i.border+d < -2147483648 || i.border+d > 2147483647)
  if unsafeOld then IO.println (toString identity++"|SKIP|")
  else
   let result := if candidate then native i else originalNative i
   let value := match result.value with | none => "none" | some n => toString n
   IO.println (toString identity++"|"++value++"|"++String.intercalate "," (result.calls.map fun e => toString (event e)))
'''.replace('CASES',',\n'.join(leanRows));(out/'Cases.lean').write_text(driver)
expected={}
for variant in ['original','candidate']:
    expected[variant]=[cases.encode(cases.oracle(r,variant=='candidate')) for r in rows]
    (out/(variant+'-expected.txt')).write_text('\n'.join(expected[variant])+'\n')
    file=out/(variant+'.cpp');file.write_text(render(bodies[variant+'-method'],variant=='original'))
    for mode,flags in [('debug',['-O0','-DDEBUG']),('release',['-O2']),('ubsan',['-O1','-fsanitize=undefined','-fno-sanitize-recover=all'])]:
        exe=out/(variant+'-'+mode);run([cfg['clang'],'-std=c++17',*flags,str(file),'-o',str(exe)]);actual=run([str(exe)]);(out/(variant+'-'+mode+'.txt')).write_text(actual)
        if actual.splitlines()!=expected[variant]:raise ValueError('native discrepancy '+variant+' '+mode)
    actual=run([cfg['lean'],'--run',str(out/'Cases.lean'),variant]);(out/(variant+'-lean.txt')).write_text(actual)
    if actual.splitlines()!=expected[variant]:raise ValueError('Lean discrepancy '+variant)

def once(text,a,z):
    if text.count(a)!=1:raise ValueError('mutant anchor '+a)
    return text.replace(a,z)
s=bodies['candidate-method']
mutants=[
 ('omit-inner-conversion',once(s,'int64_t(mScrolledFrame->BSize(aWM)) - aBaseline','int64_t(aBaseline)')),
 ('omit-outer-conversion',once(s,'return first ? baseline : bSize - baseline;','return baseline;')),
 ('outer-for-inner',once(s,'mScrolledFrame->BSize(aWM)','GetLogicalSize(aWM).BSize(aWM)')),
 ('wrong-clamp',once(s,'int64_t(0), int64_t(bSize)','int64_t(0), int64_t(INT32_MAX)')),
 ('ignore-containment',once(s,'if (StyleDisplay()->IsContainLayout())','if (StyleDisplay()->IsContainLayout() && false)')),
 ('containment-before-legacy',once(s,'  // Block containers','  if (StyleDisplay()->IsContainLayout()) return Nothing{};\n  // Block containers')),
 ('ignore-button-exception',once(s,'bf && !bf->IsButtonLike()','bf')),
 ('query-inner-for-first',once(s,'first ? int64_t(aBaseline)','first ? (mScrolledFrame->BSize(aWM), int64_t(aBaseline))'))]
results=[]
for name,body in mutants:
    file=out/(name+'.cpp');file.write_text(render(body));exe=out/name;run([cfg['clang'],'-std=c++17','-O2',str(file),'-o',str(exe)]);actual=run([str(exe)]).splitlines()
    if len(actual)!=len(rows) or any(a.split('|')[0]!=str(i) or len(a.split('|'))!=3 for i,a in enumerate(actual)):raise ValueError('malformed mutant roster')
    changed=[i for i,(a,z) in enumerate(zip(actual,expected['candidate'])) if a!=z]
    values=[i for i in changed if actual[i].split('|')[1]!=expected['candidate'][i].split('|')[1]]
    if not changed or (name!='query-inner-for-first' and not values):raise ValueError('surviving semantic mutant '+name)
    (out/(name+'.txt')).write_text('\n'.join(actual)+'\n');k=(values or changed)[0]
    results.append({'name':name,'changed':changed,'value_changed':values,'first_expected':expected['candidate'][k],'first_actual':actual[k]})
name='narrow-before-subtraction';body=once(s,'int64_t(mScrolledFrame->BSize(aWM)) - aBaseline','(mScrolledFrame->BSize(aWM) - aBaseline)')
file=out/(name+'.cpp');file.write_text(render(body));exe=out/name
run([cfg['clang'],'-std=c++17','-O1','-fsanitize=undefined','-fno-sanitize-recover=all',str(file),'-o',str(exe)])
run([str(exe)],ubsan_failure=True)
results.append({'name':name,'rejected':'UBSan signed integer overflow in source-expression mutant'})
(out/'MUTANTS.json').write_text(json.dumps(results,indent=2)+'\n')
(out/'EXTRACTION.json').write_text(json.dumps({'bindings':bind,'scope':'Complete actual methods; synthetic frame, Maybe/map, query, geometry, fallback and CSSMinMax providers. Arguments checked, calls observed. No compiled Gecko object/lifecycle implementation.'},indent=2)+'\n')
result={'cases':len(rows),'original_executed':sum('|SKIP|' not in r for r in expected['original']),'candidate_executed':len(rows),'variants':['original','candidate'],'modes':['debug','release','ubsan','Lean evaluator'],'native_mutants':{r['name']:len(r['changed']) if 'changed' in r else r['rejected'] for r in results},'status':'PASS'}
(out/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
