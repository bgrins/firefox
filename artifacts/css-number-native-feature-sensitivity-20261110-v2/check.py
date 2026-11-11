import argparse
import ast
import copy
import hashlib
import json
from pathlib import Path
import runpy
import subprocess
import sys
import tempfile
import tomllib

ROOT = Path(__file__).resolve().parent


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def read(path):
    return json.loads(path.read_text())


def main():
    assert sys.flags.isolated and not sys.flags.optimize
    p = argparse.ArgumentParser()
    p.add_argument('--repository', required=True, type=Path)
    p.add_argument('--out', required=True, type=Path)
    args = p.parse_args()
    repository = args.repository.resolve()
    output = args.out.resolve()
    output.mkdir(parents=True, exist_ok=False)
    if (ROOT / 'SOURCE-ONLY.json').exists():
        for name, expected in read(ROOT / 'SOURCE-ONLY.json').items():
            assert sha((ROOT / name).read_bytes()) == expected, name
    for file in list(ROOT.glob('*.py')) + list((ROOT / 'inputs').glob('*.py')):
        ast.parse(file.read_text(), filename=str(file))
    for record in read(ROOT / 'PINS.json')['files']:
        actual = (ROOT / record['installed']).read_bytes()
        if record['commit']:
            origin = subprocess.check_output(['git', '-c', 'core.fsmonitor=false', '-C', str(repository),
                'show', record['commit'] + ':' + record['path']])
        else:
            origin = (repository / record['path']).read_bytes()
        assert sha(origin) == sha(actual) == record['sha256'], record['installed']
    schema = runpy.run_path(str(ROOT / 'strict_model.py'))
    mutations = runpy.run_path(str(ROOT / 'mutate.py'))
    instrument = runpy.run_path(str(ROOT / 'inputs/instrument.py'))['instrument']
    prepared = runpy.run_path(str(ROOT / 'prepare.py'))
    audited = runpy.run_path(str(ROOT / 'audit.py'))
    cases = read(ROOT / 'inputs/CASES.json')
    model = schema['read'](ROOT / 'inputs/model-rows.jsonl', cases)
    controls, confusions = [], []

    def reject(label, function):
        try:
            function()
        except (ValueError, KeyError, AssertionError):
            controls.append(label)
        else:
            raise AssertionError('Control accepted: ' + label)

    def changed(label, mutate, confused=False):
        rows = copy.deepcopy(model)
        mutate(rows)
        if confused:
            assert rows == model, label
            confusions.append(label)
        reject(label, lambda: schema['validate'](rows, cases))

    for index in [5, 6]:
        for constructor in [int, float]:
            changed(f'flag-{index}-{constructor.__name__}',
                lambda rows, i=index, c=constructor: rows[0][2].__setitem__(i, c(rows[0][2][i])), True)
    for index in range(5):
        row_index = next(i for i, row in enumerate(model) if row[2][index])
        changed(f'codes-{index}-float',
            lambda rows, i=index, r=row_index: rows[r][2][i].__setitem__(0, float(rows[r][2][i][0])), True)
    for value, name in [(False, 'bool-code'), (-1, 'negative-code'), (128, 'non-ascii-code')]:
        changed(name, lambda rows, v=value: rows[0][2][0].__setitem__(0, v))
    for index in [1, 3]:
        changed('error-flag-' + str(index), lambda rows, i=index: rows[0].__setitem__(i, 0))
    changed('observation-arity', lambda rows: rows[0][2].append(False))
    changed('missing-row', lambda rows: rows.pop())
    reject('duplicate-json-key', lambda: schema['strict_json']('{"x":0,"x":1}'))
    reject('non-finite-json', lambda: schema['strict_json']('NaN'))
    mutation_records = {}
    original = (ROOT / 'inputs/tokenizer.rs').read_text()
    for name, mutation in mutations['MUTATIONS'].items():
        altered = mutations['mutate'](original, name)
        traced = instrument(altered)
        assert altered != original and traced != altered
        index = next(i for i, case in enumerate(cases) if case['id'] == mutation['witness'])
        earlier = cases[:index]
        if name == 'reported-sign-lost':
            assert all(not c['tail'].startswith(('+', '-')) for c in earlier)
            assert cases[index]['tail'] == '-0'
        else:
            assert all('e' not in c['tail'].lower() for c in earlier)
            assert cases[index]['tail'] == '1e0'
        mutation_records[name] = dict(source_sha256=sha(altered.encode()), instrumented_sha256=sha(traced.encode()),
            expected_first_witness=mutation['witness'], first_witness_prefix_checked=True,
            compiled=False, executed=False)
    dependencies = read(ROOT / 'DEPENDENCIES.json')
    with tempfile.TemporaryDirectory(prefix='css-number-feature-preparation-') as tmp:
        workspace = Path(tmp) / 'workspace'
        prepared['materialize'](repository, workspace)
        manifest = tomllib.loads((workspace / 'Cargo.toml').read_text())
        assert manifest['dependencies']['cssparser']['default-features'] is True
        assert tomllib.loads((workspace / '.cargo/config.toml').read_text())['net']['offline'] is True
        native = tomllib.loads((workspace / 'vendor/cssparser/Cargo.toml').read_text())
        assert set(native['features']['default']) == {'fast_match_byte', 'fast_match_color'}
        for name, package in dependencies['package_records'].items():
            directory = workspace / 'vendor' / name
            native = tomllib.loads((directory / 'Cargo.toml').read_text())['package']
            assert native['name'] == name and native['version'] == package['version']
            sums = read(directory / '.cargo-checksum.json')
            assert sums['package'] == package.get('checksum'), name
            for filename, expected in sums['files'].items():
                assert sha((directory / filename).read_bytes()) == expected, (name, filename)
        audited['vendor'](workspace, dependencies['files'], (ROOT / 'inputs/tokenizer.rs').read_bytes(),
            (workspace / 'vendor/cssparser/.cargo-checksum.json').read_bytes())
        records = []
        for name, package in dependencies['package_records'].items():
            records.append(dict(id=name, name=name, version=package['version'], source=package.get('source'),
                manifest_path=str(workspace / 'vendor' / name / 'Cargo.toml')))
        records.append(dict(id='root', name='css-number-feature-gate', version='0.1.0', source=None,
            manifest_path=str(workspace / 'Cargo.toml')))
        metadata = dict(packages=records, resolve=dict(nodes=[dict(id=r['id'],
            features=sorted(audited['FEATURES']) if r['name'] == 'cssparser' else []) for r in records]))
        audited['metadata'](metadata, workspace, dependencies['package_records'])
        parser_index = next(i for i, r in enumerate(records) if r['name'] == 'cssparser')
        for label in ['missing-feature', 'extra-feature', 'source-drift', 'path-escape']:
            altered = copy.deepcopy(metadata)
            if label == 'missing-feature':
                altered['resolve']['nodes'][parser_index]['features'].remove('fast_match_color')
            elif label == 'extra-feature':
                altered['resolve']['nodes'][parser_index]['features'].append('serde')
            elif label == 'source-drift':
                altered['packages'][parser_index]['source'] = None
            else:
                altered['packages'][parser_index]['manifest_path'] = '/outside/Cargo.toml'
            reject(label, lambda a=altered: audited['metadata'](a, workspace, dependencies['package_records']))
        for source, target in [('Cargo.toml', 'Cargo.toml'), ('.cargo/config.toml', 'config.toml'), ('Cargo.lock', 'seed-Cargo.lock')]:
            (output / target).write_bytes((workspace / source).read_bytes())
    report = dict(status='source-preparation-pass', source_inputs=len(read(ROOT / 'PINS.json')['files']),
        pinned_crates=len(dependencies['package_records']), pinned_git_files=len(dependencies['files']),
        exact_typed_actual_model_rows=len(model), schema_refusals=controls[:18],
        metadata_refusals=controls[18:], python_equality_confusions_rejected=confusions,
        mutations=mutation_records, cargo_executed=False, native_compiled=False, native_executed=False,
        metadata_controls_use_synthetic_records=True, temporary_source_workspace_removed=True)
    (output / 'REPORT.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
