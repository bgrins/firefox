import hashlib
import importlib.util
import json

read = lambda path: json.loads(path.read_bytes())
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()


def load(path):
    spec = importlib.util.spec_from_file_location('sealed_first_read_parser', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def header(root, policy):
    package = root / policy['property_ids']['directory']
    assert sha(package / 'FILES.json') == policy['property_ids']['manifest_sha256']
    assert sha(package / 'MAPPING.json') == policy['property_ids']['mapping_sha256']
    mapping = read(package / 'MAPPING.json')
    path = root / mapping['header_path']
    digest = sha(path) if path.is_file() else None
    return {'path': mapping['header_path'], 'sha256': digest, 'expected_sha256': mapping['header_sha256'], 'matches': digest == mapping['header_sha256']}


def capture(root, output, phase, policy, before, save):
    parser_path = root / policy['instrumentation']['parser']
    assert sha(parser_path) == policy['instrumentation']['parser_sha256']
    raw = phase / 'raw.jsonl'
    report = load(parser_path).analyze(raw.read_text().splitlines() if raw.is_file() else [])
    save(output / 'TRACE.json', report)
    after = header(root, policy)
    receipt = {
        'raw_path': str(raw.relative_to(output)),
        'raw_sha256': sha(raw) if raw.is_file() else None,
        'parser': policy['instrumentation']['parser'],
        'parser_sha256': policy['instrumentation']['parser_sha256'],
        'trace_sha256': sha(output / 'TRACE.json'),
        'generated_header': after,
        'generated_header_before': before,
        'diagnostic_capture_complete': bool(report['syntax_and_sequence_valid'] and report['closed_query_scopes'] and report['event_count'] and before == after and after['matches']),
        'first_read_phase_alignment_established': False,
        'native_causality_or_composition_proved': False,
    }
    save(output / 'TRACE-BINDING.json', receipt)
    return receipt
