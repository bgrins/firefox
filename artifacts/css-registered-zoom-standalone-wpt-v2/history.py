import json


def validate(root, here, helper):
    binding = helper.read(here / 'HISTORICAL.json')
    experiment = helper.read(here / 'EXPERIMENT.json')
    events, provenance = [], []
    for record in binding['records']:
        capsule, directory = root / record['capsule'], root / record['runtime']
        helper.authenticate(capsule, record['manifest_sha256'])
        for name,pin in record['pins'].items():
            path = directory / name
            helper.need(path.is_file() and not path.is_symlink() and helper.sha(path) == pin, 'historical evidence: ' + name)
        assessment, result = [helper.read(directory / n) for n in ['ASSESSMENT.json','RESULT.json']]
        helper.need(assessment['complete'] and assessment['execution_preserved'] and result['observation_gate_passed'] and
                    result['execution_error'] is None and result['preservation_error'] is None, 'complete historical execution')
        helper.need(assessment['native_sources'] == binding['native_sources'] and
                    assessment['capsule_manifest_sha256'] == record['manifest_sha256'], 'historical combined-nine source role')
        epoch = helper.read(directory / 'EPOCH.json')
        helper.need(helper.sha(directory / 'EPOCH.json') == assessment['epoch_sha256'] and
                    all(epoch['pins'].get(n) == pin for n,pin in binding['native_sources'].items()), 'historical epoch')
        metadata = helper.read(directory / 'APPLICATION-METADATA.json')
        helper.need(metadata == helper.read(directory / 'APPLICATION-METADATA-POST.json') == assessment['run_binding'] and
                    metadata['revision'] == epoch['semantic_index']['head'], 'historical metadata retained')
        helper.need(helper.read(directory / 'PRE.json') == helper.read(directory / 'POST.json'), 'historical full preservation')
        cleanup = helper.read(directory / 'CLEANUP.json')
        helper.need(cleanup['owned_group_absent'] and cleanup['temporary_root_removed'], 'historical cleanup')
        helper.need(all(epoch['pins'].get(n) == pin for n,pin in helper.read(directory / 'NORMAL-BINARIES.json').items()), 'historical binaries')
        policy = helper.read(capsule / 'POLICY.json')
        parser = helper.load('historical_parser', capsule / 'assess.py') if (capsule / 'assess.py').exists() else helper.load('historical_parser', root / policy['base_assessor'])
        checks = helper.load('historical_checks', root / policy['helpers']['checks'])
        raw = [json.loads(line) for line in (directory / 'raw.jsonl').read_text().splitlines()]
        replay = parser.assess(raw,result['exit'],policy,checks,original=None,run_binding=metadata)
        ignore = {'subtest_cardinality_policy','oracle_caveat','comparison_errors','comparison_gate_passed'}
        helper.need(replay['complete'] and all(assessment.get(n) == v for n,v in replay.items() if n not in ignore), 'historical raw replay')
        events += assessment['rows'] + assessment['ends']
        provenance.append({'runtime':record['runtime'],'assessment_sha256':record['pins']['ASSESSMENT.json'],
                           'capsule_manifest_sha256':record['manifest_sha256'],'run_binding':metadata})
    for name in experiment['zoom_source_paths']:
        helper.need(binding['native_sources'][name] == experiment['source_roles']['candidate'][name], 'same historical seven zoom bodies')
    return {'events':events,'provenance':provenance,'interpretation':binding['interpretation']}
