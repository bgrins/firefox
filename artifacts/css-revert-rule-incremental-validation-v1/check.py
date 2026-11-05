import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
packages = json.loads((HERE / 'PACKAGES.json').read_bytes())
lanes = tuple(packages)


class Lane:
    def __init__(self, name, seen, failure):
        self.name, self.seen, self.failure = name, seen, failure
        self.owned = ()

    def active_processes(self):
        return self.owned

    def run(self, root, output, pins, cancelled):
        self.seen.append(self.name)
        assert pins['repetitions'] == 2
        if self.failure == 'exception':
            self.owned = (12345,)
            raise RuntimeError('synthetic cleanup failure')
        return {'complete_observation': True, 'safe_to_continue': self.failure != 'unsafe',
                'supplemental_audit_passed': self.failure != 'audit',
                'all_pass': self.name != 'controls' and self.failure != 'fail',
                'controls_unchanged': self.failure != 'fail'}


checks = {}
cases = [('preserved_control_failures_are_allowed', None, None)]
cases += [(name + '_failure_stops', name, 'fail') for name in lanes]
cases += [('last_lane_unsafe_rejected', lanes[-1], 'unsafe'),
          ('raw_audit_failure_stops', lanes[0], 'audit'),
          ('cleanup_registry_survives_exception', 'controls', 'exception')]
for label, failing_lane, failure in cases:
    spec = importlib.util.spec_from_file_location('check_' + label, HERE / 'run.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    seen = []
    modules = {name: Lane(name, seen, failure if name == failing_lane else None) for name in lanes}
    module.load_packages = lambda root: module._modules.update(modules)
    with tempfile.TemporaryDirectory(dir=HERE) as temporary:
        result = module.run(ROOT, Path(temporary) / 'output',
                            {'execution_enabled': True, 'source_role': 'candidate', 'repetitions': 2},
                            lambda: False)
        expected = lanes if failing_lane is None else lanes[:lanes.index(failing_lane) + 1]
        assert tuple(seen) == expected
        assert result['validation_passed'] == (failure is None)
        assert module.active_processes() == ((12345,) if failure == 'exception' else ())
        if failure == 'exception':
            assert not result['safe_to_continue']
        checks[label] = True
ast.parse((HERE / 'run.py').read_text())
for row in packages.values():
    directory = ROOT / row['directory']
    digest = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    assert digest(directory / 'FILES.json') == row['manifest_sha256']
    assert all(digest(directory / name) == value for name, value in
               json.loads((directory / 'FILES.json').read_bytes()).items())
checks['package_payloads_match'] = True
(HERE / 'CHECK.json').write_text(json.dumps({
    'lanes': lanes, 'browser_free_checks': checks, 'browser_or_build_executed': False,
}, indent=2) + '\n')
print(json.dumps(checks))
