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
program="const vm=require('vm');let input='';process.stdin.on('data',x=>input+=x);process.stdin.on('end',()=>{const names=[];const context=vm.createContext({window:{},test:(_,name)=>names.push(name),promise_test:(_,name)=>names.push(name)});for(const source of JSON.parse(input))vm.runInContext(source,context);process.stdout.write(JSON.stringify(names));});"
roster={}
mozilla_lint_findings=[]
for dirname,url,output in [('tests','/','MANIFEST.json')]:
    tests=HERE/dirname
    for path in sorted(tests.rglob('*.html')):
        relative=str(path.relative_to(tests));source=path.read_text()
        dom=html5lib.parse(source,namespaceHTMLElements=False)
        scripts=[node.text for node in dom.iter('script') if not node.get('src')]
        names=json.loads(subprocess.run(['node','-e',program],input=json.dumps(scripts),text=True,capture_output=True,check=True).stdout)
        assert names and len(names)==len(set(names))
        errors=lint.check_path(str(tests),relative)+lint.check_file_contents(str(tests),relative)
        if dirname == 'mozilla/tests':
            mozilla_lint_findings.extend(errors)
            assert all(e[0] == 'SPECIALPOWERS API' for e in errors), errors
        else:
            assert not errors,errors
        for node in dom.iter('script'):
            if node.get('src'): assert node.get('src') in ['/resources/testharness.js','/resources/testharnessreport.js']
        roster[url+relative]=names
    paths=sorted(str(p.relative_to(tests)) for p in tests.rglob('*') if p.is_file())
    manifest=Manifest(str(tests),url);manifest.update([(path,None,True) for path in paths],parallel=False)
    (HERE/output).write_text(json.dumps(manifest.to_json(),indent=2,sort_keys=True)+'\n')
assert len(roster)==1 and sum(map(len,roster.values()))==4
(HERE/'ROSTER.json').write_text(json.dumps(roster,indent=2)+'\n')
result={'callbacks':4,'pages':1,'signatures':5,'genuine_manifests':1,'mozilla_lint_findings':mozilla_lint_findings,'mozilla_other_lint_errors':0,'new_fixture_browser_execution':False,'native_build':False}
(HERE/'CHECK.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
