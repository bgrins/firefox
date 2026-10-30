import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    refs = json.loads((HERE / 'REFERENCES.json').read_bytes())
    for name, digest in refs.items():
        assert sha(ROOT / name) == digest, name
    spec = importlib.util.spec_from_file_location('trace_root_verifier_static', HERE / 'verify.py')
    verifier = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(verifier)
    hashes = {'assessment_sha256': 'a' * 64, 'raw_sha256': 'b' * 64, 'result_sha256': 'c' * 64}
    def case(callbacks=True, trace=True, signatures=True):
        assessment = {'complete': True, 'errors': [], 'rows': [{'status': 'PASS'} for _ in range(9)], 'ends': [{'status': 'OK'} for _ in range(3)], 'comparison_gate_passed': callbacks, 'comparison_errors': [] if callbacks else ['ordinary assertion failure']}
        if not callbacks:
            assessment['rows'][0]['status'] = 'FAIL'
        phase = {'execution_error': None, 'preservation_verified': True, 'native_fix_acceptance': False, 'comparison_gate_passed': callbacks, 'success': callbacks, 'exit': 0 if callbacks else 1}
        passed = callbacks and trace and signatures
        error = None if passed else repr(AssertionError((None, True, [], assessment['comparison_errors']))) if not callbacks else repr(AssertionError()) if not signatures else repr(AssertionError('Trace capture is incomplete; callback results remain unchanged'))
        result = {'restoration_verified': True, 'runtime_controls_unchanged': True, 'empty_staging_preserved': True, 'publication_errors': [], 'native_fix_acceptance': False, 'success': passed, 'error': error, 'candidate_phase': hashes if passed else None}
        return [result, phase, assessment, 0 if passed else 1, hashes, trace, signatures, True]
    for args in [case(), case(callbacks=False), case(trace=False), case(signatures=False)]:
        assert verifier.outcome_join(*args) == args[0]['success']
    diagnostic = case(trace=False)
    assert diagnostic[2]['comparison_gate_passed'] and not diagnostic[0]['success']
    negatives = []
    def reject(name, args):
        try:
            verifier.outcome_join(*args)
        except AssertionError:
            negatives.append(name)
        else:
            raise AssertionError(name)
    args = case(trace=False); args[0]['success'] = True; reject('diagnostic failure relabeled success', args)
    args = case(callbacks=False); args[0]['error'] = None; reject('failure error erased', args)
    args = case(); args[3] = 1; reject('invented owner exit', args)
    args = case(); args[0]['restoration_verified'] = False; reject('unverified restoration', args)
    args = case(); args[-1] = False; reject('missing PASS records', args)
    args = case(); args[2]['ends'].pop(); reject('missing ending', args)
    args = case(trace=False); args[0]['error'] = repr(AssertionError('different error')); reject('wrong diagnostic failure cause', args)
    check_trace(verifier)
    print(json.dumps({'positive_outcome_cases': 4, 'negative_cases': negatives, 'trace_replay_positive': 1, 'trace_replay_negatives': 3, 'references_authenticated': len(refs), 'live_runtime_or_current_state_read': False, 'verifier_executed': False}))


def check_trace(verifier):
    import tempfile
    def load(name, path):
        spec = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    owner = ROOT / 'artifacts/css-contextual-duration-first-read-trace-browser-v1'
    policy = json.loads((owner / 'POLICY.json').read_bytes())
    parser_path = ROOT / policy['instrumentation']['parser']
    sys.modules['trace'] = load('trace', parser_path)
    streams = load('trace_stream_fixture', parser_path.parent / 'check_trace.py')
    capture = load('saved_trace_capture_fixture', owner / 'trace_capture.py')
    mapping = json.loads((ROOT / policy['property_ids']['directory'] / 'MAPPING.json').read_bytes())
    header = {'path': mapping['header_path'], 'sha256': mapping['header_sha256'], 'expected_sha256': mapping['header_sha256'], 'matches': True}
    capture.header = lambda *args: header
    with tempfile.TemporaryDirectory(prefix='css-first-read-root-replay-', dir='/private/tmp') as temporary:
        output = Path(temporary)
        phase = output / 'candidate-wpt'
        phase.mkdir()
        rows = [streams.event('query-enter', 1), streams.event('query-exit', 2)]
        (phase / 'raw.jsonl').write_text('\n'.join(json.dumps({'action': 'process_output', 'data': streams.encode(row)}) for row in rows) + '\n')
        def save(path, value):
            with path.open('x') as stream:
                json.dump(value, stream)
        capture.capture(ROOT, output, phase, policy, header, save)
        verifier.PAIR = output
        assert verifier.replay_trace(policy, phase)['diagnostic_capture_complete']
        binding_path = output / 'TRACE-BINDING.json'
        original = binding_path.read_bytes()
        for field, value in [('raw_sha256', '0' * 64), ('trace_sha256', '0' * 64), ('diagnostic_capture_complete', False)]:
            binding = json.loads(original); binding[field] = value
            binding_path.write_text(json.dumps(binding))
            try:
                verifier.replay_trace(policy, phase)
            except AssertionError:
                pass
            else:
                raise AssertionError(field)
        binding_path.write_bytes(original)
    assert not output.exists()


if __name__ == '__main__':
    main()
