import ast
import copy
import difflib
import hashlib
import importlib.util
import json
from pathlib import Path
import sys


assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


assessor = load('typecheck_assessor', HERE / 'assess.py')
root = Path('/synthetic/firefox')
objdir = root / 'objdir-full.noindex'
records = []
for name, relative in assessor.CRATES.items():
    directory = root / relative
    records.append({
        'reason': 'compiler-artifact', 'package_id': 'path+' + directory.as_uri() + '#' + name + '@0.0.1',
        'manifest_path': str(directory / 'Cargo.toml'),
        'target': {'name': name, 'kind': ['lib'], 'crate_types': ['lib'], 'src_path': str(directory / 'lib.rs')},
        'profile': {'test': False}, 'fresh': False,
        'filenames': [str(objdir / 'aarch64-apple-darwin/release/deps' / ('lib' + name + '-test.rmeta'))],
    })
records.append({'reason': 'build-finished', 'success': True})


def report(rows, exit_code=0, extra=''):
    body = ('Mach startup\n' + '\n'.join(json.dumps(row) for row in rows) + '\n' + extra).encode()
    return assessor.assess(body, exit_code, root, objdir)


assert report(records)['success']
documented = copy.deepcopy(records)
for row in documented[:-1]:
    row['package_id'] = row['package_id'].removeprefix('path+')
assert report(documented)['success']
fresh = copy.deepcopy(records)
for row in fresh[:-1]:
    row['fresh'] = True
fresh.insert(0, {'reason': 'compiler-message', 'message': {'level': 'warning', 'message': 'retained warning'}})
assert report(fresh)['success'] and len(report(fresh)['warnings']) == 1
negatives = []


def reject(label, rows, exit_code=0, extra=''):
    result = report(rows, exit_code, extra)
    assert result['success'] is False, label
    negatives.append({'case': label, 'errors': result['errors']})


failed = copy.deepcopy(records)
failed[-1]['success'] = False
reject('Mach zero but Cargo failed', failed)
reject('missing completion', records[:-1])
reject('duplicate completion', records + [records[-1]])
reject('missing style', records[1:])
reject('Mach failed despite Cargo success', records, 1)
reject('compiler error despite claimed success', [{'reason': 'compiler-message', 'message': {'level': 'error'}}] + records)
reject('unstructured tool error', records, extra='error: backend failed\n')
reject('malformed JSON', records, extra='{not json\n')
reject('artifact after completion', records + [records[0]])
reject('duplicate library', [records[0]] + records)
for label, field, value in [
    ('foreign package', 'package_id', 'path+file:///other/style#style@0.0.1'),
    ('foreign scheme', 'package_id', 'registry+file:///synthetic/firefox/servo/components/style#style@0.0.1'),
    ('foreign manifest', 'manifest_path', '/other/Cargo.toml'),
    ('outside object directory', 'filenames', ['/tmp/libstyle.rmeta']),
    ('missing filenames', 'filenames', []),
    ('untyped freshness', 'fresh', None),
    ('test profile', 'profile', {'test': True}),
]:
    changed = copy.deepcopy(records)
    changed[0][field] = value
    reject(label, changed)
for field, value in [('kind', ['custom-build']), ('crate_types', ['proc-macro']), ('src_path', '/other/lib.rs')]:
    changed = copy.deepcopy(records)
    changed[0]['target'][field] = value
    reject('wrong target ' + field, changed)

old = ROOT / 'artifacts/css-hyphenation-ownership-native-pair-v1/run.py'
before, after = old.read_text(), (HERE / 'run.py').read_text()
assert (HERE / 'RUN-DELTA.patch').read_text() == ''.join(difflib.unified_diff(before.splitlines(True), after.splitlines(True), fromfile=str(old.relative_to(ROOT)), tofile=str((HERE / 'run.py').relative_to(ROOT))))
start, stop = '    finally:\n        if owned:', '    success = '
assert before[before.index(start):before.index(stop)] == after[after.index(start):after.index(stop)]
assert "for role in ('original', 'candidate')" not in after
assert "phases.run(" not in after and "./mach', 'build'" not in after
module = load('typecheck_driver', HERE / 'run.py')
assert module.EXECUTION_ENABLED is False
old_argv = sys.argv
sys.argv = [str(HERE / 'run.py'), '--run', 'synthetic']
try:
    module.main()
except AssertionError as error:
    assert str(error) == 'Unbound typecheck template; root admission required'
else:
    raise AssertionError('Disabled template executed')
finally:
    sys.argv = old_argv
ast.parse(after)
for path, digest in json.loads((HERE / 'REFERENCES.json').read_bytes()).items():
    assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == digest, path
print(json.dumps({'synthetic_positives': 3, 'synthetic_negative_cases': len(negatives), 'restoration_tail_exact': True, 'driver_disabled': True, 'no_live_operations': True, 'negative_cases': [row['case'] for row in negatives]}))
