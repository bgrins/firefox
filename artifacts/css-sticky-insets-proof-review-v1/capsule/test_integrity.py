import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit("use Python -I -S without -O or -OO")
sys.dont_write_bytecode = True
import argparse
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parent

def require(condition, message):
    if not condition:
        raise RuntimeError(message)

def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    checker = module('integrity_checker', ROOT / 'check.py')
    checker.authenticate()
    output = Path(args.output).resolve()
    require(ROOT != output and ROOT not in output.parents and not output.exists(), 'new external output required')
    output.mkdir(parents=True)
    records = []
    with tempfile.TemporaryDirectory(prefix='sticky-integrity-') as temp:
        work = Path(temp)
        capsule = work / 'capsule'
        for name in ['optimized', 'double-optimized', 'nonisolated', 'site-enabled',
                     'unsafe-shadow', 'changed-source', 'extra-file', 'extra-directory',
                     'symlink-file', 'symlink-directory', 'fifo', 'duplicate-json-key',
                     'escape-path', 'duplicate-path-spelling', 'wrong-manifest-hash',
                     'output-inside', 'wrong-tool']:
            if capsule.exists():
                shutil.rmtree(capsule)
            shutil.copytree(ROOT, capsule)
            target = work / ('output-' + name)
            flags = ['-I', '-S']
            extra = []
            marker = work / 'IMPORTED-SHADOW'
            if name == 'optimized': flags += ['-O']
            elif name == 'double-optimized': flags += ['-OO']
            elif name == 'nonisolated': flags = ['-S']
            elif name == 'site-enabled': flags = ['-I']
            elif name == 'unsafe-shadow':
                flags = ['-S']
                (capsule / 'json.py').write_text('open(' + repr(str(marker)) + ', "w").write("executed")\n')
            elif name == 'changed-source':
                with (capsule / 'replay.py').open('a') as f: f.write('\nraise RuntimeError("tampered")\n')
            elif name == 'extra-file': (capsule / 'extra.txt').write_text('extra')
            elif name == 'extra-directory': (capsule / 'extra').mkdir()
            elif name == 'symlink-file': (capsule / 'linked').symlink_to(capsule / 'replay.py')
            elif name == 'symlink-directory': (capsule / 'linked').symlink_to(capsule / 'lean', target_is_directory=True)
            elif name == 'fifo': os.mkfifo(capsule / 'pipe')
            elif name in ['duplicate-json-key', 'escape-path', 'duplicate-path-spelling']:
                path = capsule / 'FILES.json'
                data = json.loads(path.read_text())
                if name == 'duplicate-json-key':
                    text = path.read_text().replace('"algorithm": "sha256"', '"algorithm": "sha256", "algorithm": "sha256"', 1)
                else:
                    data['files']['../escape' if name == 'escape-path' else 'lean//StickyAxis.lean'] = '0' * 64
                    text = json.dumps(data)
                path.write_text(text)
                seal_path = capsule / 'FREEZE.json'
                seal = json.loads(seal_path.read_text())
                seal['manifest_sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
                seal_path.write_text(json.dumps(seal))
            elif name == 'wrong-manifest-hash':
                (capsule / 'FILES.json').write_text('{}')
            elif name == 'output-inside': target = capsule / 'new-output'
            elif name == 'wrong-tool': extra = ['--lean', sys.executable]
            run = subprocess.run([sys.executable, *flags, str(capsule / 'check.py'), '--output', str(target), *extra], text=True, capture_output=True)
            (output / (name + '.log')).write_text(run.stdout + run.stderr)
            require(run.returncode != 0 and not target.exists() and not marker.exists(), 'guard failed: ' + name)
            records.append({'name': name, 'exit': run.returncode, 'output_created': False, 'shadow_executed': False})
    replay = module('integrity_replay', ROOT / 'replay.py')
    sys.path.insert(0, str(ROOT / 'native'))
    from corpus import cases
    from oracle import observe, expected_trace
    selected = cases()[:2]
    good = []
    for case in selected:
        row = observe(case, 'combined')
        row['trace'] = expected_trace(case, 'combined')
        good.append(row)
    replay.check_rows(selected, replay.parse_rows('\n'.join(map(json.dumps, good)), selected), 'combined')
    comparators = []
    for name in ['missing-row', 'duplicate-row', 'wrong-id', 'boolean-id', 'extra-field',
                 'float-coordinate', 'changed-position', 'omitted-provider', 'duplicate-key', 'junk-suffix']:
        bad = copy.deepcopy(good)
        if name == 'missing-row': bad.pop()
        elif name == 'duplicate-row': bad[1] = bad[0]
        elif name == 'wrong-id': bad[0]['id'] = 99
        elif name == 'boolean-id': bad[0]['id'] = False
        elif name == 'extra-field': bad[0]['extra'] = 1
        elif name == 'float-coordinate': bad[0]['position'][0] = float(bad[0]['position'][0])
        elif name == 'changed-position': bad[0]['position'][0] += 1
        elif name == 'omitted-provider': bad[0]['trace'].pop()
        text = '\n'.join(map(json.dumps, bad))
        if name == 'duplicate-key': text = text.replace('"id": 0', '"id": 0, "id": 0', 1)
        elif name == 'junk-suffix': text += ' junk'
        try:
            replay.check_rows(selected, replay.parse_rows(text, selected), 'combined')
        except (RuntimeError, ValueError, TypeError):
            comparators.append({'name': name, 'rejected': True})
        else:
            raise RuntimeError('comparison corruption accepted: ' + name)
    checker.authenticate()
    result = {'status': 'pass', 'pre_dispatch_guards': records, 'comparator_guards': comparators, 'positive_comparator_rows': len(good)}
    (output / 'RESULT.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'status': 'pass', 'pre_dispatch_guards': len(records), 'comparator_guards': len(comparators)}))

if __name__ == '__main__':
    main()
