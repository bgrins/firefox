import copy


def installed(epoch, owned, role, stage, claims, index, semantic, manifest, label):
    current, ownership = copy.deepcopy(epoch), copy.deepcopy(owned)
    for path, record in stage['files'].items():
        claim = claims[path]
        assert claim['path'] == path and claim['owned_sha256'] == record['sha256']
        for name in ('pins', 'staged_working', 'committed_research_working_payloads'):
            if path in current[name]:
                current[name][path] = record['sha256']
        current['pins'][path] = record['sha256']
        current['installed_identities'][path] = claim['identity']
        ownership[path] = copy.deepcopy(claim)
    current['semantic_index'] = semantic
    current['raw_index_observation']['current'] = index['raw_index']
    current['modified_native_paths'] = sorted(stage['head_preimages'])
    current['counts']['native_modified_paths'] = len(stage['head_preimages'])
    current['counts']['roles'] = len(current['pins'])
    current['counts']['installed_identities'] = len(current['installed_identities'])
    marker = {'stage': stage['stage'], 'installation_manifest': manifest,
              'files': {p: r['sha256'] for p, r in stage['files'].items()},
              'head_preimages': stage['head_preimages'], 'compiled': False,
              'current_app_contains_candidate': False, 'accepted': False,
              'old_restoration_recipes_require_rebase': True}
    current.setdefault('root_self_animation_publication', {})[stage['stage']] = marker
    new_role = copy.deepcopy(role)
    new_role.update(role='published-native', variant=stage['stage'],
                    built=False, last_transition=label, paired_head=semantic['head'],
                    pending_gtest_overlay_installed=False)
    new_role.pop('last_build', None)
    new_role.pop('last_install', None)
    current['registered_number_transition'] = {
        'role': new_role['role'], 'variant': new_role['variant'], 'compiled': False,
        'accepted': False, 'last_transition': label, 'paired_head': semantic['head'],
        'pending_gtest_overlay_installed': False,
        'superseded_by': 'root_self_animation_publication'}
    assert current['prototype_overlay_state'] == epoch['prototype_overlay_state']
    assert current['registered_color_image_publication'] == epoch['registered_color_image_publication']
    assert current['nowrap_publication'] == epoch['nowrap_publication']
    assert current['language_partition_publication'] == epoch['language_partition_publication']
    assert current['hyphenation_ownership_publication'] == epoch['hyphenation_ownership_publication']
    assert current['prioritary_declaration_capacity_publication'] == epoch['prioritary_declaration_capacity_publication']
    return current, ownership, new_role


def committed(epoch, stage, index, semantic, commit):
    current = copy.deepcopy(epoch)
    current['semantic_index'] = semantic
    current['raw_index_observation']['current'] = index['raw_index']
    current['modified_native_paths'] = []
    current['counts']['native_modified_paths'] = 0
    current['root_self_animation_publication'][stage]['native_commit'] = commit
    current['registered_number_transition']['paired_head'] = commit
    return current
