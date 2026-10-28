import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys

if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit('Use python3 -I -S -B without optimization')
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RUNTIME = ROOT/'artifacts/css-registered-number-native-runtime-v1'
ENV = dict(os.environ, GIT_OPTIONAL_LOCKS='0', PYTHONDONTWRITEBYTECODE='1')
read = lambda p:json.loads(p.read_text())
sha = lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def save(path, value):
    with path.open('x') as stream:
        json.dump(value,stream,indent=2,sort_keys=True)
        stream.write('\n')


def load(name, path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    inputs=read(HERE/'INPUTS.json')
    assert inputs['ready'] is True, 'Disabled pending actual final validation and root acceptance'
    assert all(not os.environ.get(k) for k in ['GIT_DIR','GIT_WORK_TREE','GIT_INDEX_FILE','GIT_OBJECT_DIRECTORY','GIT_ALTERNATE_OBJECT_DIRECTORIES'])
    state=load('checkpoint_state',RUNTIME/'state.py')
    ownership=load('checkpoint_ownership',ROOT/'artifacts/css-registered-number-source-transition-v4/transition.py')
    renderer=load('checkpoint_renderer',HERE/'render_checkpoint.py')
    renderer.validate_inputs(inputs)
    git=lambda *args:state.h.git(ROOT,ENV,*args)
    epoch_path=HERE/'CURRENT-EPOCH.json'
    epoch_bytes=epoch_path.read_bytes()
    epoch=json.loads(epoch_bytes)
    before=state.a.verify_current(state.h,ROOT,ENV,epoch)
    assert epoch['modified_native_paths']==[]
    native=read(HERE/'native-fix-receipt.json')
    assert native['signature_verified'] and git('rev-parse','HEAD').decode().strip()==native['commit']==epoch['semantic_index']['head']
    assert read(HERE/'LEDGER-RENDER.json')['native_commit']==native['commit']
    selection=read(HERE/'native-fix-selection.json')
    assert sorted(native['files'])==sorted(selection['files']) and len(selection['files'])==14
    for name,pin in selection['source_pins'].items():
        assert sha(ROOT/name)==pin==epoch['pins'][name]
        assert hashlib.sha256(git('show','HEAD:'+name)).hexdigest()==pin
    controls={n:(RUNTIME/n).read_bytes() for n in ['CURRENT-EPOCH.json','ROLE.json','OWNED.json']}
    runtime_epoch_claim=ownership.claim(ROOT,str((RUNTIME/'CURRENT-EPOCH.json').relative_to(ROOT)),
        hashlib.sha256(controls['CURRENT-EPOCH.json']).hexdigest())
    flags={n:state.h.git(ROOT/n,ENV,'ls-files','-v','-z') for n in ['.','artifacts/css-spec-lean']}
    roles=read(ROOT/'artifacts/css-registered-zoom-fix139-payload-v1/PAYLOAD.json')['source_roles']
    overlay=read(HERE/'ACCEPTED-OVERLAY.json')
    assert overlay['accepted_commit']==native['commit'] and overlay['rebase_required']
    plan_ref=overlay['original_restoration_plan']
    assert sha(ROOT/plan_ref['path'])==plan_ref['sha256']
    parked=read(ROOT/plan_ref['path'])['paths']
    recovery=read(ROOT/'artifacts/css-unfinished-work-checkpoint-20261027-v8/SOURCE-PINS.json')
    assert len(parked)==50 and len(recovery)==140
    old={n:(ROOT/n).read_bytes() for n in read(HERE/'LEDGER-PREIMAGES.json')}
    assert {n:hashlib.sha256(b).hexdigest() for n,b in old.items()}==read(HERE/'LEDGER-PREIMAGES.json')
    ledger_claims={n:ownership.claim(ROOT,n,hashlib.sha256(b).hexdigest()) for n,b in old.items()}
    epoch_claim=ownership.claim(ROOT,str(epoch_path.relative_to(ROOT)),hashlib.sha256(epoch_bytes).hexdigest())
    receipts={n:read(HERE/(n+'-receipt.json')) for n in ['research','validation','native-fix']}
    evidence={k:inputs[k] for k in ['acceptance','final_build','final_wpt','lint']}
    acceptance=read(ROOT/inputs['acceptance']['path'])
    assert acceptance['fix']==139 and acceptance['status']=='READY_FOR_STANDALONE_SIGNED_COMMIT'
    assert acceptance['validated_payload']==inputs['payload']
    assert acceptance['canonical_lean_increment']==0 and acceptance['native_refinement_proved'] is False
    for item in evidence.values():
        assert inputs['evidence_pins'][item['path']]==item['sha256']==sha(ROOT/item['path'])
    for key,ident in [('native_receipt','native-fix'),('validation_receipt','validation')]:
        path=HERE/(ident+'-receipt.json')
        evidence[key]={'path':str(path.relative_to(ROOT)),'sha256':sha(path)}
    planned,planned_overlay=renderer.render(old,read(HERE/'ENTRY-TEMPLATE.json'),receipts,evidence,read(HERE/'ACCEPTED-OVERLAY-TEMPLATE.json'))
    assert planned_overlay==overlay
    for n,b in planned.items():
        assert (HERE/'checkpoint-postimages'/n).read_bytes()==b
        assert hashlib.sha256(b).hexdigest()==read(HERE/'LEDGER-RENDER.json')['postimages'][n]

    def preserve(current, checkpoint_files=None):
        for name,pin in inputs['evidence_pins'].items():
            assert sha(ROOT/name)==pin
        for name,pin in selection['source_pins'].items():
            assert sha(ROOT/name)==pin
        assert sha(ROOT/plan_ref['path'])==plan_ref['sha256']
        for name,item in parked.items():
            assert sha(RUNTIME/'prototype-original'/name)==item['prototype_original']
            assert sha(ROOT/name)==item['head_original']
        for name,pin in recovery.items():
            if name in old:
                assert sha(ROOT/name)==current['pins'][name]
            else:
                source=(RUNTIME/'prototype-original'/name if name in parked else
                        ROOT/roles[name]['base'] if name in roles else ROOT/name)
                assert sha(source)==pin,name
        untracked=set(git('ls-files','--others','--exclude-standard','dom/animation',
            'layout/style/test/gtest','servo/components/style','testing/web-platform/tests/css').decode().splitlines())
        assert len(untracked)==74 and untracked<=set(recovery)
        for n,body in flags.items():
            observed=state.h.git(ROOT/n,ENV,'ls-files','-v','-z')
            if n=='.' and checkpoint_files is not None:
                prior={row[2:]:row[:1] for row in body.split(b'\0') if row}
                now={row[2:]:row[:1] for row in observed.split(b'\0') if row}
                assert all(now.get(path)==flag for path,flag in prior.items())
                assert set(now)-set(prior)=={name.encode() for name in checkpoint_files}-set(prior)
            else:
                assert observed==body
        assert state.h.index_state(ROOT/'artifacts/css-spec-lean',ENV)==before['nested_index']
        assert all((RUNTIME/n).read_bytes()==body for n,body in controls.items())
    preserve(epoch)
    assert state.a.verify_current(state.h,ROOT,ENV,epoch)==before
    backup=HERE/'ledger-preimages'
    backup.mkdir()
    for name,body in old.items():
        path=backup/name
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_bytes(body)
    (HERE/'PRE-LEDGER-EPOCH.json').write_bytes(epoch_bytes)
    current=copy.deepcopy(epoch)
    changed=[]
    try:
        assert {n:(ROOT/n).read_bytes() for n in old}==old
        for n,item in ledger_claims.items():
            ownership.claim(ROOT,n,item['owned_sha256'],item['identity'])
        ownership.claim(ROOT,epoch_claim['path'],epoch_claim['owned_sha256'],epoch_claim['identity'])
        for name,body in planned.items():
            changed.append(name)
            ownership.write_owned(ROOT,ledger_claims[name],body)
            for key in ['pins','staged_working','committed_research_working_payloads']:
                if name in current[key]:
                    current[key][name]=sha(ROOT/name)
        index=state.h.index_state(ROOT,ENV)
        semantic=state.h.semantic_index(index)
        assert {k:v for k,v in semantic.items() if k!='working_diff'}=={k:v for k,v in epoch['semantic_index'].items() if k!='working_diff'}
        current['semantic_index']=semantic
        current['raw_index_observation']['current']=index['raw_index']
        current['registered_number_transition']['accepted']=True
        current['zoom_acceptance_payload']['accepted']=True
        current['accepted_registered_zoom']={'fix':139,'native_commit':native['commit'],
            'native_sources':overlay['accepted_native'],'tests':overlay['accepted_wpt'],
            'restoration_contract':str((HERE/'ACCEPTED-OVERLAY.json').relative_to(ROOT)),
            'pending_prototypes_require_rebase':True}
        preserve(current)
        state.a.verify_current(state.h,ROOT,ENV,current)
        ownership.write_owned(ROOT,epoch_claim,ownership.encoded(current))
    except BaseException:
        for name in reversed(changed):
            ownership.write_owned(ROOT,ledger_claims[name],old[name])
        restored=copy.deepcopy(epoch)
        index=state.h.index_state(ROOT,ENV)
        assert state.h.semantic_index(index)==epoch['semantic_index']
        restored['raw_index_observation']['current']=index['raw_index']
        preserve(restored)
        state.a.verify_current(state.h,ROOT,ENV,restored)
        ownership.write_owned(ROOT,epoch_claim,ownership.encoded(restored))
        raise
    save(HERE/'ROADMAP-UPDATE.json',{'before':read(HERE/'LEDGER-PREIMAGES.json'),
        'after':{n:sha(ROOT/n) for n in planned},'native_commit':native['commit'],
        'accepted':138,'tracked':139,'held_excluded':120,
        'original_snapshots_unchanged':True,'accepted_overlay_requires_new_restoration_controller':True})
    (HERE/'PRE-CHECKPOINT-EPOCH.json').write_bytes(epoch_path.read_bytes())
    (HERE/'CHECKPOINT.md').write_text(
        '# Signed standalone registered-value zoom checkpoint\n\n'
        f"Native fix139: `{native['commit']}`. Research: `{receipts['research']['commit']}`. Validation: `{receipts['validation']['commit']}`.\n\n"
        'Accepted138; tracked139; held120 excluded. Final86 focused assertions pass; broad historical outcomes remain preserved, including known failures. Source-container interpretation follows CSSWG intent with the draft gap disclosed. The separate provider-readiness defect remains unaccepted. Original50 prototype snapshots and74 unfinished project files remain intact; accepted zoom7 and its seven WPTs must survive later restoration, which requires a new reviewed accepted-base plan. No native refinement or additional canonical coverage is claimed.\n')
    files=set(planned)
    for name in ['commit.py','render_checkpoint.py','publish_checkpoint.py','PLAN.md','INPUTS.json',
                 'ENTRY-TEMPLATE.json','ACCEPTED-OVERLAY-TEMPLATE.json','ACCEPTED-OVERLAY.json',
                 'LEDGER-PREIMAGES.json','LEDGER-RENDER.json','ROADMAP-UPDATE.json','CHECKPOINT.md',
                 'RESEARCH-PACKAGES.json','VALIDATION-INVENTORY.json','PREPARATION-CHECK.json','INITIAL-EPOCH.json','BEFORE.json',
                 'PRE-LEDGER-EPOCH.json','PRE-CHECKPOINT-EPOCH.json']:
        files.add(str((HERE/name).relative_to(ROOT)))
    for ident in ['research','validation','native-fix']:
        for suffix in ['-selection.json','-item.json','-receipt.json','-signature.log','-message.txt','-commit.log']:
            files.add(str((HERE/(ident+suffix)).relative_to(ROOT)))
    for directory in ['ledger-preimages','checkpoint-postimages']:
        files.update(str(p.relative_to(ROOT)) for p in (HERE/directory).rglob('*') if p.is_file())
    pins={n:sha(ROOT/n) for n in sorted(files)}
    save(HERE/'checkpoint-selection.json',{'id':'checkpoint',
        'message':'No bug - Record signed registered-value zoom fix and pending prototype base. r?#firefox-style-system-reviewers',
        'files':sorted(pins),'source_pins':pins})
    with (HERE/'checkpoint-driver.log').open('x') as stream:
        subprocess.run([sys.executable,'-I','-S','-B',str(HERE/'commit.py'),str(HERE/'checkpoint-selection.json')],
            cwd=ROOT,env=ENV,stdout=stream,stderr=subprocess.STDOUT,check=True)
    receipt=read(HERE/'checkpoint-receipt.json')
    assert receipt['signature_verified'] and receipt['parent']==native['commit']
    assert git('rev-parse','HEAD').decode().strip()==receipt['commit']
    final=read(epoch_path)
    state.a.verify_current(state.h,ROOT,ENV,final)
    preserve(final, pins)
    assert final['modified_native_paths']==[]
    for name,pin in pins.items():
        assert hashlib.sha256(git('show','HEAD:'+name)).hexdigest()==pin
    assert read(ROOT/'artifacts/stylo-bloom-tools/CURRENT-COMMITS.json')['committed_native_fixes']==138
    assert all((RUNTIME/n).read_bytes()==body for n,body in controls.items())
    try:
        ownership.write_owned(ROOT,runtime_epoch_claim,epoch_path.read_bytes())
    except BaseException:
        ownership.write_owned(ROOT,runtime_epoch_claim,controls['CURRENT-EPOCH.json'])
        raise
    state.a.verify_current(state.h,ROOT,ENV,read(RUNTIME/'CURRENT-EPOCH.json'))
    assert all((RUNTIME/n).read_bytes()==controls[n] for n in ['ROLE.json','OWNED.json'])
    save(HERE/'FINAL-CHECK.json',{'head':receipt['commit'],'native_commit':native['commit'],
        'signatures_verified':True,'staging_empty':True,'accepted_fixes':138,'tracked':139,
        'held_excluded':120,'native_dirty_paths':0,'parked_snapshots':50,'untracked_project_files':74,
        'accepted_overlay_recorded':True,'old_restoration_controller_reusable':False,
        'canonical_coverage_increment':0,'current_epoch_sha256':sha(epoch_path),
        'runtime_epoch_synchronized':True})


if __name__=='__main__':
    main()
