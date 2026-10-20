import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import stat
import subprocess
import sys


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def load(p):
    def unique(pairs):
        out = {}
        for k, v in pairs:
            assert k not in out, 'duplicate JSON'
            out[k] = v
        return out
    return json.loads(p.read_text(), object_pairs_hook=unique)


def main():
    args = argparse.ArgumentParser()
    args.add_argument('--producer', type=Path, required=True)
    args.add_argument('--lean', type=Path, required=True)
    args.add_argument('--output', type=Path, required=True)
    a = args.parse_args()
    review = Path(__file__).resolve().parent
    p = a.producer.resolve()
    out = a.output.resolve()
    pins = load(review / 'PRODUCER.json')
    for name, expected in pins['pins'].items():
        assert sha(p / name) == expected, name
    manifest = load(p / 'MANIFEST.json')['files']
    expected_files = set(manifest) | {'MANIFEST.json', 'FREEZE.json'}
    expected_dirs = {str(parent) for name in expected_files for parent in Path(name).parents if str(parent) != '.'}
    files, dirs = set(), set()
    for path in p.rglob('*'):
        rel = path.relative_to(p).as_posix()
        mode = path.lstat().st_mode
        assert stat.S_ISREG(mode) or stat.S_ISDIR(mode), rel
        (dirs if stat.S_ISDIR(mode) else files).add(rel)
    assert files == expected_files and dirs == expected_dirs
    for name, expected in manifest.items():
        assert not Path(name).is_absolute() and '..' not in Path(name).parts
        assert sha(p / name) == expected, name
    assert not out.exists() and not out.is_relative_to(p) and not out.is_relative_to(review)
    out.mkdir(parents=True)
    capsule = out / 'capsule'
    for name in expected_files:
        dest = capsule / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(p / name, dest)
    lean = a.lean.resolve()
    command = [sys.executable, '-I', '-S', str(capsule / 'check.py'), '--lean', str(lean), '--output', str(out / 'producer-replay')]
    run = subprocess.run(command, capture_output=True, text=True)
    (out / 'producer-driver.log').write_text(run.stdout + run.stderr)
    assert run.returncode == 0, run.stdout + run.stderr
    baseline = out / 'producer-replay/baseline'
    shutil.copyfile(review / 'Challenges.lean', baseline / 'Challenges.lean')
    env = {k: v for k, v in os.environ.items() if not k.startswith('LEAN_')}
    env['LEAN_PATH'] = str(baseline)
    challenge = subprocess.run([str(lean), 'Challenges.lean'], cwd=baseline, env=env, capture_output=True, text=True)
    (out / 'challenges.log').write_text(challenge.stdout + challenge.stderr)
    assert challenge.returncode == 0, challenge.stdout + challenge.stderr
    assert 'sorryAx' not in challenge.stdout
    expected = re.findall(r'^theorem (\w+)', (review / 'Challenges.lean').read_text(), re.M)
    actual = re.findall(r"'IndependentFragmentation\.([^']+)'", challenge.stdout)
    assert actual == expected and len(actual) == 7
    guards = []
    for kind in ['source-tamper', 'module-shadow', 'empty-directory', 'inside-output']:
        clone = out / ('guard-' + kind)
        shutil.copytree(capsule, clone)
        target = out / ('guard-output-' + kind)
        if kind == 'source-tamper':
            with (clone / 'lean/Rules.lean').open('a') as f:
                f.write('\n-- independent corruption\n')
            diagnostic = 'lean/Rules.lean'
        elif kind == 'module-shadow':
            (clone / 'json.py').write_text('raise RuntimeError("SHADOW EXECUTED")\n')
            diagnostic = 'file roster'
        elif kind == 'empty-directory':
            (clone / 'extra').mkdir()
            diagnostic = 'directory roster'
        else:
            target = clone / 'new-output'
            diagnostic = 'output must be outside capsule'
        r = subprocess.run([sys.executable, '-I', '-S', str(clone / 'check.py'), '--lean', str(lean), '--output', str(target)], capture_output=True, text=True)
        assert r.returncode != 0 and not target.exists() and diagnostic in r.stderr
        assert 'SHADOW EXECUTED' not in r.stderr
        guards.append({'case': kind, 'exit': r.returncode, 'diagnostic': r.stderr.splitlines()[-1]})
        shutil.rmtree(clone)
    result = {'producer': load(out / 'producer-replay/RESULT.json'), 'independent_challenges': actual, 'guards': guards,
              'source_pins': pins, 'producer_driver_sha256': sha(out / 'producer-driver.log'), 'challenges_sha256': sha(out / 'challenges.log')}
    (out / 'RESULT.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'status': 'PASS', 'producer_audits': len(result['producer']['exact_audits']), 'mutants': result['producer']['mutants'], 'independent_challenges': len(actual), 'guards': len(guards)}))


if __name__ == '__main__':
    main()
