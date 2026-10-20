import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise RuntimeError('Require python3 -I -S without optimization')
sys.dont_write_bytecode = True
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    out = args.output.resolve()
    if out.exists():
        raise RuntimeError('new output required')
    capsule = HERE / 'capsule'
    sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    identity = json.loads((HERE / 'CAPSULE-IDENTITY.json').read_text())
    for filename, key in [('FILES.json','manifest_sha256'),('FREEZE.json','freeze_sha256'),('check.py','checker_sha256')]:
        if sha(capsule / filename) != identity[key]:
            raise RuntimeError('identity ' + filename)
    spec = importlib.util.spec_from_file_location('authenticated_checker', capsule / 'check.py')
    checker = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(checker)
    count = checker.closure(capsule, identity['manifest_sha256'])
    entries = checker.read(capsule / 'FILES.json')['files']
    with tempfile.TemporaryDirectory(prefix='sticky-sentinel-v3-relocated-') as temporary:
        target = Path(temporary) / 'capsule'
        target.mkdir()
        for filename in [entry['path'] for entry in entries] + ['FILES.json','FREEZE.json']:
            dest = target / filename
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(capsule / filename, dest)
        assert checker.closure(target, identity['manifest_sha256']) == count
        argv = [sys.executable, '-I', '-S', str(target / 'check.py'), '--manifest-sha',
                identity['manifest_sha256'], '--output', str(out)]
        result = subprocess.run(argv, cwd=target.parent, text=True, capture_output=True)
        if not out.exists():
            out.mkdir(parents=True)
        (out / 'RELOCATION.stdout').write_text(result.stdout)
        (out / 'RELOCATION.stderr').write_text(result.stderr)
        receipt = {'command': argv, 'exit': result.returncode, 'source_files': count,
                   'manifest_sha256': identity['manifest_sha256'],
                   'manifest_only_copy': True, 'temporary_source_copy_removed': True}
        (out / 'RELOCATION.json').write_text(json.dumps(receipt, indent=2) + '\n')
        if result.returncode:
            raise RuntimeError('relocated replay failed')
    assert checker.closure(capsule, identity['manifest_sha256']) == count
    print(json.dumps(receipt))

if __name__ == '__main__':
    main()
