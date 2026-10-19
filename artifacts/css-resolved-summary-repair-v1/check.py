import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parent
parser = argparse.ArgumentParser()
parser.add_argument('--scanner', action='store_true')
parser.add_argument('--output', type=Path)
args = parser.parse_args()
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
freeze = json.loads((ROOT / 'FREEZE.json').read_text())
assert sha(ROOT / 'MANIFEST.json') == freeze['manifest_sha256']
manifest = json.loads((ROOT / 'MANIFEST.json').read_text())
for name, digest in manifest.items():
    path = ROOT / name
    assert not path.is_symlink() and path.is_file() and sha(path) == digest, name
out = args.output.resolve() if args.output else Path(tempfile.mkdtemp(prefix='resolved-summary-check-'))
out.mkdir(parents=True, exist_ok=True)
commands = []
def run(command, cwd):
    result = subprocess.run(command, cwd=cwd, capture_output=True, text=True)
    commands.append({'command':command, 'cwd':str(cwd), 'exit':result.returncode,
                     'stdout':result.stdout, 'stderr':result.stderr})
    (out / 'commands.json').write_text(json.dumps(commands, indent=2)+'\n')
    assert result.returncode == 0, commands[-1]
    return result.stdout
copy = out / 'source'
assert not copy.exists(), 'Use a fresh output directory'
for name in manifest:
    dst = copy / name
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(ROOT / name, dst)
run(['python3',str(copy/'prepare.py')],copy)
assert sha(copy/'candidate/custom_properties.rs') == sha(ROOT/'candidate/custom_properties.rs')
assert sha(copy/'native.patch') == sha(ROOT/'native.patch')
run(['python3',str(copy/'make-wpt.py')],copy)
assert sha(copy/'wpt/attr-resolved-unit-dependencies.html') == sha(ROOT/'wpt/attr-resolved-unit-dependencies.html')
s = (copy/'candidate/custom_properties.rs').read_text()
o = (copy/'original/custom_properties.rs').read_text()
helper = s[s.index('fn resolved_token_dependencies('):s.index('\nimpl VariableValue {')]
audited = (copy/'evidence/audited-scanner-proposal.rs').read_text()
audited = audited[audited.index('fn resolved_unit_flags('):].replace('resolved_unit_flags','resolved_token_dependencies')
without_comment = lambda x: re.sub(r'\s*//[^\n]*', '', x).strip()
assert without_comment(helper) == without_comment(audited)
assert s.count('VariableValue::new_resolved(') == 2
constructor = s[s.index('    fn new_resolved('):s.index('    fn push(',s.index('    fn new_resolved('))]
restored = s.replace(helper+'\n','').replace(constructor,'').replace('VariableValue::new_resolved(', 'VariableValue::new(')
assert restored == o
assert 'value.references.flags = flags;' in constructor
assert 'Self::new(css, url_data, first_token_type, last_token_type)' in constructor
apply = out/'apply'
target = apply/'servo/components/style/custom_properties.rs'
target.parent.mkdir(parents=True)
shutil.copyfile(copy/'original/custom_properties.rs',target)
run(['patch','--batch','-p1','-i',str(copy/'native.patch')],apply)
assert sha(target) == sha(copy/'candidate/custom_properties.rs')
run(['patch','--batch','-R','-p1','-i',str(copy/'native.patch')],apply)
assert sha(target) == sha(copy/'original/custom_properties.rs')
html = (copy/'wpt/attr-resolved-unit-dependencies.html').read_text()
js = re.findall(r'<script>(.*?)</script>',html,re.S)
assert len(js)==1
script = out/'wpt.js'
script.write_text(js[0])
run(['node','--check',str(script)],out)
script.write_text('global.CSS={registerProperty(){}};let names=[];global.test=(f,n)=>names.push(n);\n'+js[0]+'\nif(names.length!==21 || new Set(names).size!==21)process.exit(1);console.log(JSON.stringify(names));')
run(['node',str(script)],out)
if args.scanner:
    run(['python3',str(copy/'scanner/build.py'),'--output',str(out/'scanner-build')],out)
receipt = {'authenticated':len(manifest),'native_generator':'PASS','helper_audit_match':'PASS',
 'exact_two_sinks_and_other_bytes':'PASS','apply_reverse':'PASS','wpt_syntax_and_registration':21,
 'wpt_callbacks_executed':False,'scanner':'PASS' if args.scanner else 'NOT RUN',
 'native_gecko_compilation':'NOT RUN','browser':'NOT RUN'}
(out/'RESULT.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt))
