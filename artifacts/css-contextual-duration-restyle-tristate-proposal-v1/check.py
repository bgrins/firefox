import difflib
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sha = lambda body: hashlib.sha256(body).hexdigest()

def function(text, signature):
    start = text.index(signature)
    brace = text.index('{', start)
    depth, end = 1, brace + 1
    while depth:
        depth += (text[end] == '{') - (text[end] == '}')
        end += 1
    return text[start:end]

def main():
    bases, candidates = {}, {}
    for name in ('EffectCompositor.cpp', 'EffectCompositor.h'):
        bases[name] = (HERE / ('base-' + name)).read_text()
        candidates[name] = (HERE / ('candidate-' + name)).read_text()
    assert sha(bases['EffectCompositor.cpp'].encode()) == '6ec3a0ca45789b3089e8d2abcfb3ff37b881b0ee9084e09d0d396d73491249ed'
    assert sha(bases['EffectCompositor.h'].encode()) == '5ee054432f5105515def6f1eba9e2875226d6a59b6a0dc4d1e05b9617a12dc19'
    expected = ''.join(''.join(difflib.unified_diff(bases[n].splitlines(True), candidates[n].splitlines(True), fromfile='a/dom/animation/'+n, tofile='b/dom/animation/'+n)) for n in bases)
    assert (HERE / 'native.patch').read_text() == expected
    restored = candidates['EffectCompositor.cpp']
    for signature in ('void EffectCompositor::RequestRestyle(', 'void EffectCompositor::PostRestyleForAnimation(', 'void EffectCompositor::PostRestyleForThrottledAnimations()', 'bool EffectCompositor::PreTraverseInSubtree('):
        new = function(candidates['EffectCompositor.cpp'], signature)
        old = function(bases['EffectCompositor.cpp'], signature)
        assert new != old
        restored = restored.replace(new, old, 1)
    assert restored == bases['EffectCompositor.cpp']
    pre = function(candidates['EffectCompositor.cpp'], 'bool EffectCompositor::PreTraverseInSubtree(')
    old_pre = function(bases['EffectCompositor.cpp'], 'bool EffectCompositor::PreTraverseInSubtree(')
    assert pre.count('iter.Remove();') == old_pre.count('iter.Remove();') == 3
    assert pre.count('elementSet.Clear();') == old_pre.count('elementSet.Clear();') == 1
    assert 'aIter.Data() == RestyleState::Throttled' in pre
    forced = function(candidates['EffectCompositor.cpp'], 'void EffectCompositor::PostRestyleForThrottledAnimations()')
    assert 'iter.Data() != RestyleState::Throttled' in forced
    assert forced.index('iter.Data() = RestyleState::Pending') < forced.index('PostRestyleForAnimation(')
    post = function(candidates['EffectCompositor.cpp'], 'void EffectCompositor::PostRestyleForAnimation(')
    assert post.index('IsInStyleRefresh()') < post.index('entry.Data() = RestyleState::DispatchAttempted') < post.index('PresShell()->RestyleForAnimation(')
    assert post.count('ServoStyleSet::IsInServoTraversal()') == 1 and '|| mIsInPreTraverse' in post
    assert 'DURATION_RESTYLE_TRACE' not in candidates['EffectCompositor.cpp']
    with tempfile.TemporaryDirectory(prefix='duration-tristate-patch-') as directory:
        for name, body in bases.items():
            path = Path(directory) / 'dom/animation' / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(body)
        result = subprocess.run(['patch','-p1','--batch','--forward','-i',str(HERE/'native.patch')],cwd=directory,capture_output=True,text=True)
        assert result.returncode == 0, result.stdout+result.stderr
        for name, body in candidates.items():
            assert (Path(directory)/'dom/animation'/name).read_text() == body
    for name, pin in json.loads((HERE/'REFERENCES.json').read_text()).items():
        assert sha((ROOT/name).read_bytes()) == pin['sha256']
    return {'ok':True,'exact_base_and_patch_replay':True,'cpp_changes_confined_to_four_functions':True,'removal_and_clear_sites_preserved':True,'forced_throttled_selection_preserved':True,'diagnostic_logger_not_in_repair':True,'native_compiled':False,'browser_executed':False,'scratch_removed':True,'candidate_sha256':{n:sha(b.encode()) for n,b in candidates.items()}}

if __name__ == '__main__':
    print(json.dumps(main(),indent=2))
