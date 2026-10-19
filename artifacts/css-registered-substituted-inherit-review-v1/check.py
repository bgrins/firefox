#!/usr/bin/env python3
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parent

def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    manifest = json.loads((ROOT / 'MANIFEST.json').read_text())
    for relative, expected in manifest.items():
        path = ROOT / relative
        assert not path.is_symlink() and path.is_file(), relative
        assert digest(path) == expected, relative
    assert not args.output.exists(), 'Output must be new'
    args.output.mkdir(parents=True)
    rows = [json.loads(x) for x in (ROOT / 'evidence/raw.json').read_text().splitlines()]
    statuses = [x for x in rows if x.get('action') == 'test_status']
    assert len(statuses) == 6
    expected = {f'{kind} with simultaneous reset-property change {padding}':
                ('FAIL' if kind == 'substituted' else 'PASS')
                for kind in ('direct', 'substituted', 'unset') for padding in ('false', 'true')}
    assert {x['subtest']: x['status'] for x in statuses} == expected
    assert len({x['subtest'] for x in statuses}) == len(statuses)
    for row in statuses:
        if row['status'] == 'FAIL':
            assert row['message'] == 'assert_equals: child after parent change expected "20px" but got "10px"'
    assert [x['status'] for x in rows if x.get('action') == 'test_end'] == ['OK']
    assert len([x for x in rows if x.get('action') == 'suite_end']) == 1
    run = json.loads((ROOT / 'evidence/RUN.json').read_text())
    assert run['stable_after'] and run['exit'] == 1
    rel = 'servo/components/style/custom_properties.rs'
    assert digest(ROOT / 'source' / rel) == run['pins'][rel]
    testrel = 'testing/web-platform/tests/css/css-properties-values-api/registered-substituted-inherit-restyle.html'
    assert digest(ROOT / 'evidence/probe.html') == run['pins'][testrel]
    assert digest(ROOT / 'evidence/final-test.html') == 'd87eaf487e9f41a98efd00a9c72cbe3f1ab6b813e4022b0d9ecb08afa541711f'
    original_test = (ROOT / 'evidence/probe.html').read_text().split('</script>')[-2]
    final_test = (ROOT / 'evidence/final-test.html').read_text().split('</script>')[-2]
    assert final_test.startswith(original_test)
    patch = ROOT / 'evidence/native.patch'
    assert digest(patch) == '14b9a124fcd9a670f3ee2968735395ed89c2f22212c709802f465ce60a346801'
    commands = []
    results = {}
    for kind, original in [('project', ROOT / 'source' / rel),
                           ('upstream', ROOT / 'evidence/upstream-custom_properties.rs')]:
        work = args.output / kind
        destination = work / rel
        destination.parent.mkdir(parents=True)
        shutil.copyfile(original, destination)
        for reverse in (False, True):
            command = ['/usr/bin/patch', '--batch', '--fuzz=0', '-p1', '-R' if reverse else '--forward', '-i', str(patch)]
            proc = subprocess.run(command, cwd=work, capture_output=True, text=True)
            commands.append({'command': command, 'cwd': str(work), 'returncode': proc.returncode,
                             'stdout': proc.stdout, 'stderr': proc.stderr})
            assert proc.returncode == 0, commands[-1]
            assert 'fuzz' not in proc.stdout.lower(), commands[-1]
            if not reverse:
                if kind == 'project':
                    assert destination.read_bytes() == (ROOT / 'candidate' / rel).read_bytes()
                results[kind] = {'original_sha256': digest(original), 'candidate_sha256': digest(destination)}
            else:
                assert destination.read_bytes() == original.read_bytes()
                results[kind]['exact_reverse'] = True
    (args.output / 'COMMANDS.json').write_text(json.dumps(commands, indent=2) + '\n')
    result = {'authenticated_inputs': len(manifest), 'baseline': {'FAIL': 2, 'PASS': 4, 'harness': 'OK'},
              'patch_checks': results, 'scope': 'Source patch and retained raw evidence only; no candidate execution.'}
    (args.output / 'RESULT.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()
