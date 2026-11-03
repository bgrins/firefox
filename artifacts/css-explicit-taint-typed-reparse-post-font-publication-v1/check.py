import copy
import difflib
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PARENT = ROOT / 'artifacts/css-explicit-taint-typed-reparse-publication-v1'
sha = lambda body: hashlib.sha256(body).hexdigest()
read = lambda path: json.loads(path.read_bytes())
policy = read(HERE / 'POLICY.json')
assert policy['bindings'] is policy['pair_binding'] is policy['runtime_output'] is policy['stage'] is None
assert policy['enabled_modes'] == []
binding = read(HERE / 'CHAIN-BINDING.json')
assert policy['publication_chain'] == binding
assert all(binding[k] is None for k in ('cancellation_research', 'cancellation_receipt', 'cancellation_installation', 'cancellation_delivery'))
for path, pin in policy['references'].items():
    assert sha((ROOT / path).read_bytes()) == pin, path
for name in ('evidence.py', 'transform.py', 'delivery.py', 'STAGES.json', 'native.patch'):
    assert (HERE/name).read_bytes() == (PARENT/name).read_bytes()
for name in ('run.py', 'publish.py', 'POLICY.json', 'PAIR-BINDING.json'):
    expected = ''.join(difflib.unified_diff((PARENT/name).read_text().splitlines(True), (HERE/name).read_text().splitlines(True), fromfile='prior/'+name, tofile='post-font/'+name))
    assert (HERE/(name+'.diff')).read_text() == expected
old, new = (PARENT/'run.py').read_text(), (HERE/'run.py').read_text()
marker = "    controls = {n: (RUNTIME / n).read_bytes()"
assert old[old.index(marker):].replace('css-explicit-taint-typed-reparse-publication-', 'css-explicit-taint-typed-reparse-post-font-publication-') == new[new.index(marker):]
for path in HERE.glob('*.py'):
    compile(path.read_bytes(), str(path), 'exec')
acceptance = ROOT / 'artifacts/css-explicit-taint-typed-reparse-acceptance-v1'
acceptance_manifest = read(acceptance/'FILES.json')
for name, row in acceptance_manifest.get('files', acceptance_manifest).items():
    assert sha((acceptance/name).read_bytes()) == row['sha256']
assert (HERE/'PAIR-BINDING.json').read_bytes() == (acceptance/'PAIR-BINDING.json').read_bytes()
assert read(acceptance/'CHECK.json')['actual_outcome_replayed'] is True
spec = importlib.util.spec_from_file_location('checked_fixed_chain', HERE/'chain.py')
chain = importlib.util.module_from_spec(spec)
spec.loader.exec_module(chain)
negatives = []
def reject(label, function):
    try:
        function()
    except AssertionError:
        negatives.append(label)
    else:
        raise AssertionError('Accepted ' + label)
reject('pending cancellation before Git', lambda: chain.verify(ROOT, lambda *a: (_ for _ in ()).throw(RuntimeError('Unexpected Git')), 'unused', binding, chain.BASE, {}, 'pending'))
font_stage, = read(ROOT/binding['font_stages']['path'])['stages']
cancel_stage, = read(ROOT/binding['cancellation_stages']['path'])['stages']
cancel_research, cancel, head = '9'*40, 'a'*40, 'b'*40
parents = {chain.FONT_RESEARCH:chain.BASE, chain.FONT:chain.FONT_RESEARCH,
           chain.POST_FONT_RESEARCH:chain.FONT, cancel_research:chain.POST_FONT_RESEARCH,
           cancel:cancel_research, head:cancel}
intervals = {(chain.BASE,chain.FONT_RESEARCH):[chain.FONT_RESEARCH],
             (chain.FONT,chain.POST_FONT_RESEARCH):[chain.POST_FONT_RESEARCH],
             (chain.POST_FONT_RESEARCH,cancel_research):[cancel_research], (cancel,head):[head]}
