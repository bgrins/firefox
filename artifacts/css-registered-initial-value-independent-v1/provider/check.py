import argparse
import hashlib
import json
from pathlib import Path
import runpy
import shutil
import subprocess
import sys

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def unique(pairs):
    out = {}
    for key, value in pairs:
        assert key not in out, ('duplicate JSON key', key)
        out[key] = value
    return out

def read_json(path):
    return json.loads(path.read_text(), object_pairs_hook=unique)

def main():
    assert sys.flags.isolated and sys.flags.no_site, 'Run python3 -I -S check.py'
    root = Path(__file__).resolve().parent
    args = argparse.ArgumentParser()
    args.add_argument('--output', required=True, type=Path)
    options = args.parse_args()
    for p in root.rglob('*'):
        assert not p.is_symlink(), ('symlink', p)
    seal = read_json(root / 'FREEZE.json')
    assert digest(root / 'MANIFEST.json') == seal['manifest_sha256']
    manifest = read_json(root / 'MANIFEST.json')
    for rel, expected in manifest.items():
        p = Path(rel)
        assert not p.is_absolute() and '..' not in p.parts
        assert digest(root / p) == expected, rel
    actual = {str(p.relative_to(root)) for p in root.rglob('*') if p.is_file()}
    assert actual == set(manifest) | {'MANIFEST.json', 'FREEZE.json'}, 'roster mismatch'
    output = options.output.resolve()
    assert root not in output.parents and output != root
    assert not output.exists(), 'Output must be new'
    derive = runpy.run_path(str(root / 'derive.py'))
    prior = read_json(root / 'prior-audit/MANIFEST.json')
    assert digest(root / 'prior-audit/MANIFEST.json') == read_json(root / 'prior-audit/FREEZE.json')['manifest_sha256']
    for p in (root / 'prior-audit/source').rglob('*'):
        if p.is_file():
            assert digest(p) == prior[str(p.relative_to(root / 'prior-audit'))]
    for source, candidate, patch in [('source', 'candidate', 'native.patch'),
                                     ('prior-audit/source', 'prior-audit/candidate', 'prior-audit/native.patch')]:
        originals = {p: (root / source / p).read_text() for p in derive['FILES']}
        assert derive['patch'](originals) == (root / patch).read_text()
        for p, text in originals.items():
            assert derive['candidate'](p, text) == (root / candidate / p).read_text()
    ordinary = [json.loads(x) for x in (root / 'root-browser/ordinary-initial-raw.json').read_text().splitlines()]
    rows = [x for x in ordinary if x.get('action') == 'test_status']
    assert [x['status'] for x in rows] == ['PASS', 'FAIL', 'PASS', 'FAIL', 'FAIL', 'PASS']
    assert all('expected "96px" but got "1in"' in x['message'] for x in rows if x['status'] == 'FAIL')
    output.mkdir(parents=True)
    results = {'authenticated_inputs': len(manifest), 'ordinary_baseline': {'PASS': 3, 'FAIL': 3}, 'patches': []}
    for label, source, candidate, patch in [('current', 'source', 'candidate', 'native.patch'),
        ('pre70-audit', 'prior-audit/source', 'prior-audit/candidate', 'prior-audit/native.patch')]:
        work = output / label
        for p in derive['FILES']:
            target = work / p
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(root / source / p, target)
        for reverse in (False, True):
            command = ['/usr/bin/patch', '-t', '-p1', '-i', str(root / patch)]
            if reverse:
                command.append('-R')
            result = subprocess.run(command, cwd=work, capture_output=True, text=True)
            (output / (label + ('-reverse' if reverse else '-apply') + '.log')).write_text(result.stdout + result.stderr)
            assert result.returncode == 0
            expected = source if reverse else candidate
            assert all((work / p).read_bytes() == (root / expected / p).read_bytes() for p in derive['FILES'])
        results['patches'].append(label)
    html = (root / 'proposed/registered-initial-computed-value.html').read_text()
    js = html.split('<script>')[1].split('</script>')[0]
    (output / 'probe.js').write_text(js)
    node = shutil.which('node')
    assert node
    result = subprocess.run([node, '--check', str(output / 'probe.js')], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    results['javascript_syntax'] = 'PASS; six loop registrations inspected, no browser execution'
    (output / 'CHECK.json').write_text(json.dumps(results, indent=2) + '\n')
    print(json.dumps(results))

if __name__ == '__main__':
    main()
