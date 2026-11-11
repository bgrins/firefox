import hashlib
import json
from pathlib import Path, PurePosixPath
import posixpath
import re
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CAP = ROOT / 'artifacts/css-pseudo-animation-snapshot-runtime-20261110-v1'


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def git(*args):
    return subprocess.check_output(['git', '-C', str(ROOT), '-c', 'core.fsmonitor=false', *args])


def main():
    manifest = json.loads((CAP / 'RUN-INPUTS.json').read_text())
    for name, expected in manifest.items():
        assert sha(CAP / name) == expected
    assert len(manifest) == 19
    origins = json.loads((CAP / 'WRAPPER-ORIGINS.json').read_text())
    for name, expected in origins['source_hashes'].items():
        assert sha(ROOT / origins['source_wrapper'] / name) == expected
    for name in origins['unchanged_helpers']:
        assert (CAP / name).read_bytes() == (ROOT / origins['source_wrapper'] / name).read_bytes()
    assert sha(CAP / 'snapshot.patch') == origins['native_patch_sha256']
    assert (CAP / 'snapshot.patch').read_bytes() == (ROOT / origins['native_candidate'] / 'snapshot.patch').read_bytes()
    plan = json.loads((CAP / 'RUN-PLAN.json').read_text())
    roles = json.loads((CAP / 'SOURCE-ROLES.json').read_text())
    for name, role in roles.items():
        assert hashlib.sha256(git('show', plan['head'] + ':' + name)).hexdigest() == role['base']
        assert sha(CAP / 'source' / name) == role['base']
        assert sha(CAP / 'candidate' / name) == role['candidate']
    changed = git('diff', '--name-only', plan['native_basis'], plan['head']).decode().splitlines()
    production_changes = [name for name in changed if not name.startswith('artifacts/')]
    assert not production_changes, production_changes
    pins = json.loads((CAP / 'runtime-inputs/test-source-pins.json').read_text())
    metadata, content = {}, {}
    for name, expected in pins.items():
        spec = plan['head'] + ':' + name
        if expected is None:
            result = subprocess.run(['git', '-C', str(ROOT), '-c', 'core.fsmonitor=false', 'cat-file', '-e', spec], capture_output=True)
            assert result.returncode != 0, name
        else:
            data = git('show', spec)
            assert hashlib.sha256(data).hexdigest() == expected
            content[name] = data.decode()
            if name.endswith('.ini'):
                metadata[name] = data.decode()
    pages = []
    for name in plan['suites']:
        if name in plan['fixtures']:
            text = (CAP / 'runtime-inputs' / plan['fixtures'][name]).read_text()
        else:
            text = content[name]
        scripts = []
        for src in re.findall(r'<script\b[^>]*\bsrc=[\'"]([^\'"]+)', text, re.I):
            path = src.split('?', 1)[0]
            if path.startswith('/'):
                resolved = 'testing/web-platform/tests' + path
            else:
                resolved = posixpath.normpath(str(PurePosixPath(name).parent / path))
            assert resolved in content, (name, resolved)
            scripts.append(resolved)
        assert not re.search(r'<meta\s+name=[\'"]variant[\'"]', text, re.I), name
        pages.append({'page': name, 'scripts': scripts, 'temporary_fixture': name in plan['fixtures']})
    assert len(pages) == 11 and sum(p['temporary_fixture'] for p in pages) == 2
    retained = json.loads((CAP / 'runtime-inputs/retained-build.json').read_text())
    assert sha(ROOT / retained['origin']) == retained['origin_sha256']
    receipt = json.loads((ROOT / retained['origin']).read_text())
    for name in ['head', 'repair_commit', 'source_sha256', 'mozconfig_sha256', 'binaries']:
        assert retained[name] == receipt[name], name
    assert retained['repair_commit'] == plan['native_basis']
    assert retained['mozconfig_sha256'] == plan['mozconfig_sha256']
    for name, expected in retained['source_sha256'].items():
        assert hashlib.sha256(git('show', plan['head'] + ':' + name)).hexdigest() == expected
    prep = json.loads((HERE / 'preparation-check.json').read_text())
    assert prep['status'] == 'PASS' and prep['parser_negative_controls'] == 20 and not prep['live_read_only_check']
    (HERE / 'CHECK.json').write_text(json.dumps({
        'status': 'pass', 'runtime_inputs_sha256': sha(CAP / 'RUN-INPUTS.json'),
        'frozen_inputs': manifest, 'source_head': plan['head'], 'source_basis': plan['native_basis'],
        'production_changes_since_repair_commit': production_changes,
        'metadata_and_script_pins': len(pins), 'metadata': metadata, 'pages': pages,
        'helper_origins_authenticated': origins, 'retained_receipt_sha256': retained['origin_sha256'],
        'preparation_controls': prep, 'live_binary_or_fixture_absence_checks': False,
        'builds_or_browser_tests_executed': False}, indent=2) + '\n')
    print('PASS: frozen inputs, helper origins, 11-page/direct-script metadata inventory, retained receipt and immutable Git source linkage')


if __name__ == '__main__':
    main()
