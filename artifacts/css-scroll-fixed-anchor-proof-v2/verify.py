import argparse
import hashlib
import json
from pathlib import Path


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source-only', action='store_true')
    parser.add_argument('--live', action='store_true')
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    repo = root.parents[1]
    name = 'SOURCE-ONLY-v1.json' if args.source_only else 'FREEZE-v1.json'
    manifest = json.loads((root / name).read_text())
    for entry in manifest['files']:
        assert sha(root / entry['path']) == entry['sha256'], entry['path']
    inputs = json.loads((root / 'REPLAY-INPUTS-v1.json').read_text())
    for path, digest in inputs.items():
        assert sha(root / path) == digest, path
    live = 0
    for entry in json.loads((root / 'SOURCE-v1.json').read_text()):
        assert sha(root / entry['copy']) == entry['sha256'], entry['copy']
        if args.live and not entry['source'].startswith('artifacts/'):
            assert sha(repo / entry['source']) == entry['sha256'], entry['source']
            live += 1
    closure = {entry['path'] for entry in json.loads((root / 'SOURCE-ONLY-v1.json').read_text())['files']}
    assert set(inputs) <= closure
    assert {'check.py', 'bridge.py', 'fixtures.py', 'lean_cases.py', 'adapter.cpp', 'Anchor.lean', 'lean_mutations.py'} <= closure
    assert {'Traversal.lean', 'instrument.py', 'semantic.py', 'lean_semantic_cases.py',
            'traversal_mutations.py', 'extension_check.py', 'EXTENSION-SCOPE-v1.md'} <= closure
    import instrument
    for repaired in [False, True]:
        _, inventory = instrument.generate(repaired)
        assert inventory['recovery_verified']
        assert len(inventory['changes']) == 14 and len(inventory['adapter_changes']) == 5
    if not args.source_only:
        final = json.loads((root / 'FINAL-v1.json').read_text())
        summary = root / final['summary']
        assert sha(summary) == final['summary_sha256']
        data = json.loads(summary.read_text())
        assert data['status'] == 'PASS' and len(data['native_semantic_mutations']) == 12
        assert all(x['input_count'] == data['native_cases_per_variant'] and x['run_exit'] == 0
                   and x['value_differences'] > 0 for x in data['native_semantic_mutations'])
        assert len(data['lean_semantic_mutations']) == 6
        for mutation in data['lean_semantic_mutations']:
            runs = mutation['executions']
            assert mutation['proof_failure_exit'] == 1 and len(runs) == 2
            assert all(run['exit_code'] == 0 for run in runs)
            assert runs[0]['stdout'] != runs[1]['stdout']
        extension = data['required_interpreter_extension']
        assert extension['status'] == 'PASS' and extension['new_theorems'] == 37
        assert extension['cases_per_native_variant'] == 4936
        assert extension['semantic_outcomes_per_case'] == 4
        assert extension['ordinary_instrumented_state_and_provider_equality']
        assert extension['exact_uninstrumented_source_recovery']
        assert len(extension['recovery_diagnostics']) == 4
        assert all(x['corrupted_count_rejected'] for x in extension['recovery_diagnostics'])
        assert len(extension['native_semantic_mutations']) == 12
        for mutation in extension['native_semantic_mutations']:
            assert mutation['input_count'] == 4936 and mutation['run_exit'] == 0
            assert mutation['value_differences'] > 0
        assert len(extension['lean_semantic_mutations']) == 6
        for mutation in extension['lean_semantic_mutations']:
            runs = mutation['executions']
            assert mutation['proof_failure_exit'] == 1 and len(runs) == 2
            assert all(run['exit_code'] == 0 for run in runs)
            assert runs[0]['stdout'] != runs[1]['stdout']
    print(json.dumps(dict(manifest=name, files=len(manifest['files']), replay_inputs=len(inputs), live_inputs=live)))


if __name__ == '__main__':
    main()