diffs = {(parent,rev):['artifacts/research.json'] for rev,parent in parents.items()}
diffs[(chain.FONT_RESEARCH,chain.FONT)] = sorted(font_stage['files'])
diffs[(cancel_research,cancel)] = sorted(cancel_stage['files'])
blobs = {}
source = ROOT/'artifacts/css-root-font-cancellation-selective-handoff-fix-v1'
for stage, commit, parent, folder in [(font_stage,chain.FONT,chain.FONT_RESEARCH,'base'),
                                      (cancel_stage,cancel,cancel_research,'parent')]:
    for path, row in stage['files'].items():
        body = (ROOT/row['path']).read_bytes(); assert sha(body) == row['sha256']
        blobs[commit+':'+path] = body
    for path, pin in stage['head_preimages'].items():
        body = (source/folder/path).read_bytes(); assert sha(body) == pin
        blobs[parent+':'+path] = body
for revision in (cancel,head):
    blobs[revision+':'+chain.ROLE] = (ROOT/'artifacts/css-explicit-attribute-taint-typed-reparse-fix-v1/base'/chain.ROLE).read_bytes()
state = {'parents':parents,'intervals':intervals,'diffs':diffs,'blobs':blobs,'present':set(),'bad_signatures':set()}
def git(*args):
    if args[0] == '-c':
        assert args[2] == 'verify-commit' and args[3] not in state['bad_signatures']
        return b''
    if args[:2] == ('merge-base','--is-ancestor'):
        assert (args[2],args[3]) in state['intervals']; return b''
    if args[:2] == ('rev-list','--parents'):
        if args[2:4] == ('-n','1'):
            rev=args[4];return (rev+' '+state['parents'][rev]+'\n').encode()
        start,end=args[2].split('..')
        return ''.join(rev+' '+state['parents'][rev]+'\n' for rev in state['intervals'][(start,end)]).encode()
    if args[:2] == ('diff','--name-only'):
        return '\n'.join(state['diffs'][(args[2],args[3])]).encode()
    if args[0] == 'show':return state['blobs'][args[1]]
    if args[0] == 'ls-tree':return b'exists' if (args[1],args[3]) in state['present'] else b''
    raise AssertionError('Unexpected Git shape: '+repr(args))
