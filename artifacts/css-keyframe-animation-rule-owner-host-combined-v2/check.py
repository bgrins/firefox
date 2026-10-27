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
OLD = ROOT / 'artifacts/css-keyframe-animation-rule-owner-host-combined-v1'
TRANSITION = ROOT / 'artifacts/css-keyframe-transition-endpoint-gtest-proposal-v1'
LIB = 'layout/style/test/gtest/rust/lib.rs'
CPP = 'layout/style/test/gtest/TestAnimationOperationArena.cpp'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    refs = json.loads((HERE / 'REFERENCES.json').read_text())
    for name, expected in refs.items():
        path = ROOT / name
        assert digest(path) == expected, name
        if path.name == 'FILES.json':
            for relative, value in json.loads(path.read_text()).items():
                assert digest(path.parent / relative) == value, relative
    pre = json.loads((HERE / 'PREIMAGES.json').read_text())
    post = json.loads((HERE / 'POSTIMAGES.json').read_text())
    assert set(pre) == set(post) and len(pre) == 17
    original_pre = json.loads((OLD / 'PREIMAGES.json').read_text())
    assert [name for name in pre if pre[name] != original_pre[name]] == [LIB]
    for name in pre:
        assert digest(HERE / 'candidate' / name) == post[name]
        old = HERE / 'original' / name
        assert digest(old) == pre[name] if pre[name] else not old.exists()
        body = (HERE / 'candidate' / name).read_bytes()
        previous = (OLD / 'candidate' / name).read_bytes()
        if name == LIB:
            prefix = (OLD / 'original' / name).read_bytes()
            current = (HERE / 'original' / name).read_bytes()
            assert current == prefix + b'\n#[cfg(feature = "gecko-gtest")]\nmod endpoint_transition_cases;\n'
            assert previous.startswith(prefix)
            assert body == current + previous[len(prefix):]
        else:
            assert body == previous
    guards = json.loads((HERE / 'PRESERVED-SOURCE-PINS.json').read_text())
    for name in ['dom/animation/KeyframeEffect.cpp',
                 'layout/style/test/gtest/TestKeyframePresentation.cpp',
                 'layout/style/test/gtest/rust/endpoint_transition_cases.rs']:
        assert name not in pre
        assert digest(TRANSITION / 'candidate' / name) == guards[name]
    corrected = (TRANSITION / 'candidate/dom/animation/KeyframeEffect.cpp').read_text()
    assert 'mProperties[0].mSegments[0].mFromEndpoint = nullptr;' in corrected
    cpp = (HERE / 'candidate' / CPP).read_text()
    names = ['.'.join(p) for p in re.findall(r'TEST\((\w+), (\w+)\)', cpp)]
    assert names == json.loads((OLD / 'GTEST-SELECTION.json').read_text())['names']
    presentation = (TRANSITION / 'candidate/layout/style/test/gtest/TestKeyframePresentation.cpp').read_text()
    names += ['.'.join(p) for p in re.findall(r'TEST_F\((\w+), (\w+)\)', presentation)]
    selection = json.loads((HERE / 'GTEST-SELECTION.json').read_text())
    assert len(names) == len(set(names)) == 17
    assert names == selection['names'] and ':'.join(names) == selection['filter']
    assert selection['required_executed'] == selection['required_passed'] == 17
    assert selection['actual_executed'] is None and selection['actual_passed'] is None
    rust = (HERE / 'candidate' / LIB).read_text()
    modules = re.findall(r'^mod (\w+);', rust, re.M)
    assert len(modules) == len(set(modules)) == 8
    assert {'owner_cases', 'descriptor_bulk_cases', 'endpoint_transition_cases'} <= set(modules)
    commands = []
    with tempfile.TemporaryDirectory(prefix='owner-host-v2-') as directory:
        scratch = Path(directory)
        for name, value in pre.items():
            if value:
                target = scratch / name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(HERE / 'original' / name, target)
        for flags in [['--check'], []]:
            args = ['git', 'apply', *flags, str(HERE / 'native.patch')]
            result = subprocess.run(args, cwd=scratch, capture_output=True, text=True)
            commands.append({'argv': args, 'exit': result.returncode, 'stderr': result.stderr})
            assert result.returncode == 0, result.stderr
        assert all(digest(scratch / name) == value for name, value in post.items())
        args = ['git', 'apply', '--reverse', str(HERE / 'native.patch')]
        result = subprocess.run(args, cwd=scratch, capture_output=True, text=True)
        commands.append({'argv': args, 'exit': result.returncode, 'stderr': result.stderr})
        assert result.returncode == 0, result.stderr
        for name, value in pre.items():
            assert digest(scratch / name) == value if value else not (scratch / name).exists()
    print(json.dumps({'status': 'OWNER_HOST_CURRENT_REBASE_SOURCE_PASS',
                      'paths': 17, 'unchanged_prior_postimages': 16,
                      'changed_preimages': [LIB], 'registered_tests': names,
                      'all_existing_modules_preserved': True,
                      'transition_fix_and_tests_untouched': True,
                      'commands': commands, 'scratch_removed': not scratch.exists(),
                      'compiled': False, 'tests_executed': 0}, indent=2))


if __name__ == '__main__':
    main()
