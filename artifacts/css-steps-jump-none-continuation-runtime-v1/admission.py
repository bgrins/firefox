import hashlib
import json
from pathlib import Path


def admit(root, binding, policy, tests, roster, pre, post, binary_roles):
    def need(value, message):
        if not value:
            raise RuntimeError(message)
    def read(path):
        return json.loads(path.read_text())
    def sha(path):
        return hashlib.sha256(path.read_bytes()).hexdigest()
    def ref(item):
        name = Path(item['path'])
        need(not name.is_absolute() and '..' not in name.parts, 'relative evidence')
        path = root / name
        need(sha(path) == item['sha256'], str(path))
        return path, read(path)
    _, receipt = ref(binding)
    need(receipt['status'] == 'STEPS_CANDIDATE_BUILD_RECONCILED' and receipt['exit'] == 0,
         'successful external reconciliation')
    manifest_path, manifest = ref(receipt['source_runtime'])
    need(manifest_path.name == 'FILES.json', 'failed runtime manifest')
    runtime = manifest_path.parent
    for name, item in manifest.items():
        relative = Path(name)
        need(not relative.is_absolute() and '..' not in relative.parts, 'manifest path')
        digest = item['sha256'] if isinstance(item, dict) else item
        need(sha(runtime / relative) == digest, name)
    execution = read(runtime / 'ROOT-EXECUTION.json')
    need(set(receipt['execution']) == {'session', 'outer_exit', 'terminal'}
         and {k: execution[k] for k in receipt['execution']} == receipt['execution']
         and execution['launch'] == '640ebb', 'actual failed outer execution')
    need(execution['session'] == 37176 and execution['outer_exit'] == 1
         and execution['terminal'] == '10fbf0', 'specific retained failed attempt')
    result = read(runtime / 'RESULT.json')
    build = read(runtime / 'candidate-build/build-RESULT.json')
    process = read(runtime / 'candidate-build/build-PROCESS.json')
    wake = read(runtime / 'candidate-build/WAKE-PROCESS.json')
    wake_result = read(runtime / 'candidate-build/WAKE-RESULT.json')
    need(build['exit'] == 0 and build['error'] is None and build['stop_reason'] is None,
         'candidate compilation completed')
    need(build['cleanup_errors'] == ["build group census: PermissionError(1, 'Operation not permitted')"]
         and not build['owned_group_absent'], 'preserved cleanup-only failure')
    need(process['command'] == ['/Users/bgrins/venvs/firefox/bin/python', './mach', 'build', '-j', '2']
         and process['cwd'] == str(root) and process['objdir'] == str(root / 'objdir-full.noindex'),
         'actual candidate build command')
    need(process['pid'] == process['pgid'] and wake['pid'] == wake['pgid']
         and wake['build_pid'] == process['pid'], 'retained owned groups')
    need(wake_result == {'exit': 0, 'owned_group_absent': True}, 'wake completion')
    need(receipt['groups_absent'] == sorted([process['pgid'], wake['pgid']]) and receipt['evidence'], 'external absence evidence')
    for item in receipt['evidence']:
        ref(item)
    need(result['captured_phases'] == ['original'] and result['source_transitions'] == ['candidate']
         and result['mutation_started'] and not result['success'] and result['wpt_group'] is None
         and result['outstanding_processes'] == {'build': process['pgid']}, 'failed attempt retained')
    need(receipt['owned_inputs'] == result['owned_inputs'] and set(result['owned_inputs']) == set(pre),
         'all four owned inputs')
    for name, item in result['owned_inputs'].items():
        need(item['path'] == name and item['owned_sha256'] == post[name]['sha256']
             and len(item['identity']) == 2, 'candidate body/identity ' + name)
    need(set(receipt['binaries']) == binary_roles
         and all(isinstance(v, str) and len(v) == 64 and all(c in '0123456789abcdef' for c in v)
                 for v in receipt['binaries'].values()), 'four actual candidate binary hashes')
    for name in ['PREIMAGES.json', 'POSTIMAGES.json', 'CANDIDATE-ROSTER.json', 'COMPARISON-POLICY.json']:
        need(sha(runtime / name) == sha(Path(__file__).parent / name), 'unchanged experiment ' + name)
    run = read(runtime / 'wpt-original/RUN.json')
    events = [json.loads(line) for line in (runtime / 'wpt-original/raw.json').read_text().splitlines()]
    for key, action in [('rows', 'test_status'), ('starts', 'test_start'), ('ends', 'test_end')]:
        need(run[key] == [e for e in events if e.get('action') == action], 'raw original ' + key)
    config = {'expected_subtests': roster, 'reftests': []}
    need(run['complete'] and run['before'] == run['after'] and not run['infrastructure_faults']
         and not tests.infrastructure_faults(events) and tests.lifecycle(events, config)
         and tests.exit_matches_results(run['exit'], run['rows'] + run['ends']), 'original lifecycle/exit')
    need(len(run['starts']) == len(run['ends']) == len(roster)
         and all(e['status'] == e.get('expected', e['status']) == 'OK'
                 and not e.get('known_intermittent') for e in run['ends']), 'original harnesses')
    for name, names in roster.items():
        need([r['subtest'] for r in run['rows'] if r['test'] == name] == names, 'original exact roster')
    need(read(runtime / 'wpt-original/CLEANUP.json') == {'owned_group_absent': True, 'errors': []},
         'original browser cleanup')
    baseline = policy.check(run['rows'], read(runtime / 'COMPARISON-POLICY.json'), 'original')
    need(read(runtime / 'original-POST.json')['pins'] == run['after'], 'original post-capture source join')
    build_pre = read(runtime / 'candidate-BUILD-PRE.json')['pins']
    need(all(build_pre[n] == post[n]['sha256'] for n in pre), 'candidate build source bodies')
    need(all(build_pre[n] == v for n, v in run['after'].items() if n not in pre),
         'only reviewed source transition before candidate build')
    return receipt, result['owned_inputs'], baseline
