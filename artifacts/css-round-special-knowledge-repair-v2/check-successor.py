from pathlib import Path
import difflib, hashlib, json, re, subprocess, sys
p=Path(__file__).resolve().parent
old=p.parent/'css-round-special-knowledge-repair-v1'
sha=lambda q: hashlib.sha256(q.read_bytes()).hexdigest()
for rel,h in json.loads((old/'FILES.json').read_text()).items():
    assert sha(old/rel)==h,rel
unchanged=['runtime-nan-native.patch','parse-guard-native.patch','combined-native.patch','runtime-nan-standalone.patch','round-runtime-nan.html','POLICY-ROSTER.json','runtime-helper.rs','runtime-helper-O0.txt','runtime-helper-O2.txt']
unchanged += [str(q.relative_to(old)) for folder in ['runtime-nan','parse-guard','combined'] for q in (old/folder).rglob('*.rs')]
for rel in unchanged: assert (old/rel).read_bytes()==(p/rel).read_bytes(),rel
policy=(p/'integer-admission-policy-probe.html').read_text()
link='<link rel="help" href="https://drafts.csswg.org/css-values-4/#simplify-a-calculation-tree">\n'
assert policy.count(link)==1 and policy.replace(link,'')==(old/'integer-admission-policy-probe.html').read_text()
node=r'''
const vm=require('vm'); const inputs=JSON.parse(require('fs').readFileSync(0,'utf8'));
const results=inputs.map(html=>{
 let script=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(x=>x[1]).join('\n');
 new vm.Script(script);
 if(script.includes('function opacity(')) script=script.slice(script.indexOf('test(t =>'));
 let rows=[], actions;
 const context={CSS:{supports:()=>true},document:{createElement:()=>({style:{}})},
 opacity:(...args)=>{actions.push(['opacity',...args.slice(1)]);return 0},
 assert_equals:(...args)=>actions.push(['equals',...args]),assert_true:(...args)=>actions.push(['true',...args]),
 assert_not_equals:(...args)=>actions.push(['not_equals',...args]),
 test:(fn,name)=>{actions=[];fn({});rows.push({name,actions})}};
 vm.runInNewContext(script,context,{timeout:1000});return rows;
});process.stdout.write(JSON.stringify(results));
'''
files=[old/'round-deferred-infinite-step.html',p/'round-deferred-infinite-step.html',p/'round-runtime-nan.html',p/'integer-admission-policy-probe.html']
# Runtime-only bodies use additional helpers; registration alone is sufficient for those.
trace=subprocess.run(['node','-e',node],input=json.dumps([x.read_text() for x in files[:2]]),text=True,capture_output=True,check=True)
a,b=json.loads(trace.stdout);assert len(a)==7 and len(b)==19
assert a[0]==b[0] and a[-2:]==b[-2:]
for strategy in range(4):
    actions=a[1+strategy]['actions'];assert len(actions)==12
    for font in range(2):
        for sign in range(2):
            expected=actions[font*6:font*6+2]+actions[font*6+2+sign*2:font*6+4+sign*2]
            assert b[1+strategy*4+font*2+sign]['actions']==expected
roster=json.loads((p/'ROSTER.json').read_text());key='testing/web-platform/tests/css/css-values/round-deferred-infinite-step.html';assert [r['name'] for r in b]==roster[key]
registration=r'''const vm=require('vm');const inputs=JSON.parse(require('fs').readFileSync(0,'utf8'));let out=[];for(const html of inputs){const s=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(x=>x[1]).join('\n');new vm.Script(s);let names=[];vm.runInNewContext(s,{test:(f,n)=>names.push(n)},{timeout:1000});out.push(names)}process.stdout.write(JSON.stringify(out));'''
r=subprocess.run(['node','-e',registration],input=json.dumps([x.read_text() for x in files[2:]]),text=True,capture_output=True,check=True);names=json.loads(r.stdout);assert len(names[0])==10 and len(names[1])==5
assert names[0]==roster['testing/web-platform/tests/css/css-values/round-runtime-nan-priority.html']
body=(p/'round-deferred-infinite-step.html').read_text();expected=(p/'parse-guard-native.patch').read_text()+''.join(difflib.unified_diff([],body.splitlines(keepends=True),fromfile='/dev/null',tofile='b/'+key));assert (p/'parse-guard-dependent.patch').read_text()==expected
result={'status':'TEST_ONLY_SUCCESSOR_CHECKS_PASS','native_and_runtime_payloads_identical':unchanged,'guard_cases':19,'runtime_nan_cases':10,'policy_cases':5,'old_16_sample_assertion_traces_preserved_independently':True,'observed_and_integer_cases_exact':True,'policy_scripts_unchanged':True,'JS_parse_and_inert_registration':True,'browser_execution':False,'native_compilation':False,'lint_replay':False,'prior_checks_inherited_not_rerun':True}
output=Path(sys.argv[1]);assert not output.exists();output.write_text(json.dumps(result,indent=2)+'\n')
