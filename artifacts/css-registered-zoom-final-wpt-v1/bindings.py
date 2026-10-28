from pathlib import Path


def validate_phase(root, here, policy, epoch, helper):
    experiment = helper.read(here/'EXPERIMENT.json')
    helper.need(policy['phase']=='observation-1', 'final current candidate observation')
    for key in ['frozen_head','tests','target_subtests','held_subtests','source_roles','installed_tests']:
        helper.need(policy[key]==experiment[key], 'fixed final inputs: '+key)
    helper.need(policy['regression_subtests']=={}, 'all completed outcomes observable')
    helper.need(epoch['semantic_index']['head']==policy['frozen_head']=='749b1227b09bee3adfac517e49de87d0fb2b89de', 'current final build HEAD')
    helper.need(epoch['registered_number_transition']=={'role':'candidate','variant':'zoom-standalone-v1','compiled':True,'accepted':False,'last_phase':'zoom-standalone-candidate-build-2'}, 'successful final candidate compilation')
    helper.need(epoch['modified_native_paths']==sorted(experiment['zoom_source_paths']) and len(experiment['zoom_source_paths'])==7, 'exact seven native edits')
    helper.need(len(policy['source_roles']['candidate'])==9 and all(epoch['pins'].get(name)==pin for name,pin in policy['source_roles']['candidate'].items()), 'nine inspected native bodies')
    helper.need(len(policy['installed_tests'])==7 and all(epoch['pins'].get(name)==pin and name in epoch['installed_identities'] for name,pin in policy['installed_tests'].items()), 'seven installed final WPT bodies and identities')
    build=Path('artifacts/css-registered-number-native-runtime-v1/zoom-standalone-candidate-build-2')
    helper.need(policy['build_result']==str(build/'RESULT.json') and policy['build_epoch']==str(build/'EPOCH.json'), 'actual final build paths')
    helper.need(helper.sha(root/policy['build_result'])==policy['build_result_sha256'], 'actual final build result')
    result=helper.read(root/policy['build_result'])
    helper.need(result['source_role']=='candidate' and result['command_success'] and result['preservation_verified'] and result['error'] is None and not result['owned_processes'] and not result['publication_errors'], 'terminal successful preserved build')
    helper.need(helper.sha(root/policy['build_epoch'])==policy['build_epoch_sha256']==policy['epoch_sha256'], 'exact saved/current build epoch bytes')
    helper.need(helper.read(root/policy['build_epoch'])==epoch, 'actual final build epoch equals bound runtime epoch')
    helper.need(set(policy['phase_binaries'])==set(policy['normal_binaries']) and all(epoch['pins'].get(name)==pin for name,pin in policy['phase_binaries'].items()), 'actual final compiled binaries')
    return {'role':'candidate','phase':'observation-1','build_result':policy['build_result'],'build_result_sha256':policy['build_result_sha256'],
            'build_head':policy['frozen_head'],'build_epoch_sha256':policy['build_epoch_sha256'],'observation_epoch_sha256':policy['epoch_sha256'],
            'native_sources':policy['source_roles']['candidate'],'installed_tests':policy['installed_tests'],'binaries':policy['phase_binaries'],
            'native_fix_acceptance':False,'build_revision_or_metadata_rewritten':False}
