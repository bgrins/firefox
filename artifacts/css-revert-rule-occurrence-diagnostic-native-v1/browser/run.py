import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
_occurrence = None


def active_processes():
    return () if _occurrence is None else _occurrence.active_processes()


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run(root, output, pins, cancelled):
    global _occurrence
    assert __debug__ and _occurrence is None and not cancelled()
    assert pins.get('execution_enabled') is True and pins['source_role'] == 'candidate'
    assert pins.get('browser_environment') == {'CSS_OCCURRENCE_TRACE': '1'}
    root, output = Path(root).resolve(), Path(output).absolute()
    assert output.parent.resolve().is_relative_to(root / 'artifacts')
    assert not output.exists() and not output.is_symlink()
    catalog = json.loads((HERE / 'CATALOG.json').read_bytes())
    for name, digest in catalog['files'].items():
        assert sha(root / name) == digest, name
    package = root / catalog['fixture_directory']
    manifest = json.loads((package / 'FILES.json').read_bytes())
    assert all(sha(package / name) == digest for name, digest in manifest.items())
    _occurrence = load('occurrence_diagnostic_lane', HERE / 'occurrence.py')
    analyzer = load('occurrence_diagnostic_analyzer', root / catalog['analyzer'])
    output.mkdir()
    save(output / 'PINS.json', pins)
    observations, trace, error = {}, None, None
    try:
        observations['occurrence'] = _occurrence.run(root, output / 'occurrence', pins, cancelled)
        raw = output / 'occurrence/raw.jsonl'
        records = [json.loads(line) for line in raw.read_text().splitlines() if line.strip()]
        trace = analyzer.analyze_records(records)
        trace['input'] = {'path': str(raw.relative_to(root)), 'sha256': sha(raw), 'records': len(records)}
        save(output / 'TRACE-ASSESSMENT.json', trace)
    except BaseException as exc:
        error = repr(exc)
    row = observations.get('occurrence', {})
    safe = error is None and not cancelled() and not active_processes() and row.get('safe_to_continue', False)
    complete = safe and row.get('complete_observation', False)
    trace_present = bool(trace and trace['native_observation_present'])
    trace_integrity = bool(trace and trace['input_integrity_ok'])
    result = {
        'source_role': pins['source_role'], 'expected_lanes': ['occurrence'], 'lanes': observations,
        'execution_error': error, 'complete_observation': complete, 'safe_to_continue': safe,
        'validation_passed': bool(complete and row.get('all_pass') and row.get('supplemental_audit_passed')
                                  and trace_present and trace_integrity),
        'trace_environment_requested': pins['browser_environment'],
        'native_trace_observed': trace_present, 'retained_trace_integrity': trace_integrity,
        'same_phase_nonadjacent_pairs': trace['same_phase_nonadjacent_pairs'] if trace else None,
        'trace_call_caps': trace['call_caps'] if trace else None,
        'timings_collected': False, 'native_fix_acceptance': False,
    }
    save(output / 'RESULT.json', result)
    return result
