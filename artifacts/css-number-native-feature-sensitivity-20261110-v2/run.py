import argparse
import hashlib
import json
import os
from pathlib import Path
import runpy
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text())


def save(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n')


def main():
    assert sys.flags.isolated and not sys.flags.optimize
    parser = argparse.ArgumentParser()
    parser.add_argument('--repository', required=True, type=Path)
    parser.add_argument('--out', required=True, type=Path)
    args = parser.parse_args()
    manifest = read(ROOT / 'SOURCE-ONLY.json')
    for name, expected in manifest.items():
        assert sha(ROOT / name) == expected, name
    tools = read(ROOT / 'TOOLCHAIN.json')
    cargo, rustc = Path(tools['cargo']), Path(tools['rustc'])
    assert sha(cargo) == tools['cargo_sha256'] and sha(rustc) == tools['rustc_sha256']
    prepared = runpy.run_path(str(ROOT / 'prepare.py'))
    audited = runpy.run_path(str(ROOT / 'audit.py'))
    mutations = runpy.run_path(str(ROOT / 'mutate.py'))
    instrument = runpy.run_path(str(ROOT / 'inputs/instrument.py'))['instrument']
    reference = runpy.run_path(str(ROOT / 'inputs/reference_compare.py'))
    schema = runpy.run_path(str(ROOT / 'strict_model.py'))
    cases = read(ROOT / 'inputs/CASES.json')
    model = schema['read'](ROOT / 'inputs/model-rows.jsonl', cases)
    models = {case['id']: row[2] for case, row in zip([c for c in cases if c['bridge_eligible']], model)}
    dependency = read(ROOT / 'DEPENDENCIES.json')
    output = args.out.resolve()
    output.mkdir(parents=True, exist_ok=False)
    commands, controls, binaries = [], {}, {}
    with tempfile.TemporaryDirectory(prefix='css-number-feature-gate-') as directory:
        scratch = Path(directory)
        workspace = scratch / 'workspace'
        prepared['materialize'](args.repository.resolve(), workspace)
        original = (workspace / 'vendor/cssparser/src/tokenizer.rs').read_bytes()
        original_checksum = (workspace / 'vendor/cssparser/.cargo-checksum.json').read_bytes()
        assert original == (ROOT / 'inputs/tokenizer.rs').read_bytes()
        env = {k: v for k, v in os.environ.items() if not k.startswith(('CARGO_', 'RUST'))}
        env.update(CARGO_HOME=str(scratch / 'cargo-home'), CARGO_TARGET_DIR=str(scratch / 'target'),
                   CARGO_NET_OFFLINE='true', RUSTC=str(rustc), PYTHONDONTWRITEBYTECODE='1')

        def run(label, argv, stdin=None, expected=0):
            stdout, stderr = output / (label + '.stdout'), output / (label + '.stderr')
            with stdout.open('wb') as out, stderr.open('wb') as err:
                result = subprocess.run([str(x) for x in argv], cwd=workspace, env=env,
                    input=stdin, stdout=out, stderr=err)
            commands.append(dict(label=label, command=[str(x) for x in argv], exit=result.returncode,
                stdout_sha256=sha(stdout), stderr_sha256=sha(stderr)))
            save(output / 'COMMANDS.json', commands)
            assert result.returncode == expected, label
            return stdout.read_text(), stderr.read_text()

        run('cargo-version', [cargo, '--version'])
        run('rustc-version', [rustc, '-vV'])
        resolved, _ = run('resolve', [cargo, 'metadata', '--offline', '--format-version=1', '--filter-platform=' + audited['HOST']])
        resolved_features = audited['metadata'](json.loads(resolved), workspace, dependency['package_records'])
        shutil.copyfile(workspace / 'Cargo.lock', output / 'Cargo.lock')
        lock_hash = sha(workspace / 'Cargo.lock')
        raw, _ = run('metadata', [cargo, 'metadata', '--frozen', '--format-version=1', '--filter-platform=' + audited['HOST']])
        features = audited['metadata'](json.loads(raw), workspace, dependency['package_records'])
        assert features == resolved_features
        assert sha(workspace / 'Cargo.lock') == lock_hash
        save(output / 'FEATURES.json', features)
        run('feature-tree', [cargo, 'tree', '--frozen', '--target', audited['HOST'], '-e', 'features', '-p', 'cssparser'])
        for variant in ['baseline'] + list(mutations['MUTATIONS']):
            body = mutations['mutate'](original.decode(), variant)
            for traced in [False, True]:
                label = variant + ('-instrumented' if traced else '-plain')
                actual = (instrument(body) if traced else body).encode()
                sums = json.loads(original_checksum)
                sums['files']['src/tokenizer.rs'] = hashlib.sha256(actual).hexdigest()
                checksum = (json.dumps(sums, separators=(',', ':')) + '\n').encode()
                (workspace / 'vendor/cssparser/src/tokenizer.rs').write_bytes(actual)
                (workspace / 'vendor/cssparser/.cargo-checksum.json').write_bytes(checksum)
                audited['vendor'](workspace, dependency['files'], actual, checksum)
                run(label + '-clean', [cargo, 'clean', '--frozen', '-p', 'cssparser'])
                run(label + '-build', [cargo, 'build', '--frozen', '--target', audited['HOST'], '--bin', 'numeric'])
                binary = scratch / 'target' / audited['HOST'] / 'debug/numeric'
                binaries[label] = dict(binary_sha256=sha(binary), tokenizer_sha256=hashlib.sha256(actual).hexdigest(),
                    checksum_manifest_sha256=hashlib.sha256(checksum).hexdigest())
                save(output / 'BINARIES.json', binaries)
                run(label, [binary], stdin=(ROOT / 'inputs/native-input.tsv').read_bytes())
                audited['vendor'](workspace, dependency['files'], actual, checksum)
                assert sha(workspace / 'Cargo.lock') == lock_hash
            compare_args = [sys.executable, '-I', ROOT / 'compare.py',
                '--plain', output / (variant + '-plain.stdout'),
                '--instrumented', output / (variant + '-instrumented.stdout'),
                '--plain-trace', output / (variant + '-plain.stderr'),
                '--trace', output / (variant + '-instrumented.stderr'),
                '--model', ROOT / 'inputs/model-rows.jsonl', '--out', output / (variant + '-comparison.json')]
            _, error = run(variant + '-comparison', compare_args, expected=0 if variant == 'baseline' else 1)
            if variant != 'baseline':
                mutation = mutations['MUTATIONS'][variant]
                key = (mutation['witness'], 'cold')
                assert error.rstrip().endswith('ValueError: Native/JSON lexical mismatch: ' + str(key)), error
                public = reference['public_rows']((output / (variant + '-plain.stdout')).read_text())
                trace = reference['trace_rows']((output / (variant + '-instrumented.stderr')).read_text())
                case = next(c for c in cases if c['id'] == key[0])
                actual = reference['core_observation'](case, public[key], trace[key][0])
                expected = models[key[0]]
                fields = read(ROOT / 'inputs/MODEL.json')['columns']
                changed = [name for name, a, b in zip(fields, actual, expected) if a != b]
                assert changed == mutation['changed_columns'], (variant, changed)
                controls[variant] = dict(witness=key, actual=actual, expected=expected, changed_columns=changed,
                    plain_and_instrumented_completed=True, unchanged_comparison_rejected=True)
                save(output / 'MUTANTS.json', controls)
            else:
                baseline = reference['public_rows']((output / 'baseline-plain.stdout').read_text())
                historical = reference['public_rows']((ROOT / 'inputs/historical-plain.tsv').read_text())
                assert set(baseline) == set(historical)
                def lexical(row):
                    ignored = {'float_bits'}
                    if row['kind'] in ('number', 'percentage', 'dimension'):
                        ignored.add('debug')
                    return {f: v for f, v in row.items() if f not in ignored}
                assert {k: lexical(v) for k, v in baseline.items()} == {k: lexical(v) for k, v in historical.items()}
                save(output / 'PAYLOAD-OBSERVATIONS.json', [dict(case=k, historical=historical[k]['float_bits'],
                    default_features=baseline[k]['float_bits']) for k in baseline if baseline[k]['float_bits'] != historical[k]['float_bits']])
        save(output / 'BINARIES.json', binaries)
        save(output / 'MUTANTS.json', controls)
    for name, expected in manifest.items():
        assert sha(ROOT / name) == expected, name
    save(output / 'RESULT.json', dict(status='PASS', cases=196, lexical_comparisons=284,
        default_cssparser_features=sorted(audited['FEATURES']), compiled_mutants=len(controls),
        exact_model_json_types=True, scratch_removed=True, full_gecko_build_equivalence=False,
        float_conversion_proved=False, native_refinement_proved=False))


if __name__ == '__main__':
    main()