original_state = copy.deepcopy(state)
with tempfile.TemporaryDirectory(prefix='typed-post-font-chain-', dir='/private/tmp') as temporary:
    scratch=Path(temporary); b=copy.deepcopy(binding)
    def save(path, value):
        target=scratch/path;target.parent.mkdir(parents=True,exist_ok=True)
        body=json.dumps(value,sort_keys=True).encode();target.write_bytes(body)
        return {'path':path,'sha256':sha(body)}
    for name,record in b.items():
        if isinstance(record,dict):
            p=scratch/record['path'];p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((ROOT/record['path']).read_bytes())
    cancel_parent={'committed':True,'head':cancel_research,'parent':chain.POST_FONT_RESEARCH,
                   'signature_verified':True,'accepted_fix_increment':0,'native_working_diff_preserved':True}
    b['cancellation_research']=save('artifacts/research/result.json',cancel_parent)
    native={'stage':'selective-cancellation','commit':cancel,'parent':cancel_research,
            'signature_verified':True,'files':sorted(cancel_stage['files']),'epoch_sha256':'c'*64,
            'accepted':False,'accepted_fix_increment':0,'app_rebuilt':False}
    installed={'stage':'selective-cancellation','installed':True,'accepted':False,'app_rebuilt':False,
               'files':sorted(cancel_stage['files']),'new_tests_created':sorted(cancel_stage['create_tests']),
               'existing_tests_adopted_without_write':[],'manifest_sha256':'d'*64}
    evidence=save('artifacts/runtime/delivery/proof.json',{'synthetic':True})
    tests={p:r['sha256'] for p,r in cancel_stage['files'].items() if p in cancel_stage['create_tests']}
    delivery={'installation_manifest':installed['manifest_sha256'],'files':tests,
              'registered_urls':sorted('/'+p.removeprefix('testing/web-platform/tests/') for p in tests),
              'lint_exit':0,'lint_errors':0,'manifest_entries_verified':True,'browser_executed':False,
              'evidence':{evidence['path']:evidence['sha256']},'manifest_command':['synthetic']}
    b['cancellation_receipt']=save('artifacts/runtime/COMMIT-RESULT.json',native)
    b['cancellation_installation']=save('artifacts/runtime/INSTALL-RESULT.json',installed)
    b['cancellation_delivery']=save('artifacts/runtime/delivery/DELIVERY.json',delivery)
    research={'committed':True,'head':head,'parent':cancel,'signature_verified':True,
              'accepted_fix_increment':0,'native_working_diff_preserved':True}
    invoke=lambda:chain.verify(scratch,git,'synthetic-signers',b,chain.BASE,research,head)
    assert invoke()==cancel
    for key, obj, field, value in [
        ('cancellation_research',cancel_parent,'parent',chain.FONT),
        ('cancellation_receipt',native,'stage','wrong'), ('cancellation_receipt',native,'parent',chain.FONT),
        ('cancellation_receipt',native,'signature_verified',False), ('cancellation_receipt',native,'files',[]),
        ('cancellation_receipt',native,'accepted',True), ('cancellation_receipt',native,'app_rebuilt',True),
        ('cancellation_installation',installed,'installed',False), ('cancellation_installation',installed,'new_tests_created',[]),
        ('cancellation_delivery',delivery,'installation_manifest','wrong'), ('cancellation_delivery',delivery,'files',{}),
        ('cancellation_delivery',delivery,'lint_exit',1), ('cancellation_delivery',delivery,'manifest_entries_verified',False)]:
        original=copy.deepcopy(b[key]);bad=copy.deepcopy(obj);bad[field]=value
        b[key]=save(original['path'],bad);reject(key+'-'+field,invoke)
        b[key]=save(original['path'],obj)
    for key in ('font_receipt','font_research','post_font_research','cancellation_research'):
        original=copy.deepcopy(b[key]);b[key]['sha256']='0'*64
        reject('wrong authenticated '+key,invoke);b[key]=original
    for revision in (chain.FONT_RESEARCH,chain.FONT,chain.POST_FONT_RESEARCH,cancel_research,cancel,head):
        state['bad_signatures']={revision};reject('unsigned endpoint '+revision,invoke)
    state=copy.deepcopy(original_state)
    for key,value,label in [
        ('parents',(cancel,chain.FONT),'wrong cancellation sole parent'),
        ('parents',(head,cancel+' '+chain.FONT),'research merge'),
        ('diffs',((cancel,head),['servo/other.rs']),'intervening native source'),
        ('diffs',((cancel_research,cancel),sorted(cancel_stage['files'])+['servo/other.rs']),'extra cancellation native path'),
        ('blobs',(cancel+':'+chain.ROLE,b'changed'),'changed taint base at cancellation'),
        ('blobs',(head+':'+chain.ROLE,b'changed'),'changed taint base at research'),
        ('blobs',(cancel+':'+next(iter(cancel_stage['files'])),b'changed'),'wrong signed cancellation blob')]:
        state[key][value[0]]=value[1];reject(label,invoke);state=copy.deepcopy(original_state)
    test=cancel_stage['create_tests'][0]
    state['present']={(cancel_research,test)};reject('existing WPT in native parent',invoke)
    state=copy.deepcopy(original_state)
    extra='e'*40;state['intervals'][(cancel,head)]=[head,extra]
    state['parents'][head]=extra;state['parents'][extra]=cancel
    state['diffs'][(extra,head)]=['artifacts/research.json'];state['diffs'][(cancel,extra)]=['servo/hidden.rs']
    research['parent']=extra;reject('hidden intermediate native change',invoke)
    research['parent']=cancel;state=copy.deepcopy(original_state)
    assert invoke()==cancel
assert not scratch.exists()
print(json.dumps({'references':len(policy['references']), 'positive_fixed_chain':True,
                  'synthetic_git_and_future_cancellation_only':True,'negative_controls':negatives,
                  'unchanged_79_verifier_and_saved_acceptance_authenticated':True,'old_79_not_rerun':True,
                  'signing_and_rollback_tail_preserved':True,'scratch_removed':True,
                  'actual_cancellation_pending':True,'no_live_operations':True}))
