import copy
import hashlib
import json
import re


def need(value, message):
    if not value:
        raise RuntimeError(message)


def admit(epoch, manifest_path, reviewed, selection, applied_expected, producer):
    directory = manifest_path.parent
    root = directory.parents[1]
    manifest = json.loads(manifest_path.read_text())

    def payload(name, text=False):
        body = (directory / name).read_bytes()
        need(hashlib.sha256(body).hexdigest() == manifest[name], 'owner payload ' + name)
        return body.decode() if text else json.loads(body)

    def external(ref):
        body = (root / ref['path']).read_bytes()
        need(hashlib.sha256(body).hexdigest() == ref['sha256'], 'owner prerequisite ' + ref['path'])
        return json.loads(body)

    need(hashlib.sha256(payload('run.py', text=True).encode()).hexdigest() == producer['producer_sha256'], 'reviewed owner producer')
    terminal = payload('ROOT-EXECUTION.json')
    need(type(terminal.get('session')) is int and terminal['session'] > 0
         and terminal.get('outer_exit') == 0
         and all(isinstance(terminal.get(k), str) and terminal[k] for k in ('launch', 'terminal')),
         'actual successful owner terminal')
    source = payload('SOURCE-EPOCH.json')
    need(source == external(producer['source_epoch']), 'actual passed unit source epoch')
    unit = external(producer['unit_result'])
    need(unit['status'] == 'UNIT_AND_DOC_TESTS_PASS' and unit['preservation'] is True
         and unit['diagnostics'] == {'E0597': 2, 'E0277': 2}, 'passed unit prerequisite')
    current = payload('CURRENT-EPOCH.json')
    applied = payload('APPLIED.json')
    need(applied == applied_expected == external(producer['applied']), 'exact reviewed owner application')
    need(len(applied['postimages']) == 18 and len(applied['preserved']) == 10
         and not set(applied['postimages']) & set(applied['preserved']), 'composed 18 sources and 10 retained guards')
    execution = payload('EXECUTION.json')
    binaries = payload('BINARIES.json')
    result = payload('RESULT.json')
    need(epoch == current, 'exact actual owner completion epoch')
    need([r['phase'] for r in execution] == ['metadata', 'export', 'binaries', 'gtest'], 'all owner phases')
    previous_finish = None
    for record in execution:
        name = record['phase']
        need(record['exit'] == 0 and record == payload(name + '-EXECUTION.json'), 'successful owner phase ' + name)
        command = payload(name + '-COMMAND.json')
        need(command['command'] == producer['commands'][name], 'actual owner command ' + name)
        need(type(command.get('started')) in (int, float) and type(record.get('finished')) in (int, float)
             and command['started'] <= record['finished']
             and (previous_finish is None or previous_finish <= command['started']), 'ordered owner phases ' + name)
        previous_finish = record['finished']
        log_body = payload(name + '.log', text=True)
        need(record['log_sha256'] == hashlib.sha256(log_body.encode()).hexdigest(), 'owner phase log ' + name)
    need(result['status'] == 'COMPACT_OWNER_BUILD_AND_17_TESTS_PASS' and result['preservation'] is True
         and result['source_composition'] == 'owner17_plus_corrected_borrow4_equals_18', 'owner terminal result')
    before, preservation = payload('BEFORE.json'), payload('PRESERVATION.json')
    semantic = lambda state: {k: state[k] for k in ('head', 'entries', 'cached_diff', 'working_diff')}
    for receipt in (before, preservation):
        need(receipt['current_raw_stable_during_check'] is True
             and receipt['working_sources_binaries_research_preserved'] is True, 'owner preservation success')
        need(semantic(receipt['index']) == source['semantic_index']
             and receipt['index']['raw_index'] == source['raw_index_observation']['current'], 'owner main index preservation')
        need(semantic(receipt['nested_index']) == source['nested_semantic_index'], 'owner nested index preservation')
    need(before['index'] == preservation['index'] and before['nested_index'] == preservation['nested_index'], 'full owner index interval')
    log = payload('gtest.log', text=True)
    events = re.findall(r'TEST_(START|END): ([^\r\n]+)', log)
    need(len(events) == 34 and [list(e) for e in events] == result['events'], 'actual GTest event join')
    names = []
    for start, end in zip(events[::2], events[1::2]):
        need(start[0] == 'START' and end == ('END', 'PASS'), 'matched passing GTest lifecycle')
        names.append(start[1])
    need(len(set(names)) == 17 and sorted(names) == sorted(selection['names']), 'all 17 selected GTests')
    need('Ran 17 test(s) from 4 test suite(s) (0 disabled), with 0 failure(s).' in log, 'GTest summary')
    binary_names = {p for p in source['pins'] if p.startswith('objdir-full.noindex/') and (p.endswith('/firefox') or p.endswith('/XUL'))}
    need(len(binary_names) == 4 and set(binaries['before']) == set(binaries['after']) == binary_names, 'four actual binary roles')
    need(binaries['before'] == {p: source['pins'][p] for p in binary_names}, 'binary before map')
    need(all(isinstance(v, str) and len(v) == 64 for v in binaries['after'].values()), 'built binary hashes')
    need(binaries['after']['objdir-full.noindex/dist/bin/gtest/XUL'] == binaries['after']['objdir-full.noindex/dist/Nightly.app/Contents/MacOS/gtest/XUL'], 'GTest app packaging')
    expected = copy.deepcopy(source)
    expected['pins'].update(binaries['after'])
    expected['provenance']['compact_owner_execution'] = {
        'path': str((directory / 'EXECUTION.json').relative_to(root)),
        'sha256': manifest['EXECUTION.json'],
    }
    need(current == expected, 'source-to-completion transition')
    need(all(p in source['pins'] and source['pins'][p] == value for p, value in reviewed.items()), 'reviewed owner and retained sources')
    need(all(p in reviewed and reviewed[p] == value for p, value in (applied['postimages'] | applied['preserved']).items()), 'applied source inventory')
    source_names = set(reviewed) | set(epoch['modified_native_paths']) | set(epoch['untracked_native'])
    need(source_names <= set(source['pins']), 'complete current native source closure')
    return {p: source['pins'][p] for p in sorted(source_names)}
