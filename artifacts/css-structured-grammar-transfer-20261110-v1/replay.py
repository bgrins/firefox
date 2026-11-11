import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--lean', required=True, type=Path)
    parser.add_argument('--out', required=True, type=Path)
    args = parser.parse_args()
    output = args.out.resolve()
    output.mkdir(parents=True, exist_ok=False)
    manifest = json.loads((ROOT / 'SOURCE-ONLY.json').read_text())
    with tempfile.TemporaryDirectory(prefix='css-grammar-source-only-') as directory:
        fresh = Path(directory)
        for name, expected in manifest.items():
            path = Path(name)
            assert not path.is_absolute() and '..' not in path.parts
            raw = (ROOT / name).read_bytes()
            assert hashlib.sha256(raw).hexdigest() == expected, name
            (fresh / name).parent.mkdir(parents=True, exist_ok=True)
            (fresh / name).write_bytes(raw)
        shutil.copyfile(ROOT / 'SOURCE-ONLY.json', fresh / 'SOURCE-ONLY.json')
        command = [sys.executable, '-I', str(fresh / 'check.py'), '--lean', str(args.lean.resolve()),
            '--out', str(output / 'check')]
        with (output / 'stdout.log').open('wb') as stdout, (output / 'stderr.log').open('wb') as stderr:
            result = subprocess.run(command, cwd=fresh, stdout=stdout, stderr=stderr)
        assert result.returncode == 0, 'source-only replay failed'
    (output / 'REPLAY.json').write_text(json.dumps(dict(source_files=len(manifest),
        source_manifest_sha256=hashlib.sha256((ROOT / 'SOURCE-ONLY.json').read_bytes()).hexdigest(),
        status='PASS', temporary_sources_and_builds_removed=True), indent=2) + '\n')


if __name__ == '__main__':
    main()
