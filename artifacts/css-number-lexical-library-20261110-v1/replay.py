import argparse
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parent
BASE = 'b3d6ef2c643b848851d5e860c836abf2120e56af'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--canonical', type=Path, required=True)
    parser.add_argument('--lean', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    canonical, lean, out = args.canonical.resolve(), args.lean.resolve(), args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    inputs = json.loads((ROOT/'SOURCE-ONLY.json').read_text())
    for name, expected in inputs.items():
        if sha((ROOT/name).read_bytes()) != expected:
            raise ValueError('Frozen input changed: '+name)
    env = dict(os.environ, GIT_OPTIONAL_LOCKS='0', PYTHONDONTWRITEBYTECODE='1')
    archive = subprocess.check_output(['git','-c','core.fsmonitor=false','-C',str(canonical),'archive',BASE],env=env)
    changes = json.loads((ROOT/'CHANGES.json').read_text())
    with tempfile.TemporaryDirectory(prefix='css-number-library-') as directory:
        work = Path(directory)
        with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
            tar.extractall(work,filter='data')
        before = {p.relative_to(work).as_posix(): sha(p.read_bytes()) for p in work.rglob('*') if p.is_file()}
        for record in changes:
            path = work/record['path']
            if (sha(path.read_bytes()) if path.exists() else None) != record['before']:
                raise ValueError('Base mismatch: '+record['path'])
        command = ['git','apply','--check',str(ROOT/'integration.patch')]
        result = subprocess.run(command,cwd=work,env=env,capture_output=True,text=True)
        (out/'patch-check.log').write_text(result.stdout+result.stderr)
        if result.returncode: raise ValueError('Patch check failed')
        subprocess.run(['git','apply',str(ROOT/'integration.patch')],cwd=work,env=env,check=True)
        for record in changes:
            if sha((work/record['path']).read_bytes()) != record['after']:
                raise ValueError('Applied patch differs from overlay')
        after = {p.relative_to(work).as_posix(): sha(p.read_bytes()) for p in work.rglob('*') if p.is_file()}
        expected = before | {r['path']:r['after'] for r in changes}
        if after != expected: raise ValueError('Unexpected patch effect')
        command = [sys.executable,'-B',str(work/'number_lexical_check.py'),'--lean',str(lean),'--out',str(out/'verification')]
        result = subprocess.run(command,cwd=work,env=env,capture_output=True,text=True)
        (out/'check.log').write_text(result.stdout+result.stderr)
        if result.returncode: raise ValueError('Standalone check failed; see check.log')
        subprocess.run(['git','apply','--reverse',str(ROOT/'integration.patch')],cwd=work,env=env,check=True)
        restored = {p.relative_to(work).as_posix(): sha(p.read_bytes()) for p in work.rglob('*') if p.is_file()}
        if restored != before: raise ValueError('Reverse patch does not restore source')
    for name, expected in inputs.items():
        if sha((ROOT/name).read_bytes()) != expected: raise ValueError('Input drift during replay')
    report = {'status':'pass','canonical_base':BASE,'patch_sha256':sha((ROOT/'integration.patch').read_bytes()),
        'exact_forward_reverse_patch':True,'standalone_cold_check':True,'source_inputs':inputs,
        'scratch_removed':not work.exists(),'verification_report_sha256':sha((out/'verification/report.json').read_bytes())}
    (out/'REPORT.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PASS: exact patch, independent scratch build/audit/runtime, full scratch removal')


if __name__ == '__main__':
    main()
