import os
from pathlib import Path
import subprocess


def validate_phase(root, here, policy, epoch, helper):
    experiment = helper.read(here / 'EXPERIMENT.json')
    succession = helper.read(here / 'SOURCE-SUCCESSION.json')
    helper.need(policy['phase'] == 'observation-1', 'current candidate observation')
    for key in ['frozen_head','tests','target_subtests','held_subtests','source_roles']:
        helper.need(policy[key] == experiment[key], 'fixed observation inputs: '+key)
    helper.need(policy['held_subtests'] == policy['regression_subtests'] == {}, 'all outcomes observational')
    helper.need(epoch['semantic_index']['head'] == policy['frozen_head'] == succession['observation_head'], 'current observation HEAD')
    helper.need(helper.sha(root / succession['signed_current_epoch']) == succession['signed_current_epoch_sha256'] == policy['epoch_sha256'], 'signed synchronized epoch bytes')
    helper.need(helper.read(root / succession['signed_current_epoch']) == epoch, 'actual current epoch equals signed checkpoint')
    transition = epoch['registered_number_transition']
    helper.need(transition == {'role':'candidate','variant':'zoom-standalone-v1','compiled':True,'accepted':False,'last_phase':'zoom-standalone-candidate-build-1'}, 'unchanged successful candidate compilation')
    helper.need(epoch['modified_native_paths'] == sorted(experiment['zoom_source_paths']) and len(experiment['zoom_source_paths']) == 7, 'exact seven native edits')
    helper.need(len(policy['source_roles']['candidate']) == 9 and all(epoch['pins'].get(n)==pin for n,pin in policy['source_roles']['candidate'].items()), 'nine inspected source bodies')
    build_path = Path('artifacts/css-registered-number-native-runtime-v1/zoom-standalone-candidate-build-1')
    helper.need(policy['build_result'] == str(build_path/'RESULT.json') and policy['build_epoch'] == str(build_path/'EPOCH.json'), 'actual historical build paths')
    helper.need(helper.sha(root/policy['build_result']) == policy['build_result_sha256'], 'actual build result bytes')
    result = helper.read(root/policy['build_result'])
    helper.need(result['source_role']=='candidate' and result['command_success'] and result['preservation_verified'] and not result['owned_processes'] and not result['publication_errors'] and result['error'] is None, 'successful terminal candidate build')
    helper.need(helper.sha(root/policy['build_epoch']) == policy['build_epoch_sha256'], 'actual historical build epoch bytes')
    built = helper.read(root/policy['build_epoch'])
    helper.need(built['semantic_index']['head'] == succession['build_head'] == 'd6243f35307b62a4a4f6067367d78c948d3f468c', 'historical build HEAD retained')
    for key in ['registered_number_transition','modified_native_paths','installed_identities','nested_semantic_index','untracked_native']:
        helper.need(built[key] == epoch[key], 'compiled continuity: '+key)
    nonartifact = lambda value: {name:pin for name,pin in value['pins'].items() if not name.startswith('artifacts/')}
    helper.need(nonartifact(built) == nonartifact(epoch), 'all compiled source/binary/config pins unchanged')
    helper.need(set(policy['phase_binaries']) == set(policy['normal_binaries']) and all(built['pins'].get(n)==epoch['pins'].get(n)==pin for n,pin in policy['phase_binaries'].items()), 'actual compiled binaries unchanged')
    helper.need(all(not os.environ.get(k) for k in ['GIT_DIR','GIT_WORK_TREE','GIT_INDEX_FILE','GIT_OBJECT_DIRECTORY','GIT_ALTERNATE_OBJECT_DIRECTORIES']), 'Git environment')
    env = dict(os.environ,GIT_OPTIONAL_LOCKS='0')
    def git(*args):
        return subprocess.check_output(['git','--no-optional-locks','-c','core.fsmonitor=false',*args],cwd=root,env=env)
    helper.need(git('rev-parse','HEAD').decode().strip()==succession['observation_head'], 'actual current HEAD')
    parent = succession['build_head']
    helper.need(len(succession['commits']) == 5, 'five signed artifact-only successors')
    for record in succession['commits']:
        helper.need(helper.sha(root/record['receipt'])==record['receipt_sha256'], 'signed successor receipt bytes')
        receipt = helper.read(root/record['receipt'])
        helper.need(receipt['signature_verified'] and all(receipt[k]==record[k] for k in ['commit','parent','tree','files']), 'receipt joins committed successor')
        commit = record['commit']
        helper.need(record['parent']==parent and git('rev-list','--parents','-n','1',commit).decode().split()==[commit,parent], 'linear actual successor')
        helper.need(git('rev-parse',commit+'^{tree}').decode().strip()==record['tree'], 'actual successor tree')
        paths = git('diff','--name-only',parent,commit).decode().splitlines()
        helper.need(sorted(paths)==sorted(record['files']) and all(n.startswith('artifacts/') and not n.startswith('artifacts/css-spec-lean/') and n!='artifacts/css-spec-lean' for n in paths), 'exact artifact-only successor paths')
        checked = subprocess.run(['git','--no-optional-locks','-c','gpg.ssh.allowedSignersFile='+str(root/'artifacts/css-local-signing-20261027-v1/allowed-signers'),'verify-commit',commit],cwd=root,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        helper.need(checked.returncode==0, 'actual SSH signature: '+commit)
        parent = commit
    helper.need(parent==succession['observation_head'], 'successor chain reaches current HEAD')
    return {'role':'candidate','phase':'observation-1','build_result':policy['build_result'],'build_result_sha256':policy['build_result_sha256'],
            'build_head':succession['build_head'],'build_epoch_sha256':policy['build_epoch_sha256'],'observation_head':succession['observation_head'],
            'observation_epoch_sha256':policy['epoch_sha256'],'artifact_only_successors':[r['commit'] for r in succession['commits']],
            'native_sources':policy['source_roles']['candidate'],'binaries':policy['phase_binaries'],'native_fix_acceptance':False,
            'build_revision_or_metadata_rewritten':False}
