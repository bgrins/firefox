import json
import os
from pathlib import Path
import shutil
import sys
import subprocess
import tempfile

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WPT = ROOT / 'testing/web-platform/tests'
sys.path[:0] = [str(p) for p in (WPT / 'tools/third_party').iterdir() if p.is_dir()] + [str(WPT / 'tools'), str(WPT)]
from manifest.manifest import Manifest
from tools.lint import lint
import html5lib

inputs = json.loads((HERE / 'INPUTS.json').read_bytes())
roster = json.loads((HERE / 'ROSTER.json').read_bytes())
fixture = 'css/css-values/minmax-log-context-integration.html'
document = html5lib.parse((HERE / Path(fixture).name).read_text(), namespaceHTMLElements=False)
scripts = [node.text or '' for node in document.find('body').iter('script') if node.get('src') is None]
assert len(scripts) == 1
registered = subprocess.run(['node', '-e', "const vm=require('vm');let s='';process.stdin.on('data',x=>s+=x);process.stdin.on('end',()=>{const names=[];vm.runInNewContext(s,{test:(fn,name)=>names.push(name)});process.stdout.write(JSON.stringify(names));});"], input=scripts[0], text=True, capture_output=True, check=True)
assert json.loads(registered.stdout) == roster['expected_subtests']['/' + fixture]
assert len(json.loads(registered.stdout)) == 4
with tempfile.TemporaryDirectory(prefix='css-minmax-log-manifest-', dir='/private/tmp') as temporary:
    scratch = Path(temporary)
    for name, record in inputs['resources'].items():
        path = scratch / name
        path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / record['path'], path)
    manifest = Manifest(str(scratch), '/')
    manifest.update([(name, None, True) for name in sorted(inputs['resources'])], parallel=False)
    result = json.loads(json.dumps(manifest.to_json()))
    names = result['items']['testharness']['css']['css-values']
    assert set(names) == {Path(page).name for page in roster['expected_subtests']}
    assert all(len(record) == 2 and record[1][0] is None for record in names.values())
    previous = os.getcwd()
    try:
        os.chdir(scratch)
        assert lint.lint(str(scratch), [fixture], 'normal', jobs=1) == 0
    finally:
        os.chdir(previous)
    (HERE / 'SUBSET-MANIFEST.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
print(json.dumps({'genuine_WPT_manifest_generated':True, 'registered_pages':len(names),
                  'resources':len(inputs['resources']), 'temporary_scratch_removed':True,
                  'authored_integration_names_registered':4, 'integration_lint_errors':0,
                  'browser_executed':False}))
