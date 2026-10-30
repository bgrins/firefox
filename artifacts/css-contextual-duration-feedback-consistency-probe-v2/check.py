import copy
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
OLD=ROOT/'artifacts/css-contextual-duration-feedback-consistency-probe-v1'
WPT=ROOT/'testing/web-platform/tests'
sys.path[:0]=[str(p) for p in (WPT/'tools/third_party').iterdir() if p.is_dir()]+[str(WPT/'tools'),str(WPT),str(ROOT/'third_party/python/pyyaml/lib')]
import html5lib
from manifest.manifest import Manifest
from tools.lint import lint

sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(OLD/'FILES.json')=='5b34013f07004069141d5da229c9f4b1bdfb39cb659e52c9700188a9fe290e52'
for name,pin in json.loads((OLD/'FILES.json').read_bytes()).items():assert sha(OLD/name)==pin
page='animation-duration-feedback-consistency-observation.tentative.html'
helper='duration-feedback-discriminator-record.py'
before=(OLD/page).read_text();after=(HERE/page).read_text()
line='      outline: 0px solid transparent;\n'
assert after.count(line)==1 and after.replace(line,'')==before
dom=html5lib.parse(after,namespaceHTMLElements=False)
assert dom.find('body').find('script') is not None
script=next(node.text for node in dom.iter('script') if not node.get('src'))
program="const vm=require('vm');let s='';process.stdin.on('data',x=>s+=x);process.stdin.on('end',()=>{const names=[];vm.runInNewContext(s,{promise_test:(fn,name)=>names.push(name)});process.stdout.write(JSON.stringify(names));});"
names=json.loads(subprocess.run(['node','-e',program],input=script,text=True,capture_output=True,check=True).stdout)
assert names==json.loads((OLD/'CHECK.json').read_bytes())['registered_names']
with tempfile.TemporaryDirectory(prefix='duration-outline-manifest-') as temporary:
    scratch=Path(temporary);folder=scratch/'css/css-animations';folder.mkdir(parents=True)
    shutil.copyfile(HERE/page,folder/page);shutil.copyfile(OLD/helper,folder/helper)
    (scratch/'lint.ignore').write_text('')
    paths=['css/css-animations/'+n for n in [page,helper]]
    manifest=Manifest(str(scratch),'/');manifest.update([(p,None,True) for p in paths],parallel=False)
    actual=json.loads(json.dumps(manifest.to_json()))
    expected=json.loads((OLD/'SUBSET-MANIFEST.json').read_bytes())
    expected['items']['testharness']['css']['css-animations'][page][0]=actual['items']['testharness']['css']['css-animations'][page][0]
    assert actual==expected
    (HERE/'SUBSET-MANIFEST.json').write_text(json.dumps(actual,indent=2,sort_keys=True)+'\n')
    cwd=os.getcwd()
    try:
        os.chdir(scratch)
        assert lint.lint(str(scratch),paths,'normal',jobs=1)==0
    finally:os.chdir(cwd)
result={'registered_names':names,'exact_one_line_addition':True,'observer_js_unchanged':True,
        'handler_unchanged':True,'manifest_only_page_body_hash_changed':True,'lint_errors':0,
        'browser_or_http_server_executed':False,'scratch_removed':True}
(HERE/'CHECK.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print(json.dumps(result,indent=2))
