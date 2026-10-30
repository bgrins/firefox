import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
PREVIOUS = ROOT / 'artifacts/css-contextual-duration-regression-plan-v1'
WPT = ROOT / 'testing/web-platform/tests'
sys.path[:0] = [str(p) for p in (WPT / 'tools/third_party').iterdir() if p.is_dir()] + [str(WPT / 'tools'), str(WPT)]
import html5lib
from manifest.manifest import Manifest
from tools.lint import lint

for source, expected in json.loads((PACKAGE / 'REFERENCES.json').read_text()).items():
    assert hashlib.sha256((ROOT / source).read_bytes()).hexdigest() == expected
name = 'animation-duration-self-feedback-observation.tentative.html'
path = 'css/css-animations/' + name
source = (PACKAGE / name).read_text()
document = html5lib.parse(source, namespaceHTMLElements=False)
scripts = [node.text or '' for node in document.iter('script')
           if not node.get('src') and node.get('type') != 'application/json']
assert len(scripts) == 1
program = "const vm=require('vm');let s='';process.stdin.on('data',x=>s+=x);process.stdin.on('end',()=>{const names=[];vm.runInNewContext(s,{promise_test:(fn,name)=>names.push(name)});process.stdout.write(JSON.stringify(names));});"
result = subprocess.run(['node', '-e', program], input=scripts[0], text=True,
                        capture_output=True, check=True)
names = json.loads(result.stdout)
old_names = json.loads((PREVIOUS / 'ROSTER.json').read_text())['pages']['/' + path]['names']
assert names[:2] == old_names and len(names) == len(set(names)) == 3
assert names[-1] == 'Observation only: zero-start self-dependent font duration completes eight samples'
assert 'observe(t, false)' in source and 'observe(t, true)' in source and 'observe(t, false, 0)' in source
resources = {node.get('src') for node in document.iter('script') if node.get('src')}
assert resources == {'/resources/testharness.js', '/resources/testharnessreport.js'}
for resource in resources:
    assert (PREVIOUS / 'capture/tests' / resource.lstrip('/')).is_file()
with tempfile.TemporaryDirectory(prefix='duration-feedback-static-') as temporary:
    scratch = Path(temporary)
    shutil.copytree(PREVIOUS / 'capture/tests', scratch, dirs_exist_ok=True)
    (scratch / path).write_text(source)
    (scratch / 'lint.ignore').write_text('')
    pages = [page.lstrip('/') for page in json.loads((PREVIOUS / 'CAPTURE.json').read_text())['pages']]
    manifest = Manifest(str(scratch), '/')
    manifest.update([(page, None, True) for page in pages], parallel=False)
    serialized = json.loads(json.dumps(manifest.to_json()))
    previous = json.loads((PREVIOUS / 'SUBSET-MANIFEST.json').read_text())
    entry = serialized['items']['testharness']['css']['css-animations'][name]
    assert entry[0] != previous['items']['testharness']['css']['css-animations'][name][0]
    previous['items']['testharness']['css']['css-animations'][name] = entry
    assert previous == serialized
    (PACKAGE / 'SUBSET-MANIFEST.json').write_text(json.dumps(serialized, indent=2, sort_keys=True) + '\n')
    directory = os.getcwd()
    try:
        os.chdir(scratch)
        assert lint.lint(str(scratch), [path], 'normal', jobs=1) == 0
    finally:
        os.chdir(directory)
record = {'registered_names': names, 'previous_two_names_unchanged': True,
          'old_calls_retain_default_from_16': True, 'new_call_from_zero': True,
          'callbacks_executed': False, 'lint_errors': 0,
          'genuine_manifest_exact_single_entry_delta': True, 'scratch_removed': True}
(PACKAGE / 'CHECK.json').write_text(json.dumps(record, indent=2, sort_keys=True) + '\n')
print(json.dumps(record))
