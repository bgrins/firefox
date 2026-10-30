import difflib
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent

def sha(body):
    return hashlib.sha256(body).hexdigest()

def erase(candidate):
    candidate = candidate.replace('\n#include <cstdio>\n#include <cstdlib>\n\n#include "base/process_util.h"\n', '', 1)
    start = candidate.index('static const char* DurationFeedbackTraceTarget(')
    end = candidate.index('NS_IMPL_CYCLE_COLLECTION_CLASS(EffectCompositor)', start)
    candidate = candidate[:start] + candidate[end:]
    candidate = candidate.replace('  const bool tracePresent = elementsToRestyle.Contains(key);\n', '', 1)
    candidate = re.sub(r'^ +DurationFeedbackTrace\([\s\S]*?;\n', '', candidate, flags=re.M)
    candidate = candidate.replace('      for (auto iter = elementSet.ConstIter(); !iter.Done(); iter.Next()) {\n      }\n', '', 1)
    return candidate

def main():
    base = (HERE / 'base-EffectCompositor.cpp').read_text()
    candidate = (HERE / 'candidate-EffectCompositor.cpp').read_text()
    assert erase(candidate) == base
    expected_ids = {f'duration-feedback-{kind}-{role}' for kind in ('coupled', 'zero-start') for role in ('passive', 'seek', 'outline', 'override', 'literal')}
    assert set(re.findall(r'id.EqualsLiteral\("([^"]+)"\)', candidate)) == expected_ids
    assert 'sequence >= 4096' in candidate and 'sequence == 4096' in candidate
    assert 'pid=%lu cap-exhausted limit=4096' in candidate
    assert 'if (!aElement || !NS_IsMainThread())' in candidate
    assert 'MOZ_DURATION_RESTYLE_TRACE' in candidate
    assert "value && value[0] == '1' && value[1] == '\\0'" in candidate
    assert 'DURATION_RESTYLE_TRACE pid=%lu seq=%u' in candidate
    expected_patch = ''.join(difflib.unified_diff(base.splitlines(True), candidate.splitlines(True), fromfile='a/dom/animation/EffectCompositor.cpp', tofile='b/dom/animation/EffectCompositor.cpp'))
    assert (HERE / 'native.patch').read_text() == expected_patch
    with tempfile.TemporaryDirectory(prefix='duration-trace-patch-') as temp:
        target = Path(temp) / 'dom/animation/EffectCompositor.cpp'
        target.parent.mkdir(parents=True)
        target.write_text(base)
        run = subprocess.run(['patch', '-p1', '--batch', '--forward', '-i', str(HERE / 'native.patch')], cwd=temp, capture_output=True, text=True)
        assert run.returncode == 0, run.stdout + run.stderr
        assert target.read_text() == candidate
    negatives = [candidate.replace('std::exchange(restyleEntry, true)', 'std::exchange(restyleEntry, false)'), candidate.replace('    return;\n  }\n\n  MOZ_ASSERT(!mPresContext', '  }\n\n  MOZ_ASSERT(!mPresContext', 1)]
    assert all(erase(body) != base for body in negatives)
    upstream = (HERE / 'upstream-EffectCompositor.cpp').read_text()
    def body(text, signature):
        start = text.index(signature); brace = text.index('{', start); depth = 1; end = brace + 1
        while depth:
            depth += (text[end] == '{') - (text[end] == '}'); end += 1
        return text[start:end]
    functions = ['void EffectCompositor::RequestRestyle(', 'void EffectCompositor::PostRestyleForAnimation(', 'bool EffectCompositor::PreTraverseInSubtree(']
    assert all(re.sub(r'\s+', '', body(base, name)) == re.sub(r'\s+', '', body(upstream, name)) for name in functions)
    print(json.dumps({'ok': True, 'diagnostic_erasure_exact_base': True, 'isolated_patch_replay': True, 'exact_ids': 10, 'behavior_change_negative_controls': 2, 'complete_upstream_function_matches': 3, 'compiled': False, 'base_sha256': sha(base.encode()), 'candidate_sha256': sha(candidate.encode())}, indent=2))

if __name__ == '__main__':
    main()
