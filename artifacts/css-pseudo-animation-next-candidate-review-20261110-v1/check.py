import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = ROOT / 'artifacts/css-pseudo-animation-next-candidate-20261110-v1'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    pins = json.loads((SOURCE / 'SOURCES.json').read_text())
    for name, expected in pins['files'].items():
        data = (SOURCE / 'source' / name).read_bytes()
        assert sha(data) == expected
        original = subprocess.check_output(['git', '-C', str(ROOT), '-c', 'core.fsmonitor=false',
            'show', pins['revision'] + ':' + name])
        assert data == original
    candidates = {str(p.relative_to(SOURCE / 'candidate')): p.read_bytes()
                  for p in (SOURCE / 'candidate').rglob('*') if p.is_file()}
    assert set(candidates) == {'dom/animation/KeyframeEffect.h', 'dom/animation/KeyframeEffect.cpp'}
    cpp = 'dom/animation/KeyframeEffect.cpp'
    original = (SOURCE / 'source' / cpp).read_text()
    candidate = candidates[cpp].decode()
    old_start = original.index('nsTArray<AnimationProperty> KeyframeEffect::BuildProperties(')
    new_start = candidate.index('KeyframeEffect::PropertyInputSnapshot KeyframeEffect::CapturePropertyInputs()')
    end = 'template <typename FrameEnumFunc>'
    assert original[:old_start] == candidate[:new_start]
    assert original[original.index(end, old_start):] == candidate[candidate.index(end, new_start):]
    assert candidate.count('const bool hasComputedKeyframes = GetComputedKeyframes(computedKeyframes);') == 1
    header = candidates['dom/animation/KeyframeEffect.h'].decode()
    declaration_start = header.index('\n\n  // Owns array storage and references;')
    declaration_end = header.index('  bool ReferencesAttributes()', declaration_start)
    assert header[:declaration_start] + '\n' + header[declaration_end:] == (SOURCE / 'source/dom/animation/KeyframeEffect.h').read_text()
    capture = candidate[new_start:candidate.index('/* static */', new_start)]
    assert capture.index('mKeyframes.Clone()') < capture.index('GetComputedKeyframes(computedKeyframes)')
    assert capture.index('GetComputedKeyframes(computedKeyframes)') < capture.index('return {mTarget, mEffectOptions.mComposite')
    assert 'mKeyframes = std::move(inputs.mSpecifiedKeyframes);' in candidate
    with tempfile.TemporaryDirectory(prefix='patch-', dir=HERE) as directory:
        work = Path(directory)
        shutil.copytree(SOURCE / 'source', work, dirs_exist_ok=True)
        applied = subprocess.run(['git', 'apply', str(SOURCE / 'snapshot.patch')], cwd=work,
            capture_output=True, text=True)
        assert applied.returncode == 0, applied.stderr
        for name, original_hash in pins['files'].items():
            actual = (work / name).read_bytes()
            assert actual == candidates[name] if name in candidates else sha(actual) == original_hash
        reversed_patch = subprocess.run(['git', 'apply', '--reverse', str(SOURCE / 'snapshot.patch')],
            cwd=work, capture_output=True, text=True)
        assert reversed_patch.returncode == 0, reversed_patch.stderr
        assert all(sha((work / name).read_bytes()) == expected for name, expected in pins['files'].items())
    result = {'status': 'pass', 'source_revision': pins['revision'],
              'authenticated_git_objects': pins['files'],
              'snapshot_patch_sha256': sha((SOURCE / 'snapshot.patch').read_bytes()),
              'candidate_sha256': {p: sha(b) for p, b in candidates.items()},
              'other_KeyframeEffect_cpp_bytes_unchanged': True,
              'other_KeyframeEffect_header_bytes_unchanged': True,
              'virtual_completion_before_target_composite_capture': True,
              'patch_forward_reverse': True, 'temporary_files_removed': True,
              'native_build_or_execution': False}
    (HERE / 'CHECK.json').write_text(json.dumps(result, indent=2) + '\n')
    print('PASS: twelve Git-pinned sources; exact two-file patch; unchanged other implementation bytes; forward/reverse application')


if __name__ == '__main__':
    main()
