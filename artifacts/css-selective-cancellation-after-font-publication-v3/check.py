import ast
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import signal
import sys
import tempfile
from types import SimpleNamespace

assert sys.flags.isolated and sys.flags.no_site and sys.dont_write_bytecode
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
PARENT=ROOT/'artifacts/css-selective-cancellation-after-font-publication-v2'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_bytes())


def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module


def extract(path):
    tree=ast.parse(path.read_text())
    main=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='main')
    outer=next(n for n in main.body if isinstance(n,ast.Try))
    install=outer.body[1]
    assert isinstance(install,ast.If) and ast.unparse(install.test)=="action == 'install'"
    index=next(i for i,n in enumerate(install.body) if isinstance(n,ast.For) and ast.unparse(n.iter)=='sorted(created_paths)')
    loop=install.body[index]
    success=ast.Module(body=copy.deepcopy(install.body[index:index+3]),type_ignores=[])
    failure=ast.Module(body=[ast.Try(body=[copy.deepcopy(loop)],handlers=copy.deepcopy(outer.handlers),orelse=[],finalbody=copy.deepcopy(outer.finalbody))],type_ignores=[])
    return compile(ast.fix_missing_locations(success),str(path),'exec'),compile(ast.fix_missing_locations(failure),str(path),'exec'),outer


policy=read(HERE/'POLICY.json')
assert policy['enabled_modes']==[] and all(policy[n] is None for n in ('bindings','stage','pair_binding','runtime_output'))
for path,pin in policy['references'].items():assert sha(ROOT/path)==pin,path
for path in HERE.glob('*.py'):compile(path.read_bytes(),str(path),'exec')
for name in ('native.patch','STAGES.json','transform.py','delivery.py','PAIR-BINDING.json'):
    assert (HERE/name).read_bytes()==(PARENT/name).read_bytes()
runner=load('new_runner',HERE/'run.py')
evidence=load('new_evidence',HERE/'evidence.py')
owner=load('actual_owner',ROOT/'artifacts/css-registered-number-source-transition-v4/transition.py')
creation=load('actual_creation',ROOT/'artifacts/css-registered-admission-wpt-install-v1/install.py')
stage,=read(HERE/'STAGES.json')['stages']
assert len(stage['create_tests'])==2
success,failure,new_outer=extract(HERE/'run.py')
_,old_failure,old_outer=extract(PARENT/'run.py')
assert ast.dump(new_outer.handlers[0],include_attributes=False)==ast.dump(old_outer.handlers[0],include_attributes=False)
assert ast.dump(ast.Module(body=new_outer.finalbody,type_ignores=[]),include_attributes=False)==ast.dump(ast.Module(body=old_outer.finalbody,type_ignores=[]),include_attributes=False)
source=ROOT/'artifacts/css-root-font-cancellation-selective-handoff-fix-v1/parent'
fixture=ROOT/'artifacts/css-selective-cancellation-publication-install-failure-v2'
actual_epoch=read(fixture/'CURRENT-EPOCH.json')
assert 'servo/components/style/gecko/traversal.rs' not in actual_epoch['pins']
results=[]
for scenario in ('success','second-journal-failure','second-write-failure','old-exclusive-journal-failure'):
    with tempfile.TemporaryDirectory(prefix='cancellation-journal-',dir='/private/tmp') as temporary:
        scratch=Path(temporary);output=scratch/'output';output.mkdir();runtime=scratch/'controls';runtime.mkdir();lock=scratch/'lock';lock.mkdir()
        epoch=copy.deepcopy(actual_epoch);epoch['semantic_index']={'head':'saved-test-head'}
        controls={n:(fixture/n).read_bytes() for n in ('CURRENT-EPOCH.json','OWNED.json','ROLE.json')}
        controls['CURRENT-EPOCH.json']=owner.encoded(epoch)
        control_claims={}
        for name,body in controls.items():
            q=runtime/name;q.write_bytes(body);control_claims[name]=owner.claim(scratch,str(q.relative_to(scratch)),sha(q))
        originals={};source_claims={}
        for path,pin in stage['head_preimages'].items():
            q=scratch/path;q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source/path,q)
            assert sha(q)==pin;originals[path]=q.read_bytes();source_claims[path]=owner.claim(scratch,path,pin)
            owner.write_owned(scratch,source_claims[path],(ROOT/stage['files'][path]['path']).read_bytes())
        parents={}
        for path in stage['create_tests']:
            q=scratch/path;q.parent.mkdir(parents=True,exist_ok=True);parents[path]=creation.parent_pins(scratch,q)
            payload=scratch/stage['files'][path]['path'];payload.parent.mkdir(parents=True,exist_ok=True);payload.write_bytes((ROOT/stage['files'][path]['path']).read_bytes())
        second=sorted(stage['create_tests'])[1]
        def saving(path,value):
            if scenario=='second-journal-failure' and path.name=='CREATED-0002.json':
                raise RuntimeError('injected second journal failure')
            runner.save(path,value)
        def writing(root,claim,body):
            owner.write_owned(root,claim,body)
            if scenario=='second-write-failure' and claim['path']==second:
                raise RuntimeError('injected after second payload write')
        used_owner=SimpleNamespace(claim=owner.claim,write_owned=writing,encoded=owner.encoded)
        before={'index':{'raw_index':'before'}}
        def verify_current(*args):
            assert all((scratch/path).read_bytes()==body for path,body in originals.items())
            assert all(not (scratch/path).exists() for path in stage['create_tests'])
            return {'index':{'raw_index':'after'}}
        state=SimpleNamespace(h=SimpleNamespace(index_state=lambda *a:{'raw_index':'after'},semantic_index=lambda *a:epoch['semantic_index']),a=SimpleNamespace(verify_current=verify_current))
        def git(*args):
            assert args==('ls-files','--others','--exclude-standard','-z')
            assert all(not (scratch/path).exists() for path in stage['create_tests'])
            return b''
        context=dict(ROOT=scratch,RUNTIME=runtime,output=output,stage=stage,owner=used_owner,creation=creation,created_paths=set(stage['create_tests']),created={},parents=parents,adopted={},source_claims=source_claims,originals=originals,controls=controls,control_claims=control_claims,epoch=epoch,before=before,state=state,ENV={},git=git,untracked=b'',action='install',safe=False,lock=lock,lock_identity=[lock.stat().st_dev,lock.stat().st_ino],copy=copy,signal=signal,save=saving)
        if scenario=='success':
            exec(success,context)
            final=context['created'];assert len(final)==2
            assert set((output/'OWNERSHIP.json').read_bytes())
            saved=read(output/'OWNERSHIP.json')
            for path in stage['create_tests']:
                assert final[path]['owned_sha256']==stage['files'][path]['sha256']
                assert owner.claim(scratch,path,stage['files'][path]['sha256'],final[path]['identity'])==saved[path]==final[path]
            first_journal=read(output/'CREATED-0001.json');second_journal=read(output/'CREATED-0002.json')
            assert list(first_journal)==sorted(stage['create_tests'])[:1]
            assert set(second_journal)==set(stage['create_tests'])
            assert first_journal[sorted(stage['create_tests'])[0]]['owned_sha256']==hashlib.sha256(b'').hexdigest()
            assert second_journal[sorted(stage['create_tests'])[0]]['owned_sha256']==stage['files'][sorted(stage['create_tests'])[0]]['sha256']
            assert second_journal[second]['owned_sha256']==hashlib.sha256(b'').hexdigest()
            assert not (output/'CREATED.json').exists()
        else:
            try:exec(old_failure if scenario=='old-exclusive-journal-failure' else failure,context)
            except (RuntimeError,FileExistsError) as error:
                if scenario=='old-exclusive-journal-failure':assert isinstance(error,FileExistsError)
                else:assert str(error).startswith('injected')
            else:raise AssertionError('failure was not injected/reproduced')
            report=read(output/'INSTALL-FAILURE.json');assert report['rollback_verified'] and not report['manual_recovery_required']
            assert not lock.exists() and all(not (scratch/path).exists() for path in stage['create_tests'])
            for path,body in originals.items():assert (scratch/path).read_bytes()==body
            for name in ('OWNED.json','ROLE.json'):assert (runtime/name).read_bytes()==controls[name]
            restored=read(runtime/'CURRENT-EPOCH.json');assert restored['raw_index_observation']['current']=='after'
            restored['raw_index_observation']['current']=epoch['raw_index_observation']['current'];assert restored==epoch
            assert len(context['created'])==2
        results.append({'scenario':scenario,'pass':True,'scratch':str(scratch)})
    assert not scratch.exists()
