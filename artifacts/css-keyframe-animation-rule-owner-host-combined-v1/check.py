#!/usr/bin/env python3
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
OWNER = ROOT / 'artifacts/css-keyframe-animation-rule-owner-v2'
HOST = ROOT / 'artifacts/css-keyframe-animation-rule-host-followup-v1'
BASE = ROOT / 'artifacts/css-keyframe-animation-rule-combined-prototype-v1'
BULK = ROOT / 'artifacts/css-keyframe-animation-rule-bulk-host-proposal-v1'
SHARED = ['layout/style/test/gtest/rust/lib.rs', 'layout/style/test/gtest/TestAnimationOperationArena.cpp']

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    references = json.loads((HERE / 'REFERENCES.json').read_text())
    for name, expected in references.items():
        manifest = ROOT / name
        assert digest(manifest) == expected
        for relative, expected_payload in json.loads(manifest.read_text()).items():
            assert digest(manifest.parent / relative) == expected_payload
    paths = sorted(q.relative_to(HERE / 'candidate') for q in (HERE / 'candidate').rglob('*') if q.is_file())
    assert len(paths) == 17
    for path in paths:
        result = (HERE / 'candidate' / path).read_bytes()
        if str(path) in SHARED:
            original = (OWNER / 'original' / path).read_bytes()
            assert original == (HOST / 'original' / path).read_bytes() == (BASE / 'candidate' / path).read_bytes()
            left = (OWNER / 'candidate' / path).read_bytes()
            right = (HOST / 'candidate' / path).read_bytes()
            assert left.startswith(original) and right.startswith(original)
            assert result == left + right[len(original):]
        elif (OWNER / 'candidate' / path).exists():
            assert result == (OWNER / 'candidate' / path).read_bytes()
        else:
            assert str(path) == 'layout/style/test/gtest/rust/descriptor_bulk_cases.rs'
            assert result == (HOST / 'candidate' / path).read_bytes()
        original = HERE / 'original' / path
        if original.exists():
            assert original.read_bytes() == (OWNER / 'original' / path).read_bytes()
            base = BULK / 'candidate' / path
            if not base.exists():
                base = BASE / 'candidate' / path
            if base.exists():
                assert original.read_bytes() == base.read_bytes()
    assert not (HERE / 'candidate/layout/style/test/gtest/rust/differential_cases.rs').exists()
    cpp = (HERE / 'candidate' / SHARED[1]).read_text()
    names = ['.'.join(pair) for pair in re.findall(r'TEST\((\w+), (\w+)\)', cpp)]
    selection = json.loads((HERE / 'GTEST-SELECTION.json').read_text())
    assert len(names) == len(set(names)) == 15
    assert selection['names'] == names and selection['filter'] == ':'.join(names)
    assert names[:10] == ['.'.join(pair) for pair in re.findall(r'TEST\((\w+), (\w+)\)', (BASE / 'candidate' / SHARED[1]).read_text())]
    assert set(names[10:]) == {'AnimationRuleSample.OwnerIdentity', 'AnimationRuleSample.OwnerLifetime', 'AnimationRuleSample.OwnerLayout', 'KeyframeEndpoint.OwnedSourceAssociation', 'AnimationRuleSample.MetadataBulk'}
    assert selection['required_executed'] == selection['required_passed'] == 15
    assert selection['actual_executed'] is None and selection['actual_passed'] is None
    rust = (HERE / 'candidate' / SHARED[0]).read_text()
    for module in ['owner_cases', 'descriptor_bulk_cases']:
        assert rust.count('mod ' + module + ';') == 1
    commands = []
    with tempfile.TemporaryDirectory(prefix='animation-owner-host-') as directory:
        scratch = Path(directory)
        for path in paths:
            source = HERE / 'original' / path
            if source.exists():
                target = scratch / path
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source, target)
        patch = str(HERE / 'native.patch')
        for argv in [['git', 'apply', '--check', patch], ['git', 'apply', patch]]:
            result = subprocess.run(argv, cwd=scratch, capture_output=True, text=True)
            commands.append({'argv':argv,'exit_code':result.returncode,'stdout':result.stdout,'stderr':result.stderr})
            assert result.returncode == 0, result.stderr
        assert all((scratch / path).read_bytes() == (HERE / 'candidate' / path).read_bytes() for path in paths)
        result = subprocess.run(['git', 'apply', '-R', patch], cwd=scratch, capture_output=True, text=True)
        commands.append({'argv':['git','apply','-R',patch],'exit_code':result.returncode,'stdout':result.stdout,'stderr':result.stderr})
        assert result.returncode == 0, result.stderr
        for path in paths:
            source = HERE / 'original' / path
            assert (scratch / path).read_bytes() == source.read_bytes() if source.exists() else not (scratch / path).exists()
    print(json.dumps({'status':'OWNER_HOST_COMPOSITION_TRANSPORT_PASS','paths':17,'distinct_registered_tests':15,'shared_append_sites':2,'source_packages_authenticated':True,'original_ten_prefix_exact':True,'new_modules_exact':True,'both_append_sections_exact':True,'commands':commands,'scratch_removed':not scratch.exists(),'compiler_run':False,'tests_executed':0},indent=2))

if __name__ == '__main__':
    main()
