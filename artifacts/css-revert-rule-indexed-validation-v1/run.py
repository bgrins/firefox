import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
_modules = {}


def active_processes():
    return tuple(sorted({pid for module in _modules.values() for pid in module.active_processes()}))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')


def load_packages(root):
    assert not _modules
    for lane, row in json.loads((HERE / 'PACKAGES.json').read_bytes()).items():
        directory = root / row['directory']
        assert sha(directory / 'FILES.json') == row['manifest_sha256']
        manifest = json.loads((directory / 'FILES.json').read_bytes())
        assert all(sha(directory / name) == digest for name, digest in manifest.items())
        spec = importlib.util.spec_from_file_location('indexed_' + lane, directory / 'run.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        _modules[lane] = module


def run(root, output, pins, cancelled):
    assert __debug__ and not active_processes() and not cancelled()
    assert pins.get('execution_enabled') is True and pins['source_role'] == 'candidate'
    assert pins.get('repetitions') == 2
    root, output = Path(root).resolve(), Path(output).absolute()
    assert output.parent.resolve().is_relative_to(root / 'artifacts')
    assert not output.exists() and not output.is_symlink()
    load_packages(root)
    output.mkdir()
    save(output / 'PINS.json', pins)
    observations, error = {}, None
    try:
        for lane in ('correctness', 'controls', 'timing'):
            if cancelled():
                raise InterruptedError('Cancelled before ' + lane)
            row = _modules[lane].run(root, output / lane, pins, cancelled)
            observations[lane] = row
            gate = 'controls_unchanged' if lane == 'controls' else 'all_pass'
            if not (row['safe_to_continue'] and row['complete_observation'] and row[gate]):
                break
    except BaseException as exc:
        error = repr(exc)
    complete = error is None and not cancelled() and len(observations) == 3 and all(
        row['complete_observation'] for row in observations.values())
    validated = complete and observations['correctness']['all_pass'] and observations['controls']['controls_unchanged'] and observations['timing']['all_pass']
    result = {
        'source_role': pins['source_role'], 'lanes': observations, 'execution_error': error,
        'complete_observation': complete,
        'safe_to_continue': error is None and not cancelled() and not active_processes() and all(
            row['safe_to_continue'] for row in observations.values()),
        'validation_passed': validated,
        'controls_unchanged': observations.get('controls', {}).get('controls_unchanged', False),
        'timing_threshold_applied': False, 'native_fix_acceptance': False,
    }
    save(output / 'RESULT.json', result)
    return result
