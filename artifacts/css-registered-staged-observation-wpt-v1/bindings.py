import re
from pathlib import Path


def validate_phase(root, here, policy, epoch, helper):
    experiment = helper.read(here / 'EXPERIMENT.json')
    role = 'candidate'
    helper.need(policy['phase'] == 'observation-1', 'current candidate observation')
    helper.need(role in ('original', 'candidate'), 'phase role')
    for key in ['frozen_head','tests','target_subtests','held_subtests','source_roles']:
        helper.need(policy[key] == experiment[key], 'fixed experiment: ' + key)
    helper.need(policy['regression_subtests'] == {}, 'all phase outcomes observational')
    helper.need(policy['frozen_head'] == 'd6243f35307b62a4a4f6067367d78c948d3f468c', 'frozen paired HEAD')
    helper.need(epoch['semantic_index']['head'] == policy['frozen_head'], 'phase HEAD')
    transition = epoch['registered_number_transition']
    helper.need(transition['role'] == role and transition['variant'] == 'zoom-standalone-v1' and
                transition['compiled'] is True and transition['accepted'] is False, 'compiled unaccepted standalone role')
    expected_dirty = [] if role == 'original' else experiment['zoom_source_paths']
    helper.need(epoch['modified_native_paths'] == sorted(expected_dirty), 'exact zero or seven modified native paths')
    helper.need(len(policy['source_roles'][role]) == 9 and all(epoch['pins'].get(n) == pin
                for n,pin in policy['source_roles'][role].items()), 'nine inspected native bodies')
    result_path = Path(policy['build_result'])
    helper.need(not result_path.is_absolute() and '..' not in result_path.parts and
                result_path.parent.parent == Path('artifacts/css-registered-number-native-runtime-v1') and
                re.fullmatch('zoom-standalone-' + role + '-build-[1-9][0-9]*', result_path.parent.name) and
                result_path.name == 'RESULT.json', 'owned matching phase build receipt')
    helper.need(transition['last_phase'] == result_path.parent.name, 'last compiled phase')
    helper.need(helper.sha(root / result_path) == policy['build_result_sha256'], 'exact build result')
    result = helper.read(root / result_path)
    helper.need(result['source_role'] == role, 'build receipt source role')
    helper.need(result['command_success'] and result['preservation_verified'] and not result['owned_processes']
                and not result['publication_errors'], 'successful terminal preserved build')
    helper.need(policy['build_epoch'] == str(result_path.with_name('EPOCH.json')), 'saved phase build epoch path')
    helper.need(helper.sha(root / policy['build_epoch']) == policy['build_epoch_sha256'] == policy['epoch_sha256'],
                'exact phase epoch bytes')
    helper.need(helper.read(root / policy['build_epoch']) == epoch, 'saved build equals externally bound runtime epoch')
    helper.need(set(policy['phase_binaries']) == set(policy['normal_binaries']) and all(epoch['pins'].get(n) == pin
                for n,pin in policy['phase_binaries'].items()), 'exact normal binary pins')
    return {'role':role,'phase':policy['phase'],'build_result':policy['build_result'],
            'build_result_sha256':policy['build_result_sha256'],'epoch_sha256':policy['epoch_sha256'],
            'native_sources':policy['source_roles'][role],'binaries':policy['phase_binaries'],
            'experiment_sha256':helper.sha(here / 'EXPERIMENT.json'),'native_fix_acceptance':False}
