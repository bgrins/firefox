import sys
sys.dont_write_bytecode = True
from pathlib import Path
import difflib
import hashlib
import json
import re
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
AUDIT = ROOT / 'artifacts/css-round-context-quotient-audit-v1'
native = 'servo/components/style/values/generics/calc.rs'
wpt = 'testing/web-platform/tests/css/css-values/round-context-quotient-precision.html'
before = (AUDIT/'source'/native).read_bytes()
after = (HERE/'candidate'/native).read_bytes()
fixture = (HERE/'candidate'/wpt).read_bytes()
patch = 'diff --git a/'+native+' b/'+native+'\n'+''.join(difflib.unified_diff(before.decode().splitlines(True),after.decode().splitlines(True),fromfile='a/'+native,tofile='b/'+native))
patch += 'diff --git a/'+wpt+' b/'+wpt+'\nnew file mode 100644\n'+''.join(difflib.unified_diff([],fixture.decode().splitlines(True),fromfile='/dev/null',tofile='b/'+wpt))
(HERE/'native-and-wpt.patch').write_text(patch)
inputs = json.loads((HERE/'INPUTS.json').read_text())
inputs['candidate_sha256']=hashlib.sha256(after).hexdigest()
inputs['fixture_sha256']=hashlib.sha256(fixture).hexdigest()
(HERE/'INPUTS.json').write_text(json.dumps(inputs,indent=2)+'\n')
steps=[]
with tempfile.TemporaryDirectory(prefix='round-context-package-') as temporary:
    scratch=Path(temporary)
    original=scratch/native;original.parent.mkdir(parents=True);original.write_bytes(before)
    for cmd in [['git','init','-q'],['git','apply','--check',str(HERE/'native-and-wpt.patch')],['git','apply',str(HERE/'native-and-wpt.patch')]]:
        subprocess.run(cmd,cwd=scratch,capture_output=True,check=True);steps.append(cmd[:3])
    assert original.read_bytes()==after and (scratch/wpt).read_bytes()==fixture
    for cmd in [['git','apply','--reverse','--check',str(HERE/'native-and-wpt.patch')],['git','apply','--reverse',str(HERE/'native-and-wpt.patch')]]:
        subprocess.run(cmd,cwd=scratch,capture_output=True,check=True);steps.append(cmd[:4])
    assert original.read_bytes()==before and not (scratch/wpt).exists()
    script='\n'.join(re.findall(r'<script>(.*?)</script>',fixture.decode(),re.S))
    js=scratch/'probe.js';js.write_text(script)
    subprocess.run(['node','--check',str(js)],capture_output=True,check=True)
    runner=scratch/'register.js';runner.write_text('const names=[]; globalThis.test=(_,name)=>names.push(name);\n'+script+'\nconsole.log(JSON.stringify(names));\n')
    names=json.loads(subprocess.run(['node',str(runner)],capture_output=True,text=True,check=True).stdout)
    assert len(names)==len(set(names))==14 and names[:6]==json.loads((AUDIT/'NAMES.json').read_text())
    (HERE/'NAMES.json').write_text(json.dumps(names,indent=2)+'\n')
with tempfile.TemporaryDirectory(prefix='round-context-format-') as temporary_format:
    formatting_path=Path(temporary_format)/'calc.rs';formatting_path.write_bytes(after)
    formatting=subprocess.run(['rustfmt','--config-path',str(HERE/'rustfmt.toml'),str(formatting_path)],capture_output=True,text=True)
    formatted=formatting_path.read_text().splitlines()
    original=after.decode().splitlines()
    changed=set()
    for tag,i,j,a,b in difflib.SequenceMatcher(a=before.decode().splitlines(),b=original).get_opcodes():
        if tag != 'equal': changed.update(range(a,b))
    format_edits=[]
    for tag,i,j,a,b in difflib.SequenceMatcher(a=original,b=formatted).get_opcodes():
        if tag != 'equal':
            assert not changed.intersection(range(i,max(i+1,j))), 'format edits changed candidate lines'
            format_edits.append({'before':[i,j],'after':[a,b]})
    assert formatting.returncode==0
(HERE/'rustfmt.log').write_text(formatting.stdout+formatting.stderr)
receipt={'git_transport':'PASS','exact_postimages':True,'reverse_restores_preimages':True,'git_commands':steps,'javascript_syntax':'PASS','inert_registered_tests':names,'rustfmt_exit':formatting.returncode,'changed_line_format':'PASS','existing_unrelated_format_edits':format_edits,'temporary_products_removed':not scratch.exists() and not formatting_path.exists(),'native_apply':False,'Gecko_build':False,'browser':False}
(HERE/'CHECK.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt,indent=2))
