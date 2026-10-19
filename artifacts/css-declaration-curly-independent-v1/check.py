import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text())


def authenticate(root, manifest_hash=None, freeze_hash=None):
    if manifest_hash:
        assert sha(root / 'MANIFEST.json') == manifest_hash
    if freeze_hash:
        assert sha(root / 'FREEZE.json') == freeze_hash
    data = read(root / 'MANIFEST.json')
    pairs = [(r['path'], r['sha256']) for r in data] if isinstance(data, list) else list(data.items())
    paths = set()
    for name, digest in pairs:
        path = Path(name)
        assert not path.is_absolute() and '..' not in path.parts and name not in paths
        paths.add(name)
        target = root / path
        assert all(not p.is_symlink() for p in [target, *target.parents])
        assert target.is_file() and sha(target) == digest, name
    actual = {p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file()}
    assert actual == paths | {'MANIFEST.json', 'FREEZE.json'}, actual ^ paths
    return paths


def outcomes(path):
    rows = [json.loads(line) for line in path.read_text().splitlines()]
    result = {}
    for row in rows:
        if row.get('action') not in ('test_status', 'test_end'):
            continue
        key = (row['action'], row['test'], row.get('subtest'))
        assert key not in result
        result[key] = (row['status'], row.get('expected', row['status']))
    return result


def browser_check(root):
    phases = {}
    for phase in ('baseline', 'candidate'):
        value = read(root / f'{phase}-input.json')
        assert value == read(root / f'{phase}-before.json') == read(root / f'{phase}-after.json')
        result = read(root / f'{phase}-result.json')
        assert result['stable_pins']
        assert result['raw_sha256'] == sha(root / f'{phase}-raw.jsonl')
        assert result['console_sha256'] == sha(root / f'{phase}-console.log')
        phases[phase] = value
    old, new = phases['baseline'], phases['candidate']
    assert old['tests'] == new['tests'] and old['fixed'].keys() == new['fixed'].keys()
    assert [k for k in old['fixed'] if old['fixed'][k] != new['fixed'][k]] == ['servo/components/style/properties/mod.rs']
    for phase, source in [('baseline', 'original-properties.rs'), ('candidate', 'candidate-properties.rs')]:
        assert phases[phase]['fixed']['servo/components/style/properties/mod.rs'] == sha(root / source)
        assert phases[phase]['fixed']['testing/web-platform/tests/css/css-syntax/declaration-curly-fallback.html'] == sha(root / 'declaration-curly-fallback.html')
    assert old['binaries'] != new['binaries']
    assert read(root / 'candidate-build-input.json') == read(root / 'candidate-build-before.json')
    assert read(root / 'candidate-build-before.json')['fixed'] == new['fixed']
    assert read(root / 'candidate-build-after.json') == new
    for phase in read(root / 'candidate-build-result.json'):
        assert phase['exit_code'] == 0
        assert phase['log_sha256'] == sha(root / f"candidate-{'force-rust' if phase['phase'] == 'force-rust' else 'link'}.log")
    a, b = outcomes(root / 'baseline-raw.jsonl'), outcomes(root / 'candidate-raw.jsonl')
    assert a.keys() == b.keys() and len(a) == 94
    target = '/css/css-syntax/declaration-curly-fallback.html'
    values = ['serif {var(--x)}', 'serif, {var(--x)}', '{var(--x)} serif', 'serif {} var(--x)', 'serif {env(x)}', 'serif {attr(x)}']
    expected = {('test_status', target, f'{api}: font-family: {value}') for value in values for api in ('setProperty', 'cssText', 'stylesheet', 'supports')}
    changed = {k for k in a if a[k] != b[k]}
    assert changed == expected
    assert all(a[k] == ('FAIL', 'PASS') and b[k] == ('PASS', 'PASS') for k in expected)
    assert sum(k[0] == 'test_status' for k in b) == 89
    assert sum(k[0] == 'test_status' and k[1] == target for k in b) == 48
    assert all(v == (('PASS', 'PASS') if k[0] == 'test_status' else ('OK', 'OK')) for k, v in b.items())
    return {'keys': len(a), 'improvements': len(changed), 'unchanged': len(a) - len(changed), 'subtests': 89, 'harnesses': 5}


