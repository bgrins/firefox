import sys
assert sys.flags.isolated and sys.flags.no_site
import collections
import hashlib
import json
import re
import subprocess
import tempfile
from pathlib import Path, PurePosixPath
R=Path(__file__).resolve().parent

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def read(p):
    return json.loads(p.read_text())

def auth(root, expected=None):
    if expected:
        assert sha(root/'MANIFEST.json')==expected[0]
        assert sha(root/'FREEZE.json')==expected[1]
    raw=read(root/'MANIFEST.json')
    records=raw if isinstance(raw,list) else [{'path':k,'sha256':v} for k,v in raw.items()]
    names=set()
    for row in records:
        n=row['path'];p=PurePosixPath(n)
        assert n==str(p) and not p.is_absolute() and '..' not in p.parts and n not in names
        names.add(n)
        assert sha(root/n)==row['sha256'],n
    assert not any(p.is_symlink() for p in root.rglob('*'))
    assert {p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file()}==names|{'MANIFEST.json','FREEZE.json'}
    return len(names)

own=auth(R)
d=R.parent/'css-all-logical-order-independent-v1'
assert auth(d,('d38978cda2bff7f0cd4999f60f3cbc8bb660d2d0a196feb5eb250b8509e66123','be747f2f9933443ea0c41fc89e75f79dd00ad7e2d39b23bed7ea3d000074d6b5'))==41
b=R.parent/'css-all-logical-order-final-browser-v1'
assert auth(b,('50251068b381f99da4f34f6b23e42d477d4ac2749d9d0f2e4cd5c48cf8587ad1','1ba1bf48e70006eacc20523737bd975879bce3cf866e3dc1e0cb3f4603507610'))==41
e=R/'evidence'
source='servo/components/style/properties/declaration_block.rs'
wpt='testing/web-platform/tests/css/cssom/setproperty-all-logical-order.html'
assert sha(e/'declaration_block.candidate.rs')=='8474218db02f8787c212f47a08be33a468553b4ab809e774f2d26d4ae098812a'
for kind in ['original','candidate']:
    assert (e/f'declaration_block.{kind}.rs').read_bytes()==(d/f'evidence/candidate/declaration_block.{kind}.rs').read_bytes()
assert sha(b/'setproperty-all-logical-order.html')=='8df0a52b5856bb061aad9787d3abac3753becb9fe05a77aec116bd65c4262b8e'
all_pins={};outcomes={}
for phase in ['baseline','candidate']:
    pins=read(b/(phase+'-input.json'))
    assert pins==read(b/(phase+'-before.json'))==read(b/(phase+'-after.json'))
    all_pins[phase]=pins
    receipt=read(b/(phase+'-result.json'))
    assert receipt['stable_pins']
    assert receipt['raw_sha256']==sha(b/(phase+'-raw.jsonl'))
    assert receipt['console_sha256']==sha(b/(phase+'-console.log'))
    raw=[json.loads(x) for x in (b/(phase+'-raw.jsonl')).read_text().splitlines()]
    normalized=[{k:v for k,v in x.items() if k in ['action','test','subtest','status','expected','message']} for x in raw if x.get('action') in ['test_status','test_end']]
    assert normalized==receipt['rows']
    keyed={(x['action'],x['test'],x.get('subtest')):x for x in normalized}
    assert len(keyed)==len(normalized)==105
    outcomes[phase]=keyed
    assert pins['fixed'][wpt]==sha(b/'setproperty-all-logical-order.html')
