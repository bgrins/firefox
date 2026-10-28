import copy
import os
import subprocess


def validate_core(receipt, policy, predecessor, roles, build, before, after, need):
    need((receipt['old_head'], receipt['build_head'], receipt['new_head']) ==
         ('e2839ec561c1e19de963bd0d56f46f4c067685d0',
          '1c7870c6d36d002b1c785ec2a6251ddc4ca2a040',
          '6eb538c23bcf3dde9c7631a1c826cba4de562462'), 'exact original/build/current HEADs')
    expected = copy.deepcopy(predecessor)
    expected['frozen_head'] = receipt['new_head']
    expected['source_roles']['candidate'].update({n:v['candidate_sha256'] for n,v in roles.items()})
    del expected['unchanged_native_sources']['servo/components/style/properties_and_values/value.rs']
    need(policy == expected and len(roles) == 7 and len(policy['source_roles']['candidate']) == 9,
         'only exact seven candidate additions and current HEAD may change policy')
    need(policy['original_frozen_head'] == receipt['old_head'], 'original HEAD retained')
    need([e['semantic_index']['head'] for e in [build,before,after]] ==
         [receipt['build_head'],receipt['build_head'],receipt['new_head']], 'build/signing HEAD chain')
    pins = [{n:v for n,v in e['pins'].items() if not n.startswith('artifacts/')} for e in [build,before,after]]
    need(pins[0] == pins[1] == pins[2], 'compiled source/binary pins changed across v19 signing')
    transition = {'role':'candidate','variant':'zoom-normalization-v3','compiled':True,
                  'accepted':False,'last_phase':'zoom-normalization-build-2'}
    need(all(e['registered_number_transition'] == transition for e in [build,before,after]),
         'compiled unaccepted build2 provenance changed')
    required = dict(policy['source_roles']['candidate'], **receipt['candidate_binaries'])
    need(set(receipt['candidate_binaries']) == set(policy['normal_binaries']) and
         all(after['pins'].get(n) == pin for n,pin in required.items()), 'candidate source/binary binding')


def validate(root, here, policy, helper):
    receipt = helper.read(here / 'HEAD-SUCCESSION.json')
    for name,pin in receipt['pins'].items():
        helper.need(helper.sha(root / name) == pin, 'signed/build evidence: ' + name)
    previous = root / receipt['fixture_predecessor']
    helper.authenticate(previous, receipt['fixture_predecessor_manifest_sha256'])
    proposal = root / receipt['proposal']
    helper.authenticate(proposal, receipt['proposal_manifest_sha256'])
    helper.need(helper.sha(here / 'assess.py') == receipt['assessor_sha256'] == helper.sha(previous / 'assess.py'),
                'unchanged comparison assessor')
    for name in ['SOURCE-PINS.json','SELECTED.json','TARGET-SUBTESTS.json','HELD-SUBTESTS.json',
                 'HELD-COMPARISON-POLICY.json','REGRESSION-SUBTESTS.json','SUBSET-MANIFEST.json',
                 'EXISTING-MANIFEST-ENTRIES.json','REFERENCES-TO-COPY.json','ADOPTED-ORIGINAL.json']:
        helper.need((here / name).read_bytes() == (previous / name).read_bytes(), 'unchanged fixtures/baseline: ' + name)
    for item in helper.read(here / 'SOURCE-PINS.json').values():
        if item['exists']:
            helper.need(helper.sha(here / item['capture']) == item['sha256'], 'fixture body binding')
    roles = helper.read(proposal / 'SOURCE-ROLES.json')
    for item in roles.values():
        helper.need(helper.sha(root / item['base']) == item['base_sha256'] and
                    helper.sha(root / item['candidate']) == item['candidate_sha256'], 'proposal source bodies')
    build,before,after = [helper.read(root / receipt[key]) for key in ['build_epoch','before_epoch','after_epoch']]
    validate_core(receipt,policy,helper.read(previous / 'POLICY.json'),roles,build,before,after,helper.need)
    helper.need(helper.sha(root / receipt['after_epoch']) == receipt['current_epoch_sha256'], 'current signed epoch digest')
    result = helper.read(root / receipt['build_result'])
    helper.need(result['command_success'] and result['preservation_verified'] and not result['owned_processes'] and
                not result['publication_errors'], 'successful terminal preserved build')
    env = dict(os.environ, GIT_OPTIONAL_LOCKS='0')
    helper.need(all(not env.get(k) for k in ['GIT_DIR','GIT_WORK_TREE','GIT_INDEX_FILE','GIT_OBJECT_DIRECTORY',
                                           'GIT_ALTERNATE_OBJECT_DIRECTORIES']), 'unexpected Git environment')
    def git(*args):
        return subprocess.check_output(['git','--no-optional-locks','-c','core.fsmonitor=false','-C',str(root),*args],
                                       env=env,stderr=subprocess.PIPE)
    parent = receipt['old_head']
    helper.need(len(receipt['receipts']) == 15, 'exact fifteen signed research successors')
    for name in receipt['receipts']:
        item = helper.read(root / name)
        helper.need(item['parent'] == parent and item['signature_verified'] and
                    item['working_bodies_and_nested_index_preserved'], 'signed receipt chain')
        helper.need(git('rev-list','--parents','-n','1',item['commit']).decode().split() == [item['commit'],parent],
                    'actual single parent')
        helper.need(git('rev-parse',item['commit']+'^{tree}').decode().strip() == item['tree'], 'actual signed tree')
        git('-c','gpg.ssh.allowedSignersFile='+str(root/'artifacts/css-local-signing-20261027-v1/allowed-signers'),
            'verify-commit',item['commit'])
        paths = [n.decode() for n in git('diff-tree','--no-commit-id','--name-only','-r','-z',item['commit']).split(b'\0') if n]
        helper.need(set(paths) == set(item['files']) and all(n.startswith('artifacts/') and
                    n != 'artifacts/css-spec-lean' and not n.startswith('artifacts/css-spec-lean/') for n in paths),
                    'exact artifact-only path set, nested repository untouched')
        parent = item['commit']
    helper.need(parent == receipt['new_head'] and not git('diff','--name-only',receipt['old_head'],receipt['new_head'],
                '--','.',':(exclude)artifacts'), 'no native committed-tree change across research chain')
    directory = root / 'artifacts/css-local-signing-20261027-v19'
    final = helper.read(directory / 'FINAL-CHECK.json')
    helper.need(final['head'] == receipt['new_head'] and final['signatures_verified'] and
                final['runtime_epoch_synchronized'] and not final['candidate_accepted'] and
                final['current_epoch_sha256'] == receipt['current_epoch_sha256'], 'final signed preservation')
    ledger = helper.read(directory / 'ROADMAP-UPDATE.json')
    prior = helper.read(root / ledger['prior_authorized_ledger_update'])
    helper.need(prior['after'] == ledger['before'] and
                all(after['pins'].get(n) == pin for n,pin in ledger['after'].items()), 'v18 to v19 ledger continuation')
    return {'old_head':receipt['old_head'],'build_head':receipt['build_head'],'new_head':receipt['new_head'],
            'signed_research_commits':15,'current_epoch_sha256':receipt['current_epoch_sha256'],
            'candidate_binaries':receipt['candidate_binaries'],'native_sources_and_binaries_unchanged_during_v19':True,
            'original_provenance_retained':True}
