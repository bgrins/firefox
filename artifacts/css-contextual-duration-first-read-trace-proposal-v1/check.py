import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

OUT = Path(__file__).resolve().parent
sha = lambda data: hashlib.sha256(data).hexdigest()


def erase(sources, edits):
    result = dict(sources)
    for edit in reversed(edits):
        path = edit['path']
        assert result[path].count(edit['after']) == 1, path
        result[path] = result[path].replace(edit['after'], edit['before'], 1)
    return result


def main():
    roles = json.loads((OUT / 'SOURCE-ROLES.json').read_text())
    edits = json.loads((OUT / 'EDITS.json').read_text())
    base = {path: (OUT / 'base' / path).read_text() for path in roles}
    candidate = {path: (OUT / 'candidate' / path).read_text() for path in roles}
    for path, role in roles.items():
        assert sha(base[path].encode()) == role['base_sha256']
        assert sha(candidate[path].encode()) == role['candidate_sha256']
    assert erase(candidate, edits) == base
    with tempfile.TemporaryDirectory(prefix='duration-first-read-erasure-') as temporary:
        work = Path(temporary)
        for path in roles:
            target = work / path
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(OUT / 'base' / path, target)
        result = subprocess.run(['patch', '-p1', '--batch', '--forward', '-i', str(OUT / 'native.patch')], cwd=work, capture_output=True, text=True)
        assert result.returncode == 0, (result.stdout, result.stderr)
        assert {path: (work / path).read_text() for path in roles} == candidate
        reverse = subprocess.run(['patch', '-p1', '--batch', '-R', '-i', str(OUT / 'native.patch')], cwd=work, capture_output=True, text=True)
        assert reverse.returncode == 0, (reverse.stdout, reverse.stderr)
        assert {path: (work / path).read_text() for path in roles} == base
    cpp = 'dom/animation/EffectCompositor.cpp'
    for before, after in [('previousState != RestyleState::DispatchAttempted', 'previousState != RestyleState::Pending'),
                          ('iter.Data() != RestyleState::Throttled', 'iter.Data() == RestyleState::Throttled')]:
        tampered = dict(candidate)
        assert before in tampered[cpp]
        tampered[cpp] = tampered[cpp].replace(before, after, 1)
        try:
            assert erase(tampered, edits) == base
        except AssertionError:
            pass
        else:
            raise AssertionError('semantic mutation escaped erasure check')
    shell = 'layout/base/PresShell.h'
    for call in ['NeedFlush(aType, /* aFlushAnimations = */ true)', 'NeedFlush(aType)']:
        assert base[shell].count(call) == candidate[shell].count(call) == 1
    assert candidate[shell].count('DoFlushPendingNotifications(aType);\n  }') == 2
    assert 'RefPtr<PresShell>' not in (OUT / 'trace-helper.inc').read_text()
    assert 'nsCOMPtr<Document>' not in (OUT / 'trace-helper.inc').read_text()
    result = {'artifact_patch_apply_and_reverse': True, 'exact_erasure_to_semantic_bases': True,
              'semantic_mutation_negatives': 2, 'source_roles': roles,
              'one_original_needflush_evaluation_per_wrapper': True,
              'pres_shell_post_call_logging': False, 'added_lifetime_extension': False,
              'scratch_removed': not Path(temporary).exists(), 'native_compile_performed': False,
              'browser_performed': False}
    if '--write' in sys.argv:
        (OUT / 'ERASURE-CHECK.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    else:
        assert result == json.loads((OUT / 'ERASURE-CHECK.json').read_text())
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
