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
fixture = 'css/css-values/literal-negative-zero.html'
document = html5lib.parse((ROOT / inputs['resources'][fixture]['path']).read_text(), namespaceHTMLElements=False)
external_scripts = [node.get('src') for node in document.iter('script') if node.get('src')]
assert external_scripts == ['/resources/testharness.js', '/resources/testharnessreport.js']
assert all(src.lstrip('/') in inputs['resources'] for src in external_scripts)
scripts = [node.text or '' for node in document.iter('script') if node.get('src') is None]
assert len(scripts) == 1
registered = subprocess.run(['node', '-e', "const vm=require('vm');let s='';process.stdin.on('data',x=>s+=x);process.stdin.on('end',()=>{const names=[];vm.runInNewContext(s,{test:(fn,name)=>names.push(name)});process.stdout.write(JSON.stringify(names));});"], input=scripts[0], text=True, capture_output=True, check=True)
assert json.loads(registered.stdout) == [row['name'] for row in roster['pages']['/' + fixture]]
assert len(json.loads(registered.stdout)) == 6
with tempfile.TemporaryDirectory(prefix='css-literal-zero-manifest-', dir='/private/tmp') as temporary:
    scratch = Path(temporary)
    for name, record in inputs['resources'].items():
        path = scratch / name
        path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / record['path'], path)
    manifest = Manifest(str(scratch), '/')
    manifest.update([(name, None, True) for name in sorted(inputs['resources'])], parallel=False)
    result = json.loads(json.dumps(manifest.to_json()))
    names = result['items']['testharness']['css']['css-values']
    assert set(names) == {Path(page).name for page in roster['pages']}
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
                  'authored_literal_zero_names_registered':6, 'fixture_lint_errors':0,
                  'browser_executed':False}))