anchor_record=policy['research_anchor'];assert sha(ROOT/anchor_record['path'])==anchor_record['sha256'];anchor=read(ROOT/anchor_record['path'])
font_record=read(HERE/'PAIR-BINDING.json')['font_native_receipt'];font=read(ROOT/font_record['path'])
future={'committed':True,'signature_verified':True,'accepted_fix_increment':0,'native_working_diff_preserved':True,'head':'1'*40,'parent':anchor['head']}
lookup={anchor['head']:anchor,future['head']:future}
calls=[]
def history(*args):
    calls.append(args)
    if args[0]=='rev-list':return (args[-1]+' '+lookup[args[-1]]['parent']).encode()
    if args[0]=='diff':return b'artifacts/example'
    if args[0] in ('-c','merge-base'):return b''
    raise AssertionError(args)
evidence.verify_research_history(history,'signers',future,font,future['head'],anchor)
assert sum(a[0]=='-c' for a in calls)==2
rejects=[]
def reject(label,fn):
    try:fn()
    except (AssertionError,KeyError):rejects.append(label)
    else:raise AssertionError(label)
for key,value in [('parent',font['commit']),('signature_verified',False),('committed',False),('native_working_diff_preserved',False)]:
    bad=dict(future);bad[key]=value
    reject('future '+key,lambda:evidence.verify_research_history(history,'signers',bad,font,future['head'],anchor))
for key,value in [('head','2'*40),('parent','2'*40),('signature_verified',False)]:
    bad=dict(anchor);bad[key]=value
    reject('anchor '+key,lambda:evidence.verify_research_history(history,'signers',future,font,future['head'],bad))
for interval in (anchor['head'],future['head']):
    def changed(*args):
        if args[0]=='diff' and args[-1]==interval:return b'servo/unexpected.rs'
        return history(*args)
    reject('native delta at '+interval,lambda:evidence.verify_research_history(changed,'signers',future,font,future['head'],anchor))
old=(PARENT/'run.py').read_text();new=(HERE/'run.py').read_text();tail='            with tempfile.TemporaryDirectory('
assert new[new.index(tail):]==old[old.index(tail):]
print(json.dumps({'production_loop_cases':results,'history_rejections':rejects,'actual_anchor_sha256':anchor_record['sha256'],'references':len(policy['references']),'real_creation_claim_write_unlink_helpers':True,'state_and_git_checks_doubled':True,'source_and_controls_restored_by_exact_handler':True,'signing_rollback_tail_exact':True,'payload_stage_transform_delivery_exact':True,'historical_full_native_browser_replay_not_repeated':True,'live_actions':False},sort_keys=True))
