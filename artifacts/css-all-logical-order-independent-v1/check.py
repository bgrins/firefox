import sys
assert sys.flags.isolated and sys.flags.no_site
import collections
import hashlib
import json
import re
import subprocess
import tempfile
from pathlib import Path, PurePosixPath
R = Path(__file__).resolve().parent

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def read(p):
    return json.loads(p.read_text())

manifest = read(R / 'MANIFEST.json')
for n,h in manifest.items():
    rel = PurePosixPath(n)
    assert str(rel) == n and not rel.is_absolute() and '..' not in rel.parts
    assert sha(R / n) == h, n
assert not any(p.is_symlink() for p in R.rglob('*'))
assert {p.relative_to(R).as_posix() for p in R.rglob('*') if p.is_file()} == set(manifest) | {'MANIFEST.json', 'FREEZE.json'}
for row in read(R / 'SOURCE-INPUTS.json'):
    assert sha(R / 'source' / row['path']) == row['sha256']
e = R / 'evidence'
b = e / 'browser'
external = read(b / 'MANIFEST.json')
assert len(external) == 14
for n,h in external.items():
    path = R / n if n.startswith('source/') else b / n
    assert sha(path) == h
pins = read(b / 'baseline-input.json')
assert pins == read(b / 'baseline-before.json') == read(b / 'baseline-after.json')
result = read(b / 'baseline-result.json')
assert result['stable_pins'] and result['exit_code'] == 1
assert result['raw_sha256'] == sha(b / 'baseline-raw.jsonl')
assert result['console_sha256'] == sha(b / 'baseline-console.log')
rows = [json.loads(x) for x in (b / 'baseline-raw.jsonl').read_text().splitlines()]
rows = [x for x in rows if x.get('action') in ('test_status','test_end')]
assert len(rows) == len({(x['action'],x['test'],x.get('subtest')) for x in rows}) == 25
values = ['initial','inherit','revert','var(--all)']
expected = {f'{family}: {value}, priority {json.dumps(priority)}': ('FAIL' if family == 'all expansion order' else 'PASS') for family in ['all expansion order','longhand reordering control','declaration-list control'] for value in values for priority in ['', 'important']}
assert {x['subtest']:x['status'] for x in rows if x['action']=='test_status'} == expected
assert [x['status'] for x in rows if x['action']=='test_end'] == ['OK']
for x in rows:
    if x['status'] == 'FAIL':
        assert 'seed padding-top,padding-block-start' in x['message']
        assert 'expected array ["padding-block-start", "padding-top"] got ["padding-top", "padding-block-start"]' in x['message']
source_matches = []
for row in read(R / 'SOURCE-INPUTS.json'):
    if row['path'] in pins['fixed']:
        assert row['sha256'] == pins['fixed'][row['path']]
        source_matches.append(row['path'])
assert 'servo/components/style/properties/declaration_block.rs' in source_matches
assert 'servo/components/style/properties/data.py' in source_matches
assert sha(b / 'setproperty-all-logical-order.html') in pins['fixed'].values()
primary = e / 'primary'
assert read(primary / 'issue5741.json')['state'] == 'open'
pr = read(primary / 'pr2516.json')
assert pr['merged'] and pr['merged_at'] == '2018-04-11T13:12:17Z'
comments = read(primary / 'issue1898-comments.json')
assert any('RESOLVED: Make it so that setters to the .style api are appended rather than put in place' in c['body'] for c in comments)
html = (primary / 'cssom.html').read_text()
for anchor in ['dom-cssstyledeclaration-setproperty','set-a-css-declaration','dom-cssstyledeclaration-item']:
    assert 'id="' + anchor + '"' in html
candidate = e / 'candidate'
old = (candidate / 'declaration_block.original.rs').read_text()
new = (candidate / 'declaration_block.candidate.rs').read_text()
assert (R / 'source/servo/components/style/properties/declaration_block.rs').read_text() == old
assert sha(candidate / 'declaration_block.candidate.rs') == '8474218db02f8787c212f47a08be33a468553b4ab809e774f2d26d4ae098812a'
a=old.index('                .map(|declaration| {')+len('                .map(|declaration| {')
z=old.index('\n                })\n                .inspect',a)
old_body=old[a:z]
a=new.index('    fn declaration_update(')
a=new.index('    ) -> DeclarationUpdate {',a)+len('    ) -> DeclarationUpdate {')
z=new.index('\n    }',a)
new_body=new[a:z]
assert re.sub(r'\s+','',old_body)==re.sub(r'\s+','',new_body)
with tempfile.TemporaryDirectory(prefix='all-order-independent-') as temp:
    target=Path(temp)/'servo/components/style/properties/declaration_block.rs'
    target.parent.mkdir(parents=True)
    target.write_text(old)
    for reverse in [False,True]:
        command=['patch','--batch','-p1','-i',str(candidate/'native.patch')]+(['-R'] if reverse else [])
        r=subprocess.run(command,cwd=temp,capture_output=True,text=True)
        assert r.returncode==0,r.stdout+r.stderr
        assert target.read_text()==(old if reverse else new)
print(json.dumps({'review_inputs':len(manifest),'browser_inputs':14,'subtests':24,'FAIL':8,'PASS':16,'OK':1,'stable_fixed_pins':len(pins['fixed']),'source_runtime_matches':source_matches,'candidate_normal_body':'whitespace-only transfer','candidate_patch_apply_reverse':'PASS','candidate_runtime':'pending','recommendation':'valid observable ordering bug; candidate design sound, final repair gate separate'},indent=2))
