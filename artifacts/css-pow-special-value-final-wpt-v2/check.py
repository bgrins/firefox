import ast
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
read = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    policy = read(HERE / 'POLICY.json')
    for path in HERE.glob('*.py'):
        ast.parse(path.read_bytes())
    if (HERE / 'FILES.json').exists():
        for name, record in read(HERE / 'FILES.json').items():
            assert sha(HERE / name) == record['sha256']
            assert (HERE / name).stat().st_size == record['bytes']
    references = {**policy['references'], **policy['baseline_receipts'], **policy['build_receipts'], **policy['lint_receipts']}
    for name, pin in references.items():
        assert sha(ROOT / name) == pin, name
    for directory, pin in {**policy['packages'], policy['build_package']: policy['build_manifest']}.items():
        manifest = ROOT / directory / 'FILES.json'
        assert sha(manifest) == pin
        for name, record in read(manifest).items():
            assert sha(manifest.parent / name) == (record['sha256'] if isinstance(record, dict) else record), name
    for name in ('assess.py', 'wpt.py'):
        assert (HERE / name).read_bytes() == (ROOT / 'artifacts/css-pow-special-value-browser-v2' / name).read_bytes()
    original = ROOT / policy['baseline_runtime'] / 'original-wpt'
    settings = read(original / 'ASSESSMENT-POLICY.json')
    fixture = 'css/css-values/pow-special-value-context.html'
    for key, expected in policy['wpt'].items():
        if key == 'resources':
            changed = dict(settings[key])
            assert changed[fixture]['sha256'] == expected[fixture]['sha256']
            changed[fixture] = expected[fixture]
            assert changed == expected
        elif key == 'metadata':
            changed = dict(settings[key])
            name = 'css/css-values/hypot-pow-sqrt-computed.html.ini'
            assert changed[name]['sha256'] == policy['deleted_metadata']['sha256']
            assert expected[name] == {'path': policy['deleted_metadata']['path'], 'sha256': None}
            changed[name] = expected[name]
            assert changed == expected
        else:
            assert settings[key] == expected, key
    assert (ROOT / policy['wpt']['resources'][fixture]['path']).read_bytes() == (original / 'tests' / fixture).read_bytes()
    lint = read(ROOT / policy['lint_result'])
    command = read(ROOT / policy['lint_command_receipt'])
    assert lint['exit'] == lint['errors'] == lint['warnings'] == lint['fixed'] == 0
    assert lint['fixture_sha256'] == policy['wpt']['resources'][fixture]['sha256']
    assert lint['log_sha256'] == sha(ROOT / policy['lint_log'])
    assert command['command'] == policy['lint_command']
    assert command['lint_receipt_sha256'] == sha(ROOT / policy['lint_result'])
    if policy['execution_enabled']:
        assert policy['activation_pending'] == [] and policy['build_receipts']
        runtime = ROOT / 'artifacts/css-registered-number-native-runtime-v1'
        assert {name:sha(runtime / name) for name in policy['controls']} == policy['controls']
        epoch = read(runtime / 'CURRENT-EPOCH.json')
        spec = importlib.util.spec_from_file_location('final_check_deletion', HERE / 'deletion.py')
        deletion = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(deletion)
        deletion.verify(ROOT, policy, epoch)
        build = ROOT / policy['build_runtime']
        assert sha(build / 'EPOCH.json') == policy['controls']['CURRENT-EPOCH.json']
        terminal = read(ROOT / policy['build_terminal'])
        assert terminal == policy['build_terminal_record']
        assert terminal['exit'] == 0 and terminal['result_sha256'] == sha(build / 'RESULT.json')
        result, inner = read(build / 'RESULT.json'), read(build / 'build-RESULT.json')
        assert result['command_success'] and result['preservation_verified'] and result['error'] is None
        assert not result['publication_errors'] and not result['owned_processes'] and not result['accepted']
        assert inner['exit'] == 0 and inner['owned_group_absent'] and not inner['cleanup_errors']
        assert inner['error'] is None and inner['stop_reason'] is None
    else:
        assert policy['activation_pending'] and policy['controls'] is None
    print(json.dumps({'checked': True, 'references': len(references), 'callbacks': 147, 'strict_control_and_ending_signatures': 131, 'execution_enabled': policy['execution_enabled'], 'browser_executed': False}, sort_keys=True))


if __name__ == '__main__':
    main()
