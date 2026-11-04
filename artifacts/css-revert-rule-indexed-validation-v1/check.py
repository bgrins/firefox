import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


class Lane:
    def __init__(self, name, seen, failure=None):
        self.name, self.seen, self.failure = name, seen, failure
        self.owned = ()

    def active_processes(self):
        return self.owned

    def run(self, root, output, pins, cancelled):
        self.seen.append(self.name)
        if self.failure == 'exception':
            self.owned = (12345,)
            raise RuntimeError('synthetic cleanup failure')
        return {'complete_observation': True, 'safe_to_continue': True,
                'all_pass': self.failure != 'fail',
                'controls_unchanged': self.failure != 'fail'}


checks = {}
for label, failing_lane, failure, expected in [
    ('success', None, None, ['correctness', 'controls', 'timing']),
    ('correctness_stops', 'correctness', 'fail', ['correctness']),
    ('control_signature_stops', 'controls', 'fail', ['correctness', 'controls']),
    ('timing_failure', 'timing', 'fail', ['correctness', 'controls', 'timing']),
    ('cleanup_registry_survives_exception', 'controls', 'exception', ['correctness', 'controls']),
]:
    spec = importlib.util.spec_from_file_location('check_' + label, HERE / 'run.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    seen = []
    modules = {name: Lane(name, seen, failure if name == failing_lane else None)
               for name in ('correctness', 'controls', 'timing')}
    module.load_packages = lambda root: module._modules.update(modules)
    with tempfile.TemporaryDirectory(dir=HERE) as temporary:
        result = module.run(ROOT, Path(temporary) / 'output',
                            {'execution_enabled': True, 'source_role': 'candidate', 'repetitions': 2},
                            lambda: False)
        assert seen == expected
        assert result['validation_passed'] == (label == 'success')
        assert module.active_processes() == ((12345,) if failure == 'exception' else ())
        if failure == 'exception':
            assert not result['safe_to_continue']
        checks[label] = True
ast.parse((HERE / 'run.py').read_text())
for row in json.loads((HERE / 'PACKAGES.json').read_text()).values():
    directory = ROOT / row['directory']
    digest = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    assert digest(directory / 'FILES.json') == row['manifest_sha256']
    assert all(digest(directory / name) == value for name, value in
               json.loads((directory / 'FILES.json').read_text()).items())
checks['package_payloads_match'] = True
with (HERE / 'CHECK.json').open('x') as stream:
    json.dump({'browser_free_checks': checks, 'browser_or_build_executed': False}, stream, indent=2)
    stream.write('\n')
print(json.dumps(checks))
