import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit('Use python3 -I -S -B without optimization')
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
read = lambda p:json.loads(p.read_text())
sha = lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def encoded(value):
    return (json.dumps(value, indent=2, ensure_ascii=False) + '\n').encode()


def once(text, old, new):
    assert text.count(old) == 1, old
    return text.replace(old, new, 1)


def validate_inputs(inputs):
    for name,pin in inputs['evidence_pins'].items():
        assert sha(ROOT/name)==pin
    for key in ['acceptance','final_build','final_wpt','lint','final_comparison']:
        item=inputs[key]
        assert inputs['evidence_pins'][item['path']]==item['sha256']==sha(ROOT/item['path'])
    acceptance=read(ROOT/inputs['acceptance']['path'])
    assert acceptance['fix']==139 and acceptance['status']=='READY_FOR_STANDALONE_SIGNED_COMMIT'
    assert acceptance['validated_payload']==inputs['payload']
    assert acceptance['canonical_lean_increment']==0 and acceptance['native_refinement_proved'] is False
    build_path=ROOT/inputs['final_build']['path']
    build=read(build_path)
    assert build['command_success'] and build['preservation_verified'] and build['error'] is None
    assert not build['owned_processes'] and not build['publication_errors']
    build_epoch=read(build_path.with_name('EPOCH.json'))
    assert sha(build_path.with_name('EPOCH.json'))==inputs['evidence_pins'][str(build_path.with_name('EPOCH.json').relative_to(ROOT))]
    assessment=read(ROOT/inputs['final_wpt']['path'])
    assert assessment['complete'] and assessment['execution_preserved']
    assert not assessment['errors'] and not assessment['infrastructure_faults']
    assert assessment['epoch_sha256']==sha(build_path.with_name('EPOCH.json'))
    assert assessment['run_binding']['revision']==inputs['initial_head']
    assert all(build_epoch['pins'][name]==pin for name,pin in assessment['native_sources'].items())
    rows={(row['test'],row['subtest']):row['status'] for row in assessment['rows']}
    assert len(rows)==len(assessment['rows'])==668 and len(assessment['ends'])==31
    targets=read(ROOT/'artifacts/css-registered-zoom-fix139-payload-v1/TARGET-SUBTESTS.json')
    assert sum(map(len,targets.values()))==86
    assert all(rows[(test,name)]=='PASS' for test,names in targets.items() for name in names)
    lint=read(ROOT/inputs['lint']['path'])
    assert lint['exit']==0 and lint['native_and_wpt_bodies_preserved']
    assert lint['source_pins']==read(HERE/'native-fix-selection.json')['source_pins']
    verdict=read(ROOT/inputs['final_comparison']['path'])
    assert verdict['comparison_complete'] and verdict['test_evidence_supports_acceptance']
    assert verdict['actual_final_payload_and_build_bound'] and verdict['all86_focused_pass']
    assert verdict['normalized_differences']==0 and verdict['exact_subtest_signatures']==668
    assert verdict['exact_test_completions']==31


