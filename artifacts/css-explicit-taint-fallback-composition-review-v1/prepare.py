import hashlib,json,shutil,subprocess,sys,tempfile
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
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
scratch=Path(tempfile.mkdtemp(prefix='attr-composition-wpt-',dir='/private/tmp'))
result={'scratch':str(scratch),'browser_execution':False,'live_installation':False}
try:
    tests=scratch/'tests';shutil.copytree(HERE/'tests',tests)
    resources={}
    for n in ['testharness.js','testharnessreport.js']:
        source=ROOT/'artifacts/css-prioritary-selection-suite-v3/tests/resources'/n
        target=tests/'resources'/n;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target)
        resources['/resources/'+n]={'path':str(source.relative_to(ROOT)),'sha256':sha(source),'bytes':source.stat().st_size}
    roster={};findings={}
    for path in sorted((tests/'css').rglob('*.html')):
        relative=str(path.relative_to(tests));original=HERE/'tests'/relative
        resources['/'+relative]={'path':str(original.relative_to(ROOT)),'sha256':sha(original),'bytes':original.stat().st_size}
        dom=html5lib.parse(path.read_text(),namespaceHTMLElements=False)
        scripts=[node.text for node in dom.iter('script') if not node.get('src')]
        program="const vm=require('vm');let input='';process.stdin.on('data',x=>input+=x);process.stdin.on('end',()=>{const names=[];const context=vm.createContext({window:{},promise_test:(_,name)=>names.push(name)});for(const source of JSON.parse(input))vm.runInContext(source,context);process.stdout.write(JSON.stringify(names));});"
        run=subprocess.run(['node','-e',program],input=json.dumps(scripts),text=True,capture_output=True)
        assert run.returncode==0,run.stderr
        names=json.loads(run.stdout);assert len(names)==3 and len(set(names))==3
        roster['/'+relative]=names
        findings[relative]=lint.check_path(str(tests),relative)+lint.check_file_contents(str(tests),relative)
    (HERE/'LINT.json').write_text(json.dumps(findings,indent=2)+'\n')
    assert not any(findings.values()),findings
    manifest=Manifest(str(tests),'/');paths=sorted(str(p.relative_to(tests)) for p in tests.rglob('*') if p.is_file())
    manifest.update([(p,None,True) for p in paths],parallel=False)
    entries=[{'url':item.url,'timeout':item.timeout} for kind,path,items in manifest if kind=='testharness' for item in items]
    assert len(entries)==1 and entries[0]['timeout']=='long'
    (HERE/'MANIFEST.json').write_text(json.dumps(manifest.to_json(),indent=2,sort_keys=True)+'\n')
    (HERE/'ROSTER.json').write_text(json.dumps(roster,indent=2)+'\n')
    (HERE/'INPUTS.json').write_text(json.dumps({'resources':resources,'metadata':{},'prefs':{},'manifest':{'path':str((HERE/'MANIFEST.json').relative_to(ROOT)),'sha256':sha(HERE/'MANIFEST.json'),'bytes':(HERE/'MANIFEST.json').stat().st_size},'pages':1,'callbacks':3,'endings':1,'signatures':4,'observations':3,'new_fixture_browser_execution':False},indent=2)+'\n')
    result.update(success=True,lint_errors=0,callbacks=3,observations=3,pages=1,signatures=4,manifest_version=manifest.to_json()['version'],entries=entries)
finally:
    shutil.rmtree(scratch);result['scratch_removed']=not scratch.exists()
    (HERE/'PREPARE-RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))
