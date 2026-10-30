import hashlib
import json
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WPT = ROOT / 'testing/web-platform/tests'
sys.path[:0] = [str(p) for p in (WPT / 'tools/third_party').iterdir() if p.is_dir()] + [str(WPT / 'tools'), str(WPT), str(ROOT / 'third_party/python/pyyaml/lib')]

def audit(event, args):
    if event == 'subprocess.Popen':
        assert Path(args[0]).name == 'node'

sys.addaudithook(audit)
import html5lib
from manifest.manifest import Manifest
from tools.lint import lint

tests = HERE / 'tests'
relative = 'css/css-text/white-space/nowrap-inline-break-policies.html'
data = (tests / relative).read_bytes()
assert hashlib.sha256(data).hexdigest() == '3c390a8c21c898e0202c5fdb754a6f8a842a0bf6447ebaa8a7e15b9ff05b6a68'
dom = html5lib.parse(data, namespaceHTMLElements=False)
scripts = [node.text for node in dom.iter('script') if not node.get('src')]
program = "const vm=require('vm');let input='';process.stdin.on('data',x=>input+=x);process.stdin.on('end',()=>{const names=[];const context=vm.createContext({document:{fonts:{load:()=>null}},promise_test:(_,name)=>names.push(name)});for(const source of JSON.parse(input))vm.runInContext(source,context);process.stdout.write(JSON.stringify(names));});"
names = json.loads(subprocess.run(['node', '-e', program], input=json.dumps(scripts), text=True, capture_output=True, check=True).stdout)
assert len(names) == len(set(names)) == 169
errors = lint.check_path(str(tests), relative) + lint.check_file_contents(str(tests), relative)
assert not errors, errors
manifest = Manifest(str(tests), '/')
manifest.update([(relative, None, True)], parallel=False)
for name, value in [('MANIFEST.json', manifest.to_json()), ('ROSTER.json', {'/' + relative: names}), ('STATIC-CHECK.json', {'callbacks': 169, 'pages': 1, 'expected_signatures': 170, 'wpt_lint_errors': errors, 'genuine_manifest': True, 'browser_run': False, 'native_build': False})]:
    (HERE / name).write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')
print(json.dumps({'callbacks': len(names), 'wpt_lint_errors': errors, 'genuine_manifest': True}))
