import hashlib
import importlib.util
import json
from pathlib import Path
import stat
import sys

def need(ok, message):
    if not ok:
        raise RuntimeError(message)

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def authenticate(root, config):
    directory = root / config['path']
    need(sha(directory / 'FILES.json') == config['manifest_sha256'], 'cost manifest identity')
    files = json.loads((directory / 'FILES.json').read_text())
    allowed_dirs = {p.as_posix() for n in files for p in Path(n).parents if p.as_posix() != '.'}
    actual = set()
    for entry in directory.rglob('*'):
        relative = entry.relative_to(directory).as_posix()
        mode = entry.lstat().st_mode
        if stat.S_ISDIR(mode):
            need(relative in allowed_dirs, 'unexpected cost directory')
        else:
            need(stat.S_ISREG(mode), 'nonregular cost input')
            actual.add(relative)
    need(actual == set(files) | {'FILES.json', 'FREEZE.json'}, 'cost closed roster')
    for name, pin in files.items():
        need(not Path(name).is_absolute() and '..' not in Path(name).parts, 'unsafe cost path')
        need(sha(directory / name) == pin, 'cost payload ' + name)
    return {str((directory / n).relative_to(root)): sha(directory / n)
            for n in sorted(actual)}

def run(wpt, name, expected_external, wpt_run):
    root, here, config = wpt.ROOT, wpt.HERE, wpt.CONFIG
    cost = config['cost']
    need(name in cost['phases'], 'unexpected cost phase')
    need(authenticate(root, cost) == expected_external, 'cost external inputs changed')
    directory = root / cost['path']
    output = here / (name + '-cost')
    paths = config['guard_sources'] + wpt.BINARIES
    expected = {str(root / n): wpt_run['after'][n] for n in paths}
    need(all(sha(Path(n)) == pin for n, pin in expected.items()), 'cost phase source/binary join')
    execution = ['probe.html', 'benchmark.js', 'CONFIG.json', 'run.py', 'validate.py', 'cleanup.py']
    expected.update({str(directory / n): sha(directory / n) for n in execution})
    command = [sys.executable, '-I', '-S', '-B', str(directory / 'run.py'),
               '--manifest-sha', cost['manifest_sha256'], '--binary', str(root / wpt.BINARIES[0]),
               '--output', str(output), '--label', name]
    for path in config['guard_sources']:
        command.extend(['--pin', str(root / path)])
    code = wpt.command(name + '-cost-runner', command)
    need(authenticate(root, cost) == expected_external, 'cost inputs changed during run')
    need(all(sha(Path(n)) == pin for n, pin in expected.items()), 'cost source/binary drift')
    need(code == 0, 'cost runner failed; WPT receipts retained')
    result = json.loads((output / 'RESULT.json').read_text())
    need(result['before'] == result['after'] == expected and result['stable'] is True,
         'cost result source/binary/fixture join')
    need(result['failure'] is None and not result['cleanupErrors'] and result['profileRemoved'] is True
         and not (output / 'profile').exists() and result['terminal'] is True
         and result['noLiveGroup'] is True and result['termination']['terminal'] is True
         and result['termination']['noLiveGroup'] is True, 'cost cleanup/termination')
    startup = result['startupEnvironment']
    need(startup['MOZ_DISABLE_SAFE_MODE_KEY'] == startup['MOZ_DISABLE_UPDATE_PROCESSING'] == '1'
         and startup['MOZ_SAFE_MODE_RESTART_removed'] is True, 'cost startup controls')
    need(json.loads((output / 'STARTUP-ENV.json').read_text()) == startup
         == result['spawn']['startupEnvironment'], 'cost startup receipt join')
    spec = importlib.util.spec_from_file_location('cost_validator', directory / 'validate.py')
    validator = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(validator)
    fixture_config = json.loads((directory / 'CONFIG.json').read_text())
    events = [json.loads(line) for line in (output / 'REQUESTS.jsonl').read_text().splitlines()]
    progress = [e['value'] for e in events if e.get('event') == 'progress-persisted']
    need(progress == validator.expected_progress(fixture_config, name)
         and len(progress) == result['progressReceipts'] == 220, 'cost progress roster')
    need(len(result['observations']) == 1, 'cost observation count')
    summary = validator.validate(result['observations'][0], fixture_config, name)
    need(summary == json.loads((output / 'SUMMARY.json').read_text())
         and summary['measuredRows'] == 90 and summary['queryReads'] == 2952000,
         'cost exact work/summary')
    need(summary['hotMismatchesByGroup'] == {}, 'clean-state hot geometry mismatch')
    return {'exit': code, 'summary': summary, 'progress': len(progress),
            'result_sha256': sha(output / 'RESULT.json'), 'cleanup_verified': True}
