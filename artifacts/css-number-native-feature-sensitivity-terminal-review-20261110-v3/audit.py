import hashlib
import json
from pathlib import Path
import re
import runpy
import subprocess
import sys

HERE = Path(__file__).resolve().parent
SOURCE = HERE.with_name('css-number-native-feature-sensitivity-20261110-v3')
EXECUTION = HERE.with_name('css-number-native-feature-sensitivity-execution-20261110-v3') / 'execution'


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    manifest = read(SOURCE / 'SOURCE-ONLY.json')
    assert sha(SOURCE / 'SOURCE-ONLY.json') == '2a1c3512b0421a05fe1b7fcb9f9a6cb7a7e3b8652cbd0629ae53a20b12f10ac6'
    assert all(sha(SOURCE / n) == h for n, h in manifest.items())
    reference = runpy.run_path(str(SOURCE / 'inputs/reference_compare.py'))
    mutations = runpy.run_path(str(SOURCE / 'mutate.py'))
    instrument = runpy.run_path(str(SOURCE / 'inputs/instrument.py'))['instrument']
    schema = runpy.run_path(str(SOURCE / 'strict_model.py'))
    metadata = runpy.run_path(str(SOURCE / 'audit.py'))['metadata']
    cases = read(SOURCE / 'inputs/CASES.json')
    rows = schema['read'](SOURCE / 'inputs/model-rows.jsonl', cases)
    models = {c['id']: r[2] for c, r in zip([c for c in cases if c['bridge_eligible']], rows)}
    commands = read(EXECUTION / 'COMMANDS.json')
    assert len(commands) == 25 and len({c['label'] for c in commands}) == 25
    by_label = {c['label']: c for c in commands}
    expected_failures = {n + '-comparison' for n in mutations['MUTATIONS']}
    for c in commands:
        assert c['exit'] == int(c['label'] in expected_failures)
        for stream in ['stdout', 'stderr']:
            assert sha(EXECUTION / (c['label'] + '.' + stream)) == c[stream + '_sha256']
    workspaces = {c['cwd'] for c in commands}
    assert len(workspaces) == 1
    workspace = Path(next(iter(workspaces)))
    assert not workspace.parent.exists()
    deps = read(SOURCE / 'DEPENDENCIES.json')
    feature_maps = [metadata(read(EXECUTION / (n + '.stdout')), workspace, deps['package_records']) for n in ['resolve', 'metadata']]
    assert feature_maps[0] == feature_maps[1] == read(EXECUTION / 'FEATURES.json')
    assert sha(EXECUTION / 'Cargo.lock') == 'eb88094dff2b216e2a4a59c35880a787d696c36f800281a4a66cfd1a8f3b2eeb'
    toolchain = read(SOURCE / 'TOOLCHAIN.json')
    assert sha(Path(toolchain['rustc'])) == toolchain['rustc_sha256']
    assert sha(Path(toolchain['cargo'])) == toolchain['cargo_sha256']
    binaries = read(EXECUTION / 'BINARIES.json')
    variants = ['baseline'] + list(mutations['MUTATIONS'])
    assert set(binaries) == {n + suffix for n in variants for suffix in ['-plain', '-instrumented']}
    assert len({b['target_directory'] for b in binaries.values()}) == 8
    assert len({b['binary_sha256'] for b in binaries.values()}) == 8
    source = (SOURCE / 'inputs/tokenizer.rs').read_text()
    build_summaries = {}
    for variant in variants:
        body = mutations['mutate'](source, variant)
        for traced in [False, True]:
            label = variant + ('-instrumented' if traced else '-plain')
            b = binaries[label]
            target = workspace.parent / 'targets' / label
            assert b['target_directory'] == str(target)
            assert b['binary_path'] == str(target / 'aarch64-apple-darwin/debug/numeric')
            assert not target.exists() and not Path(b['binary_path']).exists()
            assert re.fullmatch('[0-9a-f]{64}', b['binary_sha256'])
            assert re.fullmatch('[0-9a-f]{64}', b['checksum_manifest_sha256'])
            actual_source = instrument(body) if traced else body
            assert hashlib.sha256(actual_source.encode()).hexdigest() == b['tokenizer_sha256']
            build = by_label[label + '-build']
            run = by_label[label]
            assert build['cargo_target_dir'] == run['cargo_target_dir'] == str(target)
            assert run['command'] == [b['binary_path']]
            assert build['command'] == [toolchain['cargo'], 'build', '--frozen', '--target', 'aarch64-apple-darwin', '--bin', 'numeric']
            log = (EXECUTION / (label + '-build.stderr')).read_text()
            assert 'Compiling cssparser v0.38.0' in log and 'Compiling css-number-feature-gate v0.1.0' in log
            finished = re.findall(r'Finished `dev` profile \[optimized\] target\(s\) in ([0-9.]+)s', log)
            assert len(finished) == 1 and float(finished[0]) > 0
            build_summaries[label] = dict(seconds=float(finished[0]), target=str(target), recorded_binary_sha256=b['binary_sha256'])
    expected_keys = {(c['id'], phase) for c in cases for phase in (reference['PHASES'] if c['mode'] == 'history' else ['cold'])}
    summaries = {}
    for variant in variants:
        plain = reference['public_rows']((EXECUTION / (variant + '-plain.stdout')).read_text())
        traced = reference['public_rows']((EXECUTION / (variant + '-instrumented.stdout')).read_text())
        trace = reference['trace_rows']((EXECUTION / (variant + '-instrumented.stderr')).read_text())
        none = reference['trace_rows']((EXECUTION / (variant + '-plain.stderr')).read_text())
        assert plain == traced and set(plain) == set(trace) == set(none) == expected_keys
        assert not any(none.values())
        count = 0
        for case in cases:
            raw = (case['prefix'] + case['tail']).encode()
            first = plain[(case['id'], 'cold')]
            assert first['start'] == case['prefix_utf8_bytes']
            for phase in (reference['PHASES'] if case['mode'] == 'history' else ['cold']):
                key = (case['id'], phase)
                public = plain[key]
                assert public['remaining'] == raw[public['end']:] and public['start'] < public['end'] <= len(raw)
                assert len(trace[key]) == (0 if phase == 'cached' or public['kind'] == 'other' else 1)
                if trace[key]:
                    reference['core_observation'](case, public, trace[key][0])
                    count += 1
            if case['mode'] == 'history':
                assert first == plain[(case['id'], 'cached')] == plain[(case['id'], 'reparsed')]
                assert plain[(case['id'], 'suffix')] == plain[(case['id'], 'suffix-replay')]
                assert plain[(case['id'], 'suffix')]['start'] == first['end']
        cmd = [sys.executable, '-I', str(SOURCE / 'compare.py'), '--plain', str(EXECUTION / (variant + '-plain.stdout')), '--instrumented', str(EXECUTION / (variant + '-instrumented.stdout')), '--plain-trace', str(EXECUTION / (variant + '-plain.stderr')), '--trace', str(EXECUTION / (variant + '-instrumented.stderr')), '--model', str(SOURCE / 'inputs/model-rows.jsonl'), '--out', str(HERE / (variant + '-comparison.json'))]
        result = subprocess.run(cmd, capture_output=True)
        (HERE / (variant + '-comparison.stdout')).write_bytes(result.stdout)
        (HERE / (variant + '-comparison.stderr')).write_bytes(result.stderr)
        assert result.returncode == int(variant != 'baseline')
        summary = dict(public_rows=len(plain), traces=count, full_pair_transparency=True, all_reset_histories_checked=True, comparator_exit=result.returncode)
        if variant == 'baseline':
            assert read(HERE / 'baseline-comparison.json') == read(EXECUTION / 'baseline-comparison.json')
            historical = reference['public_rows']((SOURCE / 'inputs/historical-plain.tsv').read_text())
            def lexical(row):
                ignored = {'float_bits'}
                if row['kind'] in ('number', 'percentage', 'dimension'):
                    ignored.add('debug')
                return {k: v for k, v in row.items() if k not in ignored}
            assert {k: lexical(v) for k, v in plain.items()} == {k: lexical(v) for k, v in historical.items()}
            payload = [dict(case=list(k), historical=historical[k]['float_bits'], default_features=plain[k]['float_bits']) for k in plain if plain[k]['float_bits'] != historical[k]['float_bits']]
            assert payload == read(EXECUTION / 'PAYLOAD-OBSERVATIONS.json')
            summary.update(historical_lexical_rows_unchanged=True, historical_float_bit_differences=len(payload))
        else:
            mutation = mutations['MUTATIONS'][variant]
            key = (mutation['witness'], 'cold')
            expected_error = 'ValueError: Native/JSON lexical mismatch: ' + str(key)
            assert result.stderr.decode().rstrip().endswith(expected_error)
            assert (EXECUTION / (variant + '-comparison.stderr')).read_text().rstrip().endswith(expected_error)
            case = next(c for c in cases if c['id'] == key[0])
            actual = reference['core_observation'](case, plain[key], trace[key][0])
            expected = models[key[0]]
            fields = read(SOURCE / 'inputs/MODEL.json')['columns']
            changed = [f for f, a, b in zip(fields, actual, expected) if a != b]
            assert changed == mutation['changed_columns']
            receipt = read(EXECUTION / 'MUTANTS.json')[variant]
            assert receipt['actual'] == actual and receipt['expected'] == expected and receipt['changed_columns'] == changed
            summary.update(witness=key, changed_columns=changed, error=expected_error)
        summaries[variant] = summary
    report = dict(status='PASS', commands=25, intended_comparator_exits_one=sorted(expected_failures), metadata_features=feature_maps[0]['cssparser'], model_rows=len(rows), builds=build_summaries, variants=summaries, workspace_absent=True, source_hashes_reconstructed=True, binary_hashes_are_pre_cleanup_runner_receipts=True, native_execution_during_review=False)
    (HERE / 'AUDIT.json').write_text(json.dumps(report, indent=2) + '\n')
    (HERE / 'EVIDENCE.json').write_text(json.dumps({p.name: sha(p) for p in sorted(EXECUTION.iterdir()) if p.is_file()}, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
