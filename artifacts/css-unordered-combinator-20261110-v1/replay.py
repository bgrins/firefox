import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--lean', required=True, type=Path)
    parser.add_argument('--out', required=True, type=Path)
    args = parser.parse_args()
    lean, out = args.lean.resolve(), args.out.resolve()
    inputs = json.loads((ROOT / 'SOURCE-ONLY.json').read_text())
    with tempfile.TemporaryDirectory(prefix='css-unordered-source-') as temp:
        copy = Path(temp)
        for name, expected in inputs.items():
            data = (ROOT / name).read_bytes()
            assert hashlib.sha256(data).hexdigest() == expected, name
            target = copy / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        shutil.copyfile(ROOT / 'SOURCE-ONLY.json', copy / 'SOURCE-ONLY.json')
        subprocess.run(['python3', '-I', '-B', str(copy / 'check.py'), '--lean', str(lean), '--out', str(out)], check=True)
    assert not copy.exists()


if __name__ == '__main__':
    main()
