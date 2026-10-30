import hashlib
import importlib.util
import json
import secrets

read = lambda path: json.loads(path.read_bytes())
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run(root, here, output, policy, env, verify, owned, cancelled):
    wpt = load('progress_wpt', here / 'wpt.py')
    trace = load('first_read_capture', here / 'trace_capture.py')
    header_before = trace.header(root, policy)
    initial = verify()
    wpt.save(output / 'PHASES-PRE.json', initial)
    directory = output / 'progress-records'
    directory.mkdir(mode=0o700)
    binding = {'directory': str(directory), 'identity': [directory.stat().st_dev, directory.stat().st_ino], 'run_id': secrets.token_hex(24)}
    wpt.save(output / 'PROGRESS-BINDING.json', binding)
    phase_env = dict(env, MOZ_DURATION_FIRST_READ_TRACE='1', DURATION_PROGRESS_RECORD_DIR=str(directory), DURATION_PROGRESS_RUN_ID=binding['run_id'])
    phase = output / 'candidate-wpt'
    original = root / policy['baseline_binding']['directory'] / 'original-wpt'
    result, failure = None, None
    try:
        result = wpt.run(root, here, phase, 'candidate', policy, phase_env, verify, owned, cancelled, original)
    except BaseException as error:
        failure = error
    if (phase / 'ASSESSMENT.json').is_file():
        assessment = read(phase / 'ASSESSMENT.json')
        if assessment['complete']:
            collection = load('progress_record_collection', here / 'records.py').collect(root, directory, binding, policy, assessment)
            wpt.save(output / 'PROGRESS-RECORDS.json', collection)
            if not failure:
                assert collection['complete'] and not collection['errors']
    trace_receipt = trace.capture(root, output, phase, policy, header_before, wpt.save)
    comparison = None
    if (phase / 'ASSESSMENT.json').is_file() and read(phase / 'ASSESSMENT.json')['complete']:
        comparison = load('first_read_reference_comparison', here / 'comparison.py').compare_uninstrumented(root, policy, read(phase / 'ASSESSMENT.json'))
        wpt.save(output / 'UNINSTRUMENTED-COMPARISON.json', comparison)
    if failure:
        raise failure
    assert comparison is not None and comparison['full_callback_and_ending_signatures_equal']
    assert trace_receipt['diagnostic_capture_complete'], 'Trace capture is incomplete; callback results remain unchanged'
    assert result is not None and not owned
    assert read(phase / 'PRE.json') == read(phase / 'POST.json') == initial
    assert read(phase / 'APPLICATION-METADATA.json') == read(phase / 'APPLICATION-METADATA-POST.json')
    assert read(phase / 'BINARY-PINS.json') == read(output / 'candidate-build/RESULT.json')['binaries']
    assert verify() == initial
    wpt.save(output / 'PHASES-POST.json', initial)
    return result
