import importlib.util
import json
from pathlib import Path
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def check():
    policy = json.loads((HERE / 'POLICY.json').read_bytes())
    package = ROOT / policy['instrumentation']['directory']
    parser = load('trace', package / 'trace.py')
    sys.modules['trace'] = parser
    streams = load('sealed_trace_checks', package / 'check_trace.py')
    streams.main()
    capture = load('owner_trace_capture', HERE / 'trace_capture.py')
    good = [streams.event('query-enter', 1), streams.event('query-exit', 2)]
    expected = {'path': 'synthetic/header', 'sha256': 'a' * 64, 'expected_sha256': 'a' * 64, 'matches': True}
    def evaluate(rows, before=expected, after=expected):
        capture.header = lambda *args: after
        with tempfile.TemporaryDirectory(prefix='css-first-read-capture-', dir='/private/tmp') as temporary:
            output = Path(temporary)
            phase = output / 'candidate-wpt'
            phase.mkdir()
            (phase / 'raw.jsonl').write_text('\n'.join(json.dumps({'action': 'process_output', 'data': streams.encode(row)}) for row in rows) + '\n')
            def save(path, value):
                with path.open('x') as stream:
                    json.dump(value, stream)
            result = capture.capture(ROOT, output, phase, policy, before, save)
            assert (output / 'TRACE.json').is_file() and (output / 'TRACE-BINDING.json').is_file()
            assert not result['first_read_phase_alignment_established'] and not result['native_causality_or_composition_proved']
        assert not output.exists()
        return result
    assert evaluate(good)['diagnostic_capture_complete']
    assert not evaluate([])['diagnostic_capture_complete']
    assert not evaluate(good[:-1])['diagnostic_capture_complete']
    assert not evaluate([good[0], dict(good[1], seq=9)])['diagnostic_capture_complete']
    assert not evaluate(good, after=dict(expected, matches=False, sha256='b' * 64))['diagnostic_capture_complete']
    assert not evaluate(good, before=dict(expected, sha256='b' * 64))['diagnostic_capture_complete']
    print(json.dumps({'capture_positive': 1, 'capture_negatives': 5, 'temporary_scratch_removed': True, 'live_header_or_browser_read': False}))


if __name__ == '__main__':
    assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
    check()
