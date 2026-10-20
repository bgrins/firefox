import sys
if not (sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize):
    raise RuntimeError('use python3 -I -S without optimization')
import hashlib,json,re
from pathlib import Path
root=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
data=json.loads((root/'SOURCE-IDENTITIES.json').read_text())
for n,h in data['sources'].items():
    if sha(root/n)!=h:raise RuntimeError(n)
if sha(root/'css-syntax-3.html')!=data['spec_sha256']:raise RuntimeError('spec changed')
for n,h in data['predecessor_pins'].items():
    if n=='check.py':continue
    if sha(root/'predecessor'/n)!=h:raise RuntimeError('predecessor seal')
manifest=json.loads((root/'predecessor/FILES.json').read_text())
for row in manifest:
    p=root/'predecessor'/row['path']
    if p.is_file() and sha(p)!=row['sha256']:raise RuntimeError('copied predecessor input')
assert (root/'searchfox-rules.rs').read_bytes()==(root/'local-rules_and_declarations.rs').read_bytes()
def body(text):
    start=text.index("pub fn parse_until_after<'i,")
    return text[start:text.index("pub fn parse_nested_block<'i,",start)]
assert body((root/'searchfox-parser.rs').read_text())==body((root/'local-parser.rs').read_text())
pins={r['path']:r['sha256'] for r in manifest}
for short in ['parser','tokenizer']:
    assert sha(root/('local-'+short+'.rs'))==pins['source/third_party__rust__cssparser__src__'+short+'.rs']
ids=set(re.findall(r'\bid="([^"]+)"',(root/'css-syntax-3.html').read_text()))
for anchor in ['consume-a-declaration','consume-a-qualified-rule','consume-a-blocks-contents','consume-simple-block']:assert anchor in ids
print(json.dumps({'status':'PASS_STATIC_SOURCE_ACCOUNTING','new_bug_established':False,'new_formal_theorem':False,'until_after_upstream_local_body_equal':True,'source_parser_tokenizer_matches_accepted_predecessor':True,'next_contract':'delimiter ownership and direct ASCII advance followed by curly recovery'}))
