import json
from pathlib import Path


def validate(root, here, baseline_path, baseline_sha, policy, helper):
    binding = helper.read(here / 'BASELINE.json')
    helper.need(binding.get('ready') is True, 'candidate requires sealed completed standalone baseline binding')
    runtime = root / binding['runtime']
    helper.need(baseline_path == runtime / 'ASSESSMENT.json' and baseline_sha == binding['assessment_sha256'], 'exact paired baseline')
    capsule = root / binding['capsule']
    helper.authenticate(capsule,binding['capsule_manifest_sha256'])
    for name in ['EXPERIMENT.json','SOURCE-PINS.json','SELECTED.json','TARGET-SUBTESTS.json','HELD-SUBTESTS.json','SUBSET-MANIFEST.json','HISTORICAL.json','assess.py','compare.py']:
        helper.need((here/name).read_bytes() == (capsule/name).read_bytes(), 'same paired input: '+name)
    for item in helper.read(here / 'SOURCE-PINS.json').values():
        if item['exists']:
            helper.need(helper.sha(here/item['capture']) == helper.sha(capsule/item['capture']) == item['sha256'], 'same paired capture')
    files,links = {},{}
    for path in runtime.rglob('*'):
        if path.is_symlink():links[str(path.relative_to(runtime))]=str(path.readlink())
        elif path.is_file():files[str(path.relative_to(runtime))]=helper.sha(path)
    helper.need(files == binding['files'] and links == binding['symlinks'], 'exact complete baseline inventory')
    original = helper.read(baseline_path)
    result = helper.read(runtime/'RESULT.json')
    original_policy = helper.read(capsule/'POLICY.json')
    helper.need(original['phase'].startswith('original-') and original['capsule_manifest_sha256'] == binding['capsule_manifest_sha256'] and
                original['experiment_sha256'] == helper.sha(here/'EXPERIMENT.json') and original['native_sources'] == policy['source_roles']['original'], 'original phase/source/experiment provenance')
    helper.need(original['complete'] and original['execution_preserved'] and result['observation_gate_passed'] and
                result['execution_error'] is None and result['preservation_error'] is None, 'complete preserved original')
    epoch = helper.read(runtime/'EPOCH.json')
    helper.need(helper.sha(runtime/'EPOCH.json') == original['epoch_sha256'] == original_policy['epoch_sha256'], 'baseline epoch')
    helper.require_compiled_transition(epoch,'original')
    helper.load('baseline_bindings',capsule/'bindings.py').validate_phase(root,capsule,original_policy,epoch,helper)
    helper.need(epoch['modified_native_paths'] == [] and epoch['semantic_index']['head'] == policy['frozen_head'], 'baseline zero dirty sources and frozen HEAD')
    helper.need(all(epoch['pins'].get(n) == v for n,v in original['native_sources'].items()), 'baseline source epoch')
    metadata = helper.read(runtime/'APPLICATION-METADATA.json')
    helper.need(metadata == helper.read(runtime/'APPLICATION-METADATA-POST.json') == original['run_binding'], 'baseline metadata')
    helper.need(metadata['revision'] == policy['frozen_head'] and helper.read(runtime/'PRE.json') == helper.read(runtime/'POST.json'), 'baseline preservation')
    cleanup = helper.read(runtime/'CLEANUP.json')
    helper.need(cleanup['owned_group_absent'] and cleanup['temporary_root_removed'], 'baseline cleanup')
    binaries = helper.read(runtime/'NORMAL-BINARIES.json')
    helper.need(binaries == original_policy['phase_binaries'] and all(epoch['pins'].get(n)==v for n,v in binaries.items()), 'baseline built binary epoch')
    parser = helper.load('baseline_parser',capsule/'assess.py')
    checks = helper.load('baseline_checks',root/policy['helpers']['checks'])
    events = [json.loads(line) for line in (runtime/'raw.jsonl').read_text().splitlines()]
    replay = parser.assess(events,result['exit'],original_policy,checks,original=None,run_binding=metadata)
    ignore = {'subtest_cardinality_policy','oracle_caveat'}
    helper.need(replay['complete'] and all(original.get(n)==v for n,v in replay.items() if n not in ignore), 'baseline raw replay')
    return {'adopted':True,'assessment_sha256':baseline_sha,'original_capsule_sha256':binding['capsule_manifest_sha256'],
            'original_metadata_retained':True,'experiment_sha256':helper.sha(here/'EXPERIMENT.json')}
