import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parent


def main(output, lean):
    assert not output.exists() and not output.is_relative_to(ROOT)
    output.mkdir(parents=True)
    names = ['extra-directory', 'fifo', 'symlink-directory', 'duplicate-json',
             'noncanonical-name', 'changed-model', 'internal-output']
    expected = ['directory roster', 'nonregular input', 'nonregular input', 'duplicate JSON key',
                'AssertionError', 'lean/Rules.lean', 'output must be outside capsule']
    rows = []
    for name, reason in zip(names, expected):
        case = output / name
        shutil.copytree(ROOT, case)
        destination = output / (name + '-attempt')
        if name == 'extra-directory':
            (case / 'extra').mkdir()
        elif name == 'fifo':
            os.mkfifo(case / 'extra')
        elif name == 'symlink-directory':
            (case / 'alias').symlink_to(case / 'source', target_is_directory=True)
        elif name == 'duplicate-json':
            path = case / 'MANIFEST.json'
            text = path.read_text()
            path.write_text(text.replace('{', '{"files":{},', 1))
        elif name == 'noncanonical-name':
            path = case / 'MANIFEST.json'
            text = path.read_text().replace('"lean/Rules.lean"', '"lean/./Rules.lean"')
            path.write_text(text)
            freeze = json.loads((case / 'FREEZE.json').read_text())
            freeze['manifest_sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
            (case / 'FREEZE.json').write_text(json.dumps(freeze))
        elif name == 'changed-model':
            path = case / 'lean/Rules.lean'
            path.write_text(path.read_text() + '\n')
        else:
            destination = case / 'output'
        result = subprocess.run([sys.executable, '-I', '-S', str(case / 'check.py'),
                                 '--lean', str(lean), '--output', str(destination)],
                                cwd=output, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        (output / (name + '.log')).write_text(result.stdout)
        assert result.returncode != 0 and reason in result.stdout, name
        assert not destination.exists(), name
        rows.append({'name':name, 'exit_code':result.returncode, 'output_created':False,
                     'diagnostic':reason, 'log_sha256':hashlib.sha256(result.stdout.encode()).hexdigest()})
        shutil.rmtree(case)
    (output / 'RESULT.json').write_text(json.dumps({'status':'PASS','controls':rows},indent=2)+'\n')
    print(json.dumps({'status':'PASS','controls':len(rows)}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--lean', type=Path, required=True)
    args = parser.parse_args()
    main(args.output.resolve(), args.lean.resolve())