def render(old, template, receipts, evidence, overlay):
    entry = copy.deepcopy(template)
    native, research, validation = [receipts[n] for n in ['native-fix','research','validation']]
    entry.update(status='COMMITTED_NATIVE_WPT', native_commit=native['commit'],
                 research_commit=validation['commit'], companion_commit=validation['commit'],
                 acceptance=evidence['acceptance'], final_build=evidence['final_build'],
                 final_validation=evidence['final_wpt'], lint=evidence['lint'],
                 commit_verification=evidence['native_receipt'],
                 research_commit_verification=evidence['validation_receipt'],
                 signature_verified=True, candidate_source_installed=True,
                 browser_binary_contains_fix=True)
    ledger_name = 'artifacts/stylo-bloom-tools/CURRENT-COMMITS.json'
    groups_name = 'artifacts/css-fix-readout-20261023/GROUPS.json'
    ledger, groups = json.loads(old[ledger_name]), json.loads(old[groups_name])
    previous_ledger, previous_groups = copy.deepcopy(ledger), copy.deepcopy(groups)
    assert ledger['committed_native_fixes'] == 137
    assert not any(item.get('fix') == 139 for item in ledger['new_queue'])
    ledger['new_queue'].append(entry)
    ledger['committed_native_fixes'] = 138
    ledger.setdefault('local_signing_history', []).append(copy.deepcopy(ledger['latest_signing']))
    ledger['latest_signing'] = {'status':'SIGNED_VERIFIED_LOCAL','fix':139,
        'native_commit':native['commit'],'research_commit':validation['commit'],
        'verification':evidence['native_receipt']}
    ledger.setdefault('research_signing_history', []).append(copy.deepcopy(ledger['latest_research_signing']))
    ledger['previous_research_signing'] = copy.deepcopy(ledger['latest_research_signing'])
    ledger['latest_research_signing'] = {'status':'SIGNED_VERIFIED_LOCAL',
        'commits':{n:receipts[n]['commit'] for n in ['research','validation']},
        'directory':str(HERE.relative_to(ROOT))}
    ledger['latest_registered_zoom_fix'] = {'fix':139,'acceptance':evidence['acceptance'],
        'commit_verification':evidence['native_receipt'],'restoration_overlay':str((HERE/'ACCEPTED-OVERLAY.json').relative_to(ROOT))}
    ledger.setdefault('verified_working_epoch_history', []).append(copy.deepcopy(ledger['latest_verified_working_epoch']))
    ledger['latest_verified_working_epoch'].update(
        path=str((HERE/'CURRENT-EPOCH.json').relative_to(ROOT)),
        status='Signed standalone registered-value zoom repair; final86 pass and broad outcomes reviewed',
        candidate_accepted=True, native_commit=native['commit'],
        proposal='artifacts/css-registered-zoom-fix139-payload-v1',
        dirty_native_source_pins={}, accepted_native_source_pins=overlay['accepted_native'],
        browser_binary_contains_fix139=True,
        accepted_overlay=str((HERE/'ACCEPTED-OVERLAY.json').relative_to(ROOT)))
    ledger['signing_next_action'] = 'Preserve accepted zoom139; rebase pending prototypes on its accepted source before restoration. Continue the separate provider-readiness repair and Bloom milestones.'
    number_research = ledger['latest_registered_number_research']
    ledger.setdefault('registered_number_research_history', []).append(copy.deepcopy(number_research))
    number_research.update(
        status='Standalone zoom fix139 is signed and accepted; admission and provider-readiness work remain separate and unaccepted.',
        candidate_accepted=True, accepted_fix_increment=1,
        accepted_zoom_fix={'fix':139,'native_commit':native['commit'],'acceptance':evidence['acceptance']},
        zoom_followup_checkpoint={'status':'STANDALONE_ZOOM_SIGNED_ACCEPTED',
            'fix':139,'native_commit':native['commit'],'final_focused_PASS':86,
            'final_build':evidence['final_build'],'final_validation':evidence['final_wpt'],
            'container_interpretation':'CSSWG resolved intent; explicit published-text gap remains disclosed',
            'restoration_overlay':str((HERE/'ACCEPTED-OVERLAY.json').relative_to(ROOT)),
            'historical_observations_preserved':True},
        zoom_acceptance_blocker={'resolved_by_fix':139,'prior_details_preserved_in_history':True})
    assert ledger['new_queue'][:-1] == previous_ledger['new_queue']
    for key in ['accepted_pending_native_fixes','accepted_pending_native_fixes_on_hold',
                'accepted_pending_native_fixes_excluding_holds']:
        assert ledger[key] == previous_ledger[key]
    assert groups['accepted'] == groups['committed'] == 137 and groups['tracked'] == 138
    group = next(g for g in groups['groups'] if g['group'] == entry['group'])
    assert group['committed'] == group['total'] == 18
    group['fixes'].append(copy.deepcopy(entry))
    group['committed'] = group['total'] = 19
    groups.update(head=native['commit'], accepted=138, committed=138, tracked=139)
    assert sum(g['committed'] for g in groups['groups']) == 138
    for key in ['held','accepted_pending','formal_library_checkpoint','formal_library_checkpoint_history']:
        assert groups[key] == previous_groups[key]
    for a,b in zip(previous_groups['groups'],groups['groups']):
        assert a['fixes'] == (b['fixes'][:-1] if b['group']==entry['group'] else b['fixes'])
    new = {ledger_name:encoded(ledger), groups_name:encoded(groups)}
    summary = (f"Fix 139, registered-value zoom normalization, is committed as `{native['commit']}` after research `{validation['commit']}`. "
        "The standalone source0/zoom7 comparison repairs56 of70 focused assertions;14 controls remain passing. "
        "The final cleaned native build passes all86 focused assertions, including16 bounded container cases. "
        "Broad566 subtest signatures are preserved; six passing reftest messages have a separate exact-port adjudication. "
        "Historical broad failures remain failures, not new passes. Source-container normalization follows CSSWG resolved intent; the explicit draft wording gap remains disclosed. "
        "The line-height-only provider-readiness discrepancy remains separate and unaccepted. No new canonical Lean coverage or native-refinement credit is claimed. "
        "Preserve this accepted seven-file overlay and its seven WPTs when rebasing the50 parked prototypes; original snapshots remain unchanged.")
    for name, data in old.items():
        if name in new:
            continue
        title, rest = data.decode().split('\n',1)
        text = title + '\n\n' + summary + '\n' + rest
        for a,b in [
            ('**137 accepted fixes: 137 committed locally, 0 accepted pending, and 1 additional held repair excluded.**',
             '**138 accepted fixes: 138 committed locally, 0 accepted pending, and 1 additional held repair excluded.**'),
            ('| Attributes and custom properties | 18 | 0 |','| Attributes and custom properties | 19 | 0 |'),
            ('| **Total** | **137** | **0** |','| **Total** | **138** | **0** |'),
            ('All 137 accepted fixes remain committed; held repair 120 stays excluded.',
             'All 138 accepted fixes remain committed; held repair 120 stays excluded.')]:
            text = once(text,a,b)
        if not name.endswith('PLAN-OF-RECORD.md'):
            marker = '| 138: Raw nested attr cycles |'
            text = once(text,marker,f"| 139: Registered-value zoom normalization | `{native['commit']}` | `{validation['commit']}` |\n"+marker)
        new[name] = text.encode()
    accepted = copy.deepcopy(overlay)
    accepted.update(status='ACCEPTED_BASE_REBASE_REQUIRED', accepted_commit=native['commit'],
                    acceptance=evidence['acceptance'], native_receipt=evidence['native_receipt'])
    return new, accepted