assert all_pins['baseline']['tests']==all_pins['candidate']['tests']
assert all_pins['baseline']['fixed'].keys()==all_pins['candidate']['fixed'].keys()
assert {k for k in all_pins['baseline']['fixed'] if all_pins['baseline']['fixed'][k]!=all_pins['candidate']['fixed'][k]}=={source}
assert all_pins['baseline']['fixed'][source]==sha(e/'declaration_block.original.rs')
assert all_pins['candidate']['fixed'][source]==sha(e/'declaration_block.candidate.rs')
assert all_pins['baseline']['binaries'].keys()==all_pins['candidate']['binaries'].keys()
assert len(all_pins['baseline']['binaries'])==2
assert all(all_pins['baseline']['binaries'][k]!=all_pins['candidate']['binaries'][k] for k in all_pins['baseline']['binaries'])
assert outcomes['baseline'].keys()==outcomes['candidate'].keys()
changes={k for k in outcomes['baseline'] if outcomes['baseline'][k]!=outcomes['candidate'][k]}
expected={f'{family}: {value}, priority {json.dumps(priority)}' for family in ['all expansion order','equal-value all reordering'] for value in ['initial','inherit','revert','var(--all)'] for priority in ['','important']}
assert len(changes)==16 and {k[2] for k in changes}==expected
for k in changes:
    assert outcomes['baseline'][k]['status']=='FAIL' and outcomes['candidate'][k]['status']=='PASS'
for phase,counts in [('baseline',{'PASS':85,'FAIL':16,'OK':4}),('candidate',{'PASS':101,'OK':4})]:
    assert dict(collections.Counter(x['status'] for x in outcomes[phase].values()))==counts
new=[x for x in outcomes['candidate'].values() if x['action']=='test_status' and x['test'].endswith('/setproperty-all-logical-order.html')]
assert len(new)==40 and all(x['status']=='PASS' for x in new)
assert read(b/'candidate-result.json')['exit_code']==0
for row in read(b/'candidate-build-result.json'):
    assert row['exit_code']==0
    log='candidate-'+('force-rust' if row['phase']=='force-rust' else 'link')+'.log'
    assert row['log_sha256']==sha(b/log)
assert read(b/'candidate-build-before.json')['fixed']==read(b/'candidate-build-after.json')['fixed']==all_pins['candidate']['fixed']
assert read(b/'candidate-build-after.json')['binaries']==all_pins['candidate']['binaries']
assert (b/'candidate-link.log').read_text().count("KeyError: 'export'")==4
assert read(b/'lint-result.json')['exit_code']==0
assert read(e/'FORMAT-CHECK.json')['whole_file_stable']
patch=e/'native-wpt.patch'
assert sha(patch)=='e2a185b68d6a3ad483ebce3f9cc77268bc6684d70ad406d40db4ef5e8466db3c'
assert read(e/'PATCH-INPUT.json')['paths']==[source,wpt]
standalone=read(e/'STANDALONE-CHECK.json')
assert standalone['patch_sha256']==sha(patch) and standalone['same_patch_applies_and_reverses']
assert standalone['isolated_base_build_browser']=='NOT_RUN'
with tempfile.TemporaryDirectory(prefix='all-native-independent-') as temp:
    root=Path(temp);target=root/source;target.parent.mkdir(parents=True)
    target.write_bytes((e/'declaration_block.original.rs').read_bytes())
    (root/wpt).parent.mkdir(parents=True)
    for reverse in [False,True]:
        command=['patch','--batch','-p1','-i',str(patch)]+(['-R'] if reverse else [])
        p=subprocess.run(command,cwd=root,capture_output=True,text=True)
        assert p.returncode==0,p.stdout+p.stderr
        assert target.read_bytes()==(e/f'declaration_block.{"original" if reverse else "candidate"}.rs').read_bytes()
        if reverse:assert not (root/wpt).exists()
        else:assert (root/wpt).read_bytes()==(b/'setproperty-all-logical-order.html').read_bytes()
print(json.dumps({'review_inputs':own,'browser_inputs':41,'discovery_inputs':41,'outcome_keys':105,'improved':16,'unchanged':89,'new_PASS':40,'existing_PASS':61,'harness_OK':4,'patch_apply_reverse':'PASS','recommendation':'accept narrow native/WPT repair'}))
