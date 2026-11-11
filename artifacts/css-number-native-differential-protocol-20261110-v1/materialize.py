import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parent


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--repository', required=True, type=Path)
    p.add_argument('--out', required=True, type=Path)
    a = p.parse_args()
    a.out.mkdir(parents=True, exist_ok=False)
    for record in json.loads((ROOT / 'MATERIALIZE.json').read_text())['files']:
        raw = subprocess.check_output(['git', '-C', str(a.repository), 'show', record['commit'] + ':' + record['path']])
        if hashlib.sha256(raw).hexdigest() != record['sha256']:
            raise ValueError('Pinned source mismatch: ' + record['path'])
        destination = a.out / record['destination']
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(raw)
    shutil.copyfile(ROOT / 'driver.rs', a.out / 'driver.rs')
    shutil.copyfile(ROOT / 'inputs/legacy-toolchain.json', a.out / 'TOOLCHAIN.json')
    shutil.copytree(ROOT / 'prepared', a.out / 'corpus')


if __name__ == '__main__':
    main()