def main():
    inputs = read(HERE/'INPUTS.json')
    assert inputs['ready'] is True, 'Disabled pending actual final validation and root acceptance'
    assert all(not os.environ.get(k) for k in ['GIT_DIR','GIT_WORK_TREE','GIT_INDEX_FILE','GIT_OBJECT_DIRECTORY','GIT_ALTERNATE_OBJECT_DIRECTORIES'])
    def git(*args):
        return subprocess.check_output(['git','--no-optional-locks',*args],cwd=ROOT,env=dict(os.environ,GIT_OPTIONAL_LOCKS='0'))
    validate_inputs(inputs)
    receipts={name:read(HERE/(name+'-receipt.json')) for name in ['research','validation','native-fix']}
    parent=inputs['initial_head']
    for name,record in receipts.items():
        assert record['signature_verified'] and record['parent']==parent
        assert git('rev-list','--parents','-n','1',record['commit']).decode().split()==[record['commit'],parent]
        assert git('rev-parse',record['commit']+'^{tree}').decode().strip()==record['tree']
        assert sorted(git('diff-tree','--no-commit-id','--name-only','-r',record['commit']).decode().splitlines())==sorted(record['files'])
        git('-c','gpg.ssh.allowedSignersFile='+str(ROOT/'artifacts/css-local-signing-20261027-v1/allowed-signers'),'verify-commit',record['commit'])
        if name!='native-fix':
            assert all(n.startswith('artifacts/') and not n.startswith('artifacts/css-spec-lean/') for n in record['files'])
        parent=record['commit']
    assert git('rev-parse','HEAD').decode().strip()==parent
    selection=read(HERE/'native-fix-selection.json')
    assert sorted(receipts['native-fix']['files'])==sorted(selection['files']) and len(selection['files'])==14
    for name,pin in selection['source_pins'].items():
        assert hashlib.sha256(git('show',parent+':'+name)).hexdigest()==pin==sha(ROOT/name)
        assert git('ls-tree',parent,'--',name).decode().split()[0]=='100644'
    old={name:(ROOT/name).read_bytes() for name in read(HERE/'LEDGER-PREIMAGES.json')}
    assert {name:hashlib.sha256(body).hexdigest() for name,body in old.items()}==read(HERE/'LEDGER-PREIMAGES.json')
    evidence={key:inputs[key] for key in ['acceptance','final_build','final_wpt','lint']}
    for ident in ['native','validation']:
        name='native-fix' if ident=='native' else ident
        path=HERE/(name+'-receipt.json')
        evidence[ident+'_receipt']={'path':str(path.relative_to(ROOT)),'sha256':sha(path)}
    new,overlay=render(old,read(HERE/'ENTRY-TEMPLATE.json'),receipts,evidence,read(HERE/'ACCEPTED-OVERLAY-TEMPLATE.json'))
    out=HERE/'checkpoint-postimages'
    out.mkdir()
    for name,data in new.items():
        target=out/name
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes(data)
    (HERE/'ACCEPTED-OVERLAY.json').write_bytes(encoded(overlay))
    (HERE/'LEDGER-RENDER.json').write_bytes(encoded({'native_commit':parent,
        'accepted':138,'tracked':139,'held_excluded':120,
        'postimages':{name:hashlib.sha256(body).hexdigest() for name,body in new.items()},
        'live_ledgers_modified':False,'automatic_restoration_controller_protection':False}))


if __name__=='__main__':
    main()
