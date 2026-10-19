from pathlib import Path
import hashlib
import json
import os
import shutil
import subprocess
import sys
import argparse

ROOT = Path(__file__).resolve().parent
BASE = ROOT / 'inputs/producer'


def run():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    cases = args.output.resolve()
    assert not cases.exists()
    assert not cases.is_relative_to(ROOT) and not ROOT.is_relative_to(cases)
    cases.mkdir()
    results = []
    mutations = [
        ('changed-proof', lambda p: (p / 'lean/TaintHistory.lean').write_text('import Std\n'), 'input hash'),
        ('shadow-python', lambda p: (p / 'json.py').write_text('raise RuntimeError("shadow")\n'), 'closed file roster'),
        ('shadow-lean', lambda p: (p / 'lean/Std.lean').write_text('import Init\n'), 'closed file roster'),
        ('extra-empty-directory', lambda p: (p / 'unused').mkdir(), 'closed directory roster'),
        ('symlink', lambda p: (p / 'linked').symlink_to(p / 'REPORT.md'), 'nonregular input'),
        ('fifo', lambda p: os.mkfifo(p / 'pipe'), 'nonregular input'),
        ('duplicate-freeze-key', lambda p: (p / 'FREEZE.json').write_text('{"inputs":32,"inputs":32}\n'), 'duplicate JSON key'),
        ('missing-input', lambda p: (p / 'lean/Observation.lean').unlink(), 'closed file roster'),
    ]
    for name, mutate, expected in mutations:
        capsule = cases / name
        shutil.copytree(BASE, capsule)
        mutate(capsule)
        output = cases / (name + '-output')
        r = subprocess.run([sys.executable, '-I', '-S', str(capsule / 'check.py'), '--output', str(output)], capture_output=True, text=True)
        results.append(dict(id=name, exit=r.returncode, expected_diagnostic=expected,
                            stdout=r.stdout, stderr=r.stderr, output_created=output.exists()))
        assert r.returncode != 0 and expected in r.stderr and not output.exists(), name
    for name, flags in [('not-isolated', ['-S']), ('site-enabled', ['-I']), ('optimized', ['-I', '-S', '-O'])]:
        output = cases / (name + '-output')
        r = subprocess.run([sys.executable, *flags, str(BASE / 'check.py'), '--output', str(output)], capture_output=True, text=True)
        results.append(dict(id=name, exit=r.returncode, stdout=r.stdout, stderr=r.stderr, output_created=output.exists()))
        assert r.returncode != 0 and 'isolated nonoptimized Python required' in r.stderr and not output.exists()
    for name, output in [('internal-output', BASE / 'new-output'), ('existing-output', cases)]:
        r = subprocess.run([sys.executable, '-I', '-S', str(BASE / 'check.py'), '--output', str(output)], capture_output=True, text=True)
        results.append(dict(id=name, exit=r.returncode, stdout=r.stdout, stderr=r.stderr))
        assert r.returncode != 0 and 'fresh external output required' in r.stderr
    (cases / 'GUARDS.json').write_text(json.dumps(results, indent=2) + '\n')
    print(json.dumps({'rejected': len(results), 'all_expected_diagnostics': True}))


if __name__ == '__main__':
    run()
