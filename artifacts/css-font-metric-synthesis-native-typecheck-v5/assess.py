import hashlib
import json
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit


CRATES = {
    'style': 'servo/components/style',
    'geckoservo': 'servo/ports/geckolib',
}


def assess(body, exit_code, root, object_directory):
    root, object_directory = Path(root), Path(object_directory)
    assert root.is_absolute() and object_directory.is_absolute()
    errors, records, artifacts, warnings = [], [], {}, []
    finished = []
    for number, line in enumerate(body.decode('utf-8', errors='strict').splitlines(), 1):
        stripped = line.strip()
        if not stripped.startswith('{'):
            if re.match(r'^(?:error(?:\[[^]]+\])?:|fatal error:|Traceback \(most recent call last\):)', stripped):
                errors.append({'line': number, 'error': 'unstructured tool error', 'text': line})
            continue
        try:
            record = json.loads(stripped)
        except ValueError:
            errors.append({'line': number, 'error': 'malformed JSON'})
            continue
        if not isinstance(record, dict) or 'reason' not in record:
            errors.append({'line': number, 'error': 'unrecognized JSON record'})
            continue
        reason = record['reason']
        records.append({'line': number, 'record': record})
        if finished:
            errors.append({'line': number, 'error': 'Cargo record after build-finished'})
        if reason == 'build-finished':
            finished.append(record)
        elif reason == 'compiler-message':
            message = record.get('message', {})
            if message.get('level') == 'error':
                errors.append({'line': number, 'error': 'compiler error', 'record': record})
            elif message.get('level') == 'warning':
                warnings.append(record)
        elif reason == 'compiler-artifact':
            target = record.get('target', {})
            name = target.get('name')
            if name not in CRATES:
                continue
            directory = root / CRATES[name]
            package = record.get('package_id', '')
            parsed = urlsplit(package.removeprefix('path+'))
            fragment = parsed.fragment
            valid_package = package.startswith(('path+file:', 'file:')) and parsed.scheme == 'file' and parsed.netloc == '' and unquote(parsed.path) == str(directory)
            valid_package &= bool(re.fullmatch(r'(?:' + name + r'@)?\d+\.\d+\.\d+(?:[-+][A-Za-z0-9.-]+)?', fragment))
            filenames = record.get('filenames', [])
            valid_files = isinstance(filenames, list) and bool(filenames)
            valid_files &= all(isinstance(f, str) and Path(f).is_absolute() and '..' not in Path(f).parts and Path(f).is_relative_to(object_directory) for f in filenames)
            valid = (
                record.get('manifest_path') == str(directory / 'Cargo.toml')
                and target.get('src_path') == str(directory / 'lib.rs')
                and set(target.get('kind', [])) & {'lib', 'rlib'}
                and set(target.get('crate_types', [])) & {'lib', 'rlib'}
                and record.get('profile', {}).get('test') is False
                and isinstance(record.get('fresh'), bool)
                and valid_package and valid_files
            )
            if not valid:
                errors.append({'line': number, 'error': 'incorrect requested library artifact', 'record': record})
            elif name in artifacts:
                errors.append({'line': number, 'error': 'duplicate requested library artifact', 'name': name})
            else:
                artifacts[name] = record
        elif reason != 'build-script-executed':
            errors.append({'line': number, 'error': 'unknown Cargo reason', 'reason': reason})
    if exit_code != 0:
        errors.append({'error': 'Mach process failed', 'exit': exit_code})
    if len(finished) != 1 or finished[0].get('success') is not True:
        errors.append({'error': 'missing, failed or ambiguous Cargo completion'})
    if set(artifacts) != set(CRATES):
        errors.append({'error': 'requested library artifacts missing', 'observed': sorted(artifacts)})
    return {
        'success': not errors, 'log_sha256': hashlib.sha256(body).hexdigest(),
        'mach_exit': exit_code, 'errors': errors, 'warnings': warnings,
        'requested_library_artifacts': artifacts, 'build_finished': finished,
        'cargo_records': records, 'native_fix_acceptance': False,
        'source_and_config_binding_verified_by_parser': False,
    }