def native_check(path):
    result = read(path)
    valid = {'{var(--x)}', 'var(--x)', 'serif [var(--x)]', 'serif f({var(--x)})', 'serif'}
    variants = {}
    for variant in ('original', 'candidate'):
        rows = result[variant]['rows']
        assert len(rows) == 26
        keyed = {(r['mode'], r['value']): r for r in rows}
        assert len(keyed) == 26
        for row in rows:
            assert row['curly_rule'] == (row['value'] in valid)
        variants[variant] = keyed
    a, b = variants['original'], variants['candidate']
    assert a.keys() == b.keys()
    changed = [k for k in a if a[k] != b[k]]
    assert len(changed) == 7
    for k in changed:
        assert k[0] == 'comma' and not a[k]['curly_rule']
        assert a[k]['gateway'] and a[k]['result']
        assert not b[k]['gateway'] and not b[k]['result']
    assert not any(r['gateway'] and not r['curly_rule'] for r in b.values())
    return {'rows_per_variant': 26, 'changed': 7, 'candidate_forbidden_gateways': 0}


def main():
    assert sys.flags.isolated and sys.flags.no_site
    ap = argparse.ArgumentParser()
    ap.add_argument('--artifacts', type=Path, default=ROOT.parent)
    ap.add_argument('--replay', type=Path)
    args = ap.parse_args()
    own = authenticate(ROOT)
    static = args.artifacts / 'css-declaration-reparse-static-v1'
    browser = args.artifacts / 'css-declaration-curly-final-browser-v1'
    source_files = authenticate(static, 'be11ba093332bb80969efac104d8c61113d02f25592395e82deda65c30cf8299', 'bb69319b1e6c4917c3c747439ac0ee30602f3d9f434dcc8309d57cc171b9eedd')
    browser_files = authenticate(browser, 'fb7ad93158892a1163537020d224d3a830a1fd66f8c668c6a3570fe32c6cb2b4', '7d506ad6b395eeccc090646d760d14feee43878592a3b5a0f05345ab171707d1')
    assert sha(static / 'check.py') == '63558c27ad2e92448bcc6cd279e0938939deaf707abff7c6e84a8c26a1ca8e91'
    old = (browser / 'original-properties.rs').read_text()
    new = (browser / 'candidate-properties.rs').read_text()
    before = '    // Look for var(), env() and top-level curly blocks after the error.'
    after = '    input.reset(start);\n\n    // Look for var(), env() and top-level curly blocks in the whole value.'
    assert old.count(before) == 1 and old.replace(before, after) == new
    assert old == (static / 'evidence/source/servo/components/style/properties/mod.rs').read_text()
    patch = (ROOT / 'evidence/native-wpt.patch').read_text()
    assert sha(ROOT / 'evidence/native-wpt.patch') == '94e0730424570c206d35f9f35017407e8171c886f0453f1aa77b8377aafbb4ec'
    assert patch.count('--- ') == 2 and patch.count('+++ ') == 2
    added = patch.split('@@ -0,0 +1,52 @@\n')[1]
    assert ''.join(line[1:] for line in added.splitlines(keepends=True) if line.startswith('+')) == (browser / 'declaration-curly-fallback.html').read_text()
    report = {'authenticated_static': len(source_files), 'authenticated_browser': len(browser_files), 'authenticated_review': len(own), 'browser': browser_check(browser), 'native': native_check(ROOT / 'evidence/replay-RESULT.json'), 'source_delta': 'exact reset plus comment'}
    if args.replay:
        output = args.replay.resolve()
        assert not output.exists() and not output.is_relative_to(ROOT) and not output.is_relative_to(static)
        output.mkdir(parents=True)
        capsule = output / 'capsule'
        for name in sorted(source_files | {'MANIFEST.json', 'FREEZE.json'}):
            dest = capsule / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(static / name, dest)
        with (output / 'replay.log').open('w') as log:
            subprocess.run([sys.executable, '-I', '-S', str(capsule / 'check.py'), '--output', str(output / 'native')], cwd=output, stdout=log, stderr=subprocess.STDOUT, check=True)
        report['fresh_native'] = native_check(output / 'native/RESULT.json')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
