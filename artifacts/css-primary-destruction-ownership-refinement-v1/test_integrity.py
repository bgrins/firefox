import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit('use python3 -I -S, without optimization')
sys.dont_write_bytecode = True

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    output = Path(args.output)
    if not output.is_absolute() or output.exists():
        raise ValueError('new absolute output required')
    output = output.resolve()
    if output == ROOT or ROOT in output.parents:
        raise ValueError('output must be outside source')
    output.mkdir(parents=True)
    expected = hashlib.sha256((ROOT / 'FILES.json').read_bytes()).hexdigest()
    records = []

    def challenge(name, flags, mutate=None, reason='use python3 -I -S', inside=False):
        case = output / name
        source = case / 'capsule'
        shutil.copytree(ROOT, source, symlinks=True)
        target = source / 'attempt' if inside else case / 'attempt'
        marker = case / 'shadow-executed'
        if mutate:
            mutate(source, marker)
        command = [sys.executable, *flags, str(source / 'check.py'),
                   '--files-sha256', expected, '--output', str(target)]
        result = subprocess.run(command, text=True, capture_output=True, cwd=source)
        (case / 'stdout').write_text(result.stdout)
        (case / 'stderr').write_text(result.stderr)
        passed = (result.returncode != 0 and reason in result.stderr and
                  not target.exists() and not marker.exists())
        records.append({'name': name, 'command': command, 'exit': result.returncode,
                        'reason': reason, 'output_created': target.exists(),
                        'shadow_executed': marker.exists(), 'passed': passed})
        (output / 'RESULT.json').write_text(json.dumps(records, indent=2) + '\n')
        if not passed:
            raise ValueError('guard failed: ' + name)
        shutil.rmtree(source)

    challenge('optimized', ['-I', '-S', '-O'])
    challenge('double-optimized', ['-I', '-S', '-OO'])
    challenge('nonisolated', ['-S'])
    challenge('site-enabled', ['-I'])
    def shadow(source, marker):
        (source / 'json.py').write_text(
            'from pathlib import Path\nPath(' + repr(str(marker)) + ').write_text("executed")\n')
    challenge('preimport-shadow', ['-S'], shadow)
    challenge('extra-file', ['-I', '-S'],
              lambda s, _: (s / 'extra').write_text('x'), 'unexpected file')
    challenge('extra-directory', ['-I', '-S'],
              lambda s, _: (s / 'extra').mkdir(), 'unexpected directory')
    challenge('symlink', ['-I', '-S'],
              lambda s, _: (s / 'link').symlink_to('REPORT.md'), 'nonregular input')
    challenge('changed-proof', ['-I', '-S'],
              lambda s, _: (s / 'lean/Ownership.lean').write_text('changed'), 'input hash mismatch')
    challenge('missing-proof', ['-I', '-S'],
              lambda s, _: (s / 'lean/Ownership.lean').unlink(), 'missing input')
    challenge('nested-output', ['-I', '-S'], reason='output must be outside source', inside=True)
    print(json.dumps({'result': 'PASS', 'pre-output_rejections': len(records)}))


if __name__ == '__main__':
    main()
