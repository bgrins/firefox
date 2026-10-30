import difflib,json,subprocess,sys,tempfile
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
WPT=ROOT/'testing/web-platform/tests'
sys.path[:0]=[str(p) for p in (WPT/'tools/third_party').iterdir() if p.is_dir()]+[str(WPT/'tools'),str(WPT),str(ROOT/'third_party/python/pyyaml/lib')]
import html5lib
from manifest.manifest import Manifest
from tools.lint import lint
page='css/css-properties-values-api/registered-prioritary-selection.tentative.html'
base=(HERE/'base.html').read_text();candidate=(HERE/'candidate.html').read_text()
assert base==(ROOT/'artifacts/css-prioritary-selection-preservation-probe-v1/tests'/page).read_text()
expected=base.replace('<script src="/resources/testharnessreport.js"></script>','<script src="/resources/testharnessreport.js"></script>\n<script src="/__research__/zoom/record.js"></script>').replace('    const diagnostic = JSON.stringify(row);','    if (row.diagnosticOnly) await window.capturePrioritaryZoom(row);\n    const diagnostic = JSON.stringify(row);')
assert candidate==expected
assert (HERE/'FIXTURE-DELTA.patch').read_text()==''.join(difflib.unified_diff(base.splitlines(True),candidate.splitlines(True),fromfile='a/'+page,tofile='b/'+page))
with tempfile.TemporaryDirectory(prefix='css-zoom-fixture-',dir='/private/tmp') as directory:
    tests=Path(directory);target=tests/page;target.parent.mkdir(parents=True);target.write_text(candidate)
    for name in ['record.js','receive.py']:
        q=tests/'__research__/zoom'/name;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes((HERE/name).read_bytes())
    errors=lint.check_path(str(tests),page)+lint.check_file_contents(str(tests),page)
    assert not errors,errors
    manifest=Manifest(str(tests),'/');manifest.update([(str(p.relative_to(tests)),None,True) for p in tests.rglob('*') if p.is_file()],parallel=False)
    (HERE/'MANIFEST.json').write_text(json.dumps(manifest.to_json(),indent=2,sort_keys=True)+'\n')
assert not Path(directory).exists()
dom=html5lib.parse(candidate,namespaceHTMLElements=False)
scripts=[n.text for n in dom.iter('script') if not n.get('src')]
program="const vm=require('vm');let s='';process.stdin.on('data',x=>s+=x);process.stdin.on('end',()=>{let names=[];const c=vm.createContext({window:{},promise_test:(_,name)=>names.push(name)});for(const x of JSON.parse(s))vm.runInContext(x,c);process.stdout.write(JSON.stringify(names));});"
names=json.loads(subprocess.run(['node','-e',program],input=json.dumps(scripts),text=True,capture_output=True,check=True).stdout)
original=json.loads((ROOT/'artifacts/css-prioritary-selection-preservation-probe-v1/ROSTER.json').read_text())['/'+page]
assert names==original
(HERE/'ROSTER.json').write_text(json.dumps({'/'+page:names},indent=2)+'\n')
print(json.dumps({'exact_two_insertions':True,'same_eight_names':True,'genuine_manifest':True,'lint_errors':0,'scratch_removed':True,'callback_execution':False}))
