import copy
import difflib
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
PARENT=ROOT/'artifacts/css-explicit-taint-typed-reparse-post-font-publication-v1'
sha=lambda body:hashlib.sha256(body).hexdigest()
read=lambda path:json.loads(path.read_bytes())
assert sha((PARENT/'FILES.json').read_bytes())=='b0e7dbc27e65b17cfcc635ddabc08772de637582bb72ab8c059b34fec8aae989'
for name,row in read(PARENT/'FILES.json').items():
    assert sha((PARENT/name).read_bytes())==row['sha256']
unchanged=['run.py','publish.py','chain.py','evidence.py','transform.py','delivery.py','STAGES.json','native.patch','PAIR-BINDING.json']
for name in unchanged:assert (HERE/name).read_bytes()==(PARENT/name).read_bytes()
policy=read(HERE/'POLICY.json');binding=read(HERE/'CHAIN-BINDING.json');old=read(PARENT/'CHAIN-BINDING.json')
assert policy['bindings'] is policy['pair_binding'] is policy['stage'] is policy['runtime_output'] is None
assert policy['enabled_modes']==[] and policy['publication_chain']==binding
changed={'cancellation_research','cancellation_receipt','cancellation_installation','cancellation_delivery'}
assert {key for key in binding if binding[key]!=old[key]}==changed
assert all(old[k] is None and binding[k] is not None for k in changed)
for name in ['POLICY.json','CHAIN-BINDING.json']:
    expected=''.join(difflib.unified_diff((PARENT/name).read_text().splitlines(True),(HERE/name).read_text().splitlines(True),fromfile='v1/'+name,tofile='v2/'+name))
    assert (HERE/('PARENT-'+name+'.diff')).read_text()==expected
for path,pin in policy['references'].items():assert sha((ROOT/path).read_bytes())==pin,path
spec=importlib.util.spec_from_file_location('bound_chain',HERE/'chain.py')
chain=importlib.util.module_from_spec(spec);spec.loader.exec_module(chain)
cancellation=chain.authenticated(ROOT,binding['cancellation_receipt'])
assert cancellation['commit']=='2409a410a2641c54a42feefd3c998cd58cbf028e'
assert cancellation['parent']=='e795bd155abbcf3bc6d9d861ad4ee22d610b07ad'
parent=chain.authenticated(ROOT,binding['cancellation_research'])
assert parent['head']==cancellation['parent'] and parent['parent']==chain.POST_FONT_RESEARCH
assert not any(os.environ.get(k) for k in ('GIT_DIR','GIT_WORK_TREE','GIT_INDEX_FILE','GIT_OBJECT_DIRECTORY','GIT_ALTERNATE_OBJECT_DIRECTORIES'))
env=dict(os.environ,GIT_OPTIONAL_LOCKS='0')
commands=[]
def immutable_git(*args):
    assert args[0] in ('-c','merge-base','rev-list','diff','show','ls-tree')
    assert all('HEAD' not in str(a) for a in args)
    commands.append(list(args))
    return subprocess.check_output(['git','--no-optional-locks','-c','core.fsmonitor=false',*args],cwd=ROOT,env=env)
future='f'*40
research={'committed':True,'head':future,'parent':cancellation['commit'],'signature_verified':True,
          'accepted_fix_increment':0,'native_working_diff_preserved':True}
future_calls=[]
def final_interval_double(*args):
    if any(future in str(a) for a in args):
        future_calls.append(list(args))
        if args==('rev-list','--parents','-n','1',future):return (future+' '+cancellation['commit']+'\n').encode()
        if args==('merge-base','--is-ancestor',cancellation['commit'],future):return b''
        if args==('rev-list','--parents',cancellation['commit']+'..'+future):return (future+' '+cancellation['commit']+'\n').encode()
        if args==('diff','--name-only',cancellation['commit'],future):return b'artifacts/future-research.json\n'
        if args==('-c','gpg.ssh.allowedSignersFile='+str(ROOT/policy['allowed_signers']),'verify-commit',future):return b''
        if args==('show',future+':'+chain.ROLE):return immutable_git('show',cancellation['commit']+':'+chain.ROLE)
        raise AssertionError('Unexpected future protocol call')
    return immutable_git(*args)
actual_base=chain.verify(ROOT,final_interval_double,str(ROOT/policy['allowed_signers']),binding,chain.BASE,research,future)
assert actual_base==cancellation['commit'] and len(future_calls)==6
rejects=[]
def reject(label,fn):
    try:fn()
    except AssertionError:rejects.append(label)
    else:raise AssertionError('Accepted '+label)
for key in sorted(changed):
    bad=copy.deepcopy(binding);bad[key]=None
    reject('missing '+key,lambda:chain.verify(ROOT,lambda *a:(_ for _ in ()).throw(RuntimeError('Unexpected Git')),str(ROOT/policy['allowed_signers']),bad,chain.BASE,research,future))
    record=dict(binding[key],sha256='0'*64)
    reject('wrong digest '+key,lambda:chain.authenticated(ROOT,record))
stage,=chain.authenticated(ROOT,binding['cancellation_stages'])['stages']
for field,value in [('parent',chain.FONT),('files',[]),('signature_verified',False)]:
    bad=dict(cancellation);bad[field]=value
    reject('actual receipt '+field,lambda:chain.require_native(bad,stage,parent['head']))
assert read(PARENT/'CHECK.json')['result']['actual_cancellation_pending'] is True
assert len(read(PARENT/'CHECK.json')['result']['negative_controls'])==33
print(json.dumps({'references':len(policy['references']),'unchanged_files':unchanged,'actual_chain_base':actual_base,
                  'actual_signed_native_prefix_verified':True,'real_immutable_git_calls':len(commands),
                  'future_taint_research_interval':'six explicit protocol doubles only; no actual future receipt or authority',
                  'future_calls':future_calls,'rejections':rejects,'parent33controls_authenticated_not_repeated':True,
                  'old79_not_replayed':True,'execution_disabled':True,'no_live_index_source_app_or_canonical_reads':True}))
