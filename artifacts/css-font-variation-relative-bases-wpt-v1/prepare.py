import hashlib,json,subprocess,sys
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
WPT=ROOT/'testing/web-platform/tests'
sys.path[:0]=[str(p) for p in (WPT/'tools/third_party').iterdir() if p.is_dir()]+[str(WPT/'tools'),str(WPT),str(ROOT/'third_party/python/pyyaml/lib')]
def audit(event,args):
    if event=='subprocess.Popen': assert Path(args[0]).name!='git'
sys.addaudithook(audit)
import html5lib
from manifest.manifest import Manifest
from tools.lint import lint
program="const vm=require('vm');let input='';process.stdin.on('data',x=>input+=x);process.stdin.on('end',()=>{const names=[];const context=vm.createContext({window:{},promise_test:(_,name)=>names.push(name)});for(const source of JSON.parse(input))vm.runInContext(source,context);process.stdout.write(JSON.stringify(names));});"
tests=HERE/'tests';roster={};inputs={};findings={}
for path in sorted(tests.rglob('*.html')):
    relative=str(path.relative_to(tests));dom=html5lib.parse(path.read_text(),namespaceHTMLElements=False);scripts=[]
    for node in dom.iter('script'):
        src=node.get('src')
        if src in ['/resources/testharness.js','/resources/testharnessreport.js']:continue
        scripts.append((path.parent/src).read_text() if src else (node.text or ''))
    names=json.loads(subprocess.run(['node','-e',program],input=json.dumps(scripts),text=True,capture_output=True,check=True).stdout)
    assert names and len(names)==len(set(names));roster['/'+relative]=names
for path in sorted(tests.rglob('*')):
    if not path.is_file():continue
    relative=str(path.relative_to(tests))
    findings[relative]=lint.check_path(str(tests),relative)+lint.check_file_contents(str(tests),relative)
    inputs[relative]={'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'bytes':path.stat().st_size}
assert not any(findings.values()),findings
assert sorted(map(len,roster.values()))==[12,12,12]
subprocess.run(['node','--check',str(tests/'css/css-fonts/support/font-variation-relative-bases.js')],check=True)
manifest=Manifest(str(tests),'/');manifest.update([(name,None,True) for name in inputs],parallel=False)
entries=[]
for kind,path,values in manifest:
    if kind=='testharness':
        for value in values:entries.append({'path':path,'url':value.url,'timeout':value.timeout})
assert len(entries)==3 and all(e['timeout']=='long' for e in entries)
for name,data in [('MANIFEST.json',manifest.to_json()),('ROSTER.json',roster),('INPUTS.json',inputs),('LINT.json',findings)]:
    (HERE/name).write_text(json.dumps(data,indent=2,sort_keys=True)+'\n')
result={'pages':entries,'callbacks':36,'ordinary':12,'animation':12,'root_self_reference':12,'lint_findings':0,'genuine_manifest':True,'browser_execution':False}
(HERE/'CHECK.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
