import argparse
import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check-live', action='store_true')
    args = parser.parse_args()
    manifest = json.loads((HERE/'RUN-INPUTS.json').read_text())
    for name, digest in manifest.items():
        assert sha(HERE/name) == digest, name
    for path in HERE.glob('*.py'):
        ast.parse(path.read_text(), filename=str(path))
    origin=json.loads((HERE/'WRAPPER-ORIGINS.json').read_text())
    for name in origin['unchanged_copied_helpers']:
        assert sha(HERE/name) == origin['inputs'][name], name
    assert sha(HERE/'native.patch') == origin['native_candidate_sha256']
    spec=importlib.util.spec_from_file_location('parser_controls', HERE/'parser-controls.py')
    controls=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(controls)
    result=controls.main()
    assert result == json.loads((HERE/'PARSER-CONTROLS.json').read_text())
    plan=json.loads((HERE/'RUN-PLAN.json').read_text())
    roles=json.loads((HERE/'SOURCE-ROLES.json').read_text())
    for name, role in roles.items():
        assert sha(HERE/'source'/name) == role['base']
        assert sha(HERE/'candidate'/name) == role['candidate']
    if args.check_live:
        assert subprocess.check_output(['git','-c','core.fsmonitor=false','rev-parse','HEAD'],cwd=ROOT,text=True).strip() == plan['head']
        assert sha(ROOT/'mozconfig') == plan['mozconfig_sha256']
        for name, role in roles.items():
            assert sha(ROOT/name) == role['base'], name
        for name, digest in json.loads((HERE/'runtime-inputs/test-source-pins.json').read_text()).items():
            assert sha(ROOT/name) == digest, name
        for name,digest in json.loads((HERE/'runtime-inputs/retained-build.json').read_text())['binaries'].items():
            assert sha(ROOT/name) == digest, name
        for name in plan['fixtures']:
            path=ROOT/name
            meta=ROOT/(name.replace('/tests/','/meta/',1)+'.ini')
            assert not path.exists() and not path.is_symlink()
            assert not meta.exists() and not meta.is_symlink()
    print(json.dumps({'status':'PASS','frozen_inputs':len(manifest),
                      'live_read_only_check':args.check_live,
                      'parser_rejection_controls':len(result['rejected_controls']),
                      'builds_or_browser_tests_executed':False},indent=2))


if __name__ == '__main__':
    main()
