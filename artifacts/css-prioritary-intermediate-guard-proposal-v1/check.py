import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import stat
import sys
from types import SimpleNamespace

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def load(name):
    spec = importlib.util.spec_from_file_location(name, HERE / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class MockPath:
    def __init__(self, name='root', identities=None):
        self.name = name
        self.identities = identities or {'native': (1, 2)}

    def __truediv__(self, name):
        return MockPath(self.name + '/' + name, self.identities)

    def lstat(self):
        dev, ino = self.identities[self.name.removeprefix('root/')]
        return SimpleNamespace(st_mode=stat.S_IFREG, st_dev=dev, st_ino=ino)


class MockChecks:
    def __init__(self):
        self.reads = []
        self.bodies = {'native': 'N', 'staged': 'S', 'archive': 'A', 'consumed': 'C'}
        self.cached = b''
        self.modified = b'native\n'
        self.untracked = b'untracked\n'
        self.calls = 0
        self.drift = False

    def index_state(self, path, env):
        self.calls += 1
        value = {'raw_index': 'R', 'head': 'H', 'entries': 'E', 'cached_diff': 'D'}
        if self.drift and self.calls > 2:
            value['raw_index'] = 'changed'
        return value

    def semantic_index(self, value):
        return {k: v for k, v in value.items() if k != 'raw_index'}

    def fingerprint(self, root, path):
        self.reads.append(path)
        return self.bodies[path]

    def git(self, root, env, *args):
        if args[:2] == ('diff', '--cached'):
            return self.cached
        if args[:2] == ('diff', '--name-only'):
            return self.modified
        assert args[:2] == ('ls-files', '--others')
        return self.untracked


def rejected(action):
    try:
        action()
    except (AssertionError, KeyError):
        return
    raise AssertionError('invalid state accepted')


def main():
    assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
    for path, digest in json.loads((HERE / 'REFERENCES.json').read_bytes()).items():
        assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == digest, path
    source = (ROOT / 'artifacts/css-keyframe-operation-descriptor-post-signing-proposal-v2/epoch.py').read_text()
    source = source[source.index('def verify_current('):]
    namespace = {'stat': stat}
    exec(compile(source, '<frozen-full-verifier>', 'exec'), namespace)
    full = namespace['verify_current']
    intermediate = load('intermediate').verify_intermediate
    scope = load('review_scope')
    bind_inputs = load('inputs').bind_inputs
    manifest = json.dumps({'POLICY.json': {'sha256': 'P'}, 'run.py': {'sha256': 'O'}}).encode()
    digest = hashlib.sha256(manifest).hexdigest()
    effective = bind_inputs('artifacts/owner', manifest, digest, {'consumed': 'C'})
    assert effective == {'consumed': 'C', 'artifacts/owner/POLICY.json': 'P',
                         'artifacts/owner/run.py': 'O', 'artifacts/owner/FILES.json': digest}
    assert bind_inputs('artifacts/owner', manifest, digest, effective) == effective
    rejected(lambda: bind_inputs('artifacts/owner', manifest, 'wrong', {}))
    rejected(lambda: bind_inputs('artifacts/owner', manifest, digest, {'artifacts/owner/run.py': 'wrong'}))
    rejected(lambda: bind_inputs('/absolute', manifest, digest, {}))
    for name in ('../outside', 'FILES.json'):
        bad_manifest = json.dumps({name: {'sha256': 'bad'}}).encode()
        rejected(lambda: bind_inputs('artifacts/owner', bad_manifest, hashlib.sha256(bad_manifest).hexdigest(), {}))
    epoch = {
        'raw_index_observation': {'current': 'R'},
        'semantic_index': {'head': 'H', 'entries': 'E', 'cached_diff': 'D'},
        'nested_semantic_index': {'head': 'H', 'entries': 'E', 'cached_diff': 'D'},
        'pins': {'native': 'N'}, 'staged_working': {'staged': 'S'},
        'committed_research_working_payloads': {'archive': 'A', 'consumed': 'C'},
        'installed_identities': {'native': [1, 2]},
        'modified_native_paths': ['native'], 'untracked_native': ['untracked'],
    }
    consumed = {'consumed': 'C'}
    initial = copy.deepcopy(epoch)
    root = MockPath()
    checks = MockChecks()
    complete = full(checks, root, {}, epoch)
    scope.require_full(complete)
    assert checks.reads == ['native', 'staged', 'archive', 'consumed']
    checks = MockChecks()
    limited = intermediate(checks, root, {}, epoch, consumed)
    scope.require_intermediate(limited, consumed)
    assert checks.reads == ['native', 'staged', 'consumed']
    assert limited['index'] == complete['index'] and limited['nested_index'] == complete['nested_index']
    assert epoch == initial
    checks = MockChecks()
    checks.bodies['archive'] = 'changed'
    intermediate(checks, root, {}, epoch, consumed)
    rejected(lambda: full(checks, root, {}, epoch))
    negatives = 0
    for path in ('native', 'staged', 'consumed'):
        checks = MockChecks()
        checks.bodies[path] = 'changed'
        rejected(lambda: intermediate(checks, root, {}, epoch, consumed))
        negatives += 1
    for key, value in [('cached', b'staged\n'), ('modified', b'other\n'), ('untracked', b'other\n'), ('drift', True)]:
        checks = MockChecks()
        setattr(checks, key, value)
        rejected(lambda: intermediate(checks, root, {}, epoch, consumed))
        negatives += 1
    for key in ('semantic_index', 'nested_semantic_index'):
        changed = copy.deepcopy(epoch)
        changed[key]['head'] = 'wrong'
        rejected(lambda: intermediate(MockChecks(), root, {}, changed, consumed))
        negatives += 1
    rejected(lambda: intermediate(MockChecks(), MockPath(identities={'native': (1, 3)}), {}, epoch, consumed))
    rejected(lambda: intermediate(MockChecks(), root, {}, epoch, {}))
    rejected(lambda: scope.require_full(limited))
    rejected(lambda: scope.require_intermediate(complete, consumed))
    rejected(lambda: scope.require_intermediate(dict(limited, working_sources_binaries_research_preserved=True), consumed))
    rejected(lambda: scope.require_intermediate(limited, {'consumed': 'wrong'}))
    negatives += 6
    print(json.dumps({'full_reads': 4, 'intermediate_reads': 3, 'archive_drift_intermediate_not_checked_final_rejected': True,
                      'negative_controls': negatives, 'binding_negative_controls': 5,
                      'effective_owner_map_from_authenticated_manifest': True,
                      'epoch_unchanged': epoch == initial,
                      'actual_index_source_app_process_operations': False}))


if __name__ == '__main__':
    main()
