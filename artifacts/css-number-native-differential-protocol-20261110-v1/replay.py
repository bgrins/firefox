import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--out', required=True, type=Path)
    a = p.parse_args()
    root = Path(__file__).resolve().parent
    manifest = json.loads((root / 'SOURCE-ONLY.json').read_text())
    for name, digest in manifest.items():
        if hashlib.sha256((root / name).read_bytes()).hexdigest() != digest:
            raise ValueError('Source changed: ' + name)
    a.out.mkdir(parents=True, exist_ok=False)
    with tempfile.TemporaryDirectory(prefix='native-number-protocol-source-only-') as temp:
        work = Path(temp)
        for name in manifest:
            destination = work / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(root / name, destination)
        result = subprocess.run([sys.executable, '-B', str(work / 'check.py')], capture_output=True, text=True)
        (a.out / 'check.log').write_text(result.stdout + result.stderr)
        if result.returncode:
            raise ValueError('Static replay failed')
        shutil.copyfile(work / 'STATIC-REPORT.json', a.out / 'REPORT.json')
    for name, digest in manifest.items():
        if hashlib.sha256((root / name).read_bytes()).hexdigest() != digest:
            raise ValueError('Source changed during replay: ' + name)


if __name__ == '__main__':
    main()
