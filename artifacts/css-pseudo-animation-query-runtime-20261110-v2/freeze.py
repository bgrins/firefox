import importlib.util
import json
from pathlib import Path
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def main():
    assert sys.flags.isolated and not sys.flags.optimize
    head, receipt_name = sys.argv[1:]
    assert len(head) == 40 and all(c in '0123456789abcdef' for c in head)
    receipt = (ROOT / receipt_name).resolve()
    assert receipt.is_relative_to(ROOT / 'artifacts') and receipt.is_file()
    assert not (HERE / 'RUN-INPUTS.json').exists() and not (HERE / 'FREEZE-READY.json').exists()
    spec = importlib.util.spec_from_file_location('check', HERE / 'check.py')
    check = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(check)
    def git(*args):
        return subprocess.check_output(['git', '-c', 'core.fsmonitor=false', *args], cwd=ROOT)
    assert git('rev-parse', 'HEAD').decode().strip() == head
    assert not git('diff', '--name-only').strip() and not git('diff', '--cached', '--name-only').strip()
    preparation = subprocess.run([sys.executable, '-I', str(HERE / 'check.py')], capture_output=True, text=True)
    (HERE / 'FREEZE-PREPARATION.log').write_text(preparation.stdout + preparation.stderr)
    assert preparation.returncode == 0
    plan = check.load(HERE / 'RUN-PLAN.json')
    roles = check.load(HERE / 'SOURCE-ROLES.json')
    origins = check.load(HERE / 'ORIGINS.json')
    retained = check.load(receipt)
    check.validate_retained(retained, head, plan, origins, roles)
    test_tree = ROOT / 'objdir-full.noindex/_tests/testing/mochitest'
    assert test_tree.is_dir() and not test_tree.is_symlink()
    assert check.sha(ROOT / 'mozconfig') == plan['mozconfig_sha256']
    assert all(check.sha(ROOT / name) == role['base'] for name, role in roles.items())
    assert all(check.sha(ROOT / name) == digest for name, digest in retained['binaries'].items())
    for name, digest in check.load(HERE / 'runtime-inputs/test-source-pins.json').items():
        path = ROOT / name
        assert not (path.exists() or path.is_symlink()) if digest is None else check.sha(path) == digest, name
    plan.update(head=head, retained_build_origin=str(receipt.relative_to(ROOT)), retained_build_sha256=check.sha(receipt))
    (HERE / 'runtime-inputs/retained-build.json').write_bytes(receipt.read_bytes())
    (HERE / 'RUN-PLAN.json').write_text(json.dumps(plan, indent=2) + '\n')
    manifest = {name: check.sha(HERE / name) for name in check.input_names()}
    (HERE / 'RUN-INPUTS.json').write_text(json.dumps(manifest, indent=2) + '\n')
    result = subprocess.run([sys.executable, '-I', str(HERE / 'check.py'), '--frozen'], capture_output=True, text=True)
    (HERE / 'FREEZE-CHECK.log').write_text(result.stdout + result.stderr)
    assert result.returncode == 0, 'Freeze failed; no ready receipt emitted, do not run'
    (HERE / 'CHECK.json').write_text(result.stdout)
    ready = {'status': 'PASS', 'head': head, 'manifest_sha256': check.sha(HERE / 'RUN-INPUTS.json'), 'inputs': len(manifest), 'retained_build_sha256': check.sha(receipt)}
    (HERE / 'FREEZE-READY.json').write_text(json.dumps(ready, indent=2) + '\n')
    print(json.dumps(ready, indent=2))


if __name__ == '__main__':
    main()
