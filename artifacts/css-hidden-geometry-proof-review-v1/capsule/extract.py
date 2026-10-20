import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent

def unit(text, signature):
    if text.count(signature) != 1:
        raise ValueError('Nonunique signature: ' + signature)
    start = text.index(signature)
    brace = text.index('{', start)
    depth, mode, i = 0, 'code', brace
    while i < len(text):
        c, pair = text[i], text[i:i + 2]
        if mode == 'line':
            if c == '\n': mode = 'code'
        elif mode == 'block':
            if pair == '*/': mode, i = 'code', i + 1
        elif mode in ('"', "'"):
            if c == '\\': i += 1
            elif c == mode: mode = 'code'
        elif pair == '//': mode, i = 'line', i + 1
        elif pair == '/*': mode, i = 'block', i + 1
        elif c in ('"', "'"): mode = c
        elif c == '{': depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0:
                return text[start:i + 1] + (';' if text[i + 1:i + 2] == ';' else '')
        i += 1
    raise ValueError('Unclosed source unit')

ROLES = [
    ('output_wm_constructor', 'layout/generic/ReflowOutput.h', 'explicit ReflowOutput(WritingMode aWritingMode)'),
    ('output_input_constructor', 'layout/generic/ReflowOutput.cpp', 'ReflowOutput::ReflowOutput(const ReflowInput& aReflowInput)'),
    ('logical_size_zero_constructor', 'layout/generic/WritingModes.h', 'explicit LogicalSize(WritingMode aWritingMode)'),
    ('cache', 'HEAD-flex.cpp', 'class nsFlexContainerFrame::CachedBAxisMeasurement'),
    ('old_measure', 'HEAD-flex.cpp', 'const CachedBAxisMeasurement& nsFlexContainerFrame::MeasureBSizeForFlexItem'),
    ('new_measure', 'candidate-HEAD-flex.cpp', 'const CachedBAxisMeasurement& nsFlexContainerFrame::MeasureBSizeForFlexItem'),
    ('finish', 'layout/generic/nsContainerFrame.cpp', 'void nsContainerFrame::FinishReflowChild(\n    nsIFrame* aKidFrame, nsPresContext* aPresContext,\n    const ReflowOutput& aDesiredSize, const ReflowInput* aReflowInput,\n    const WritingMode& aWM,'),
    ('did_reflow', 'layout/generic/nsIFrame.cpp', 'void nsIFrame::DidReflow('),
    ('hides', 'layout/generic/nsIFrame.cpp', 'bool nsIFrame::HidesContentForLayout() const'),
    ('hidden_parent', 'layout/generic/nsIFrame.cpp', 'bool nsIFrame::IsHiddenByContentVisibilityOfInFlowParentForLayout() const'),
    ('update', 'layout/base/PresShell.cpp', 'void PresShell::UpdateHiddenContentInForcedLayout('),
    ('ensure', 'layout/base/PresShell.cpp', 'void PresShell::EnsureReflowIfFrameHasHiddenContent('),
    ('forcing', 'layout/base/PresShell.cpp', 'bool PresShell::IsForcingLayoutForHiddenContent('),
    ('flush', 'layout/base/PresShell.cpp', 'bool PresShell::ReflowForHiddenContentIfNeeded()'),
]

def extract():
    units, bindings = {}, []
    for name, source, signature in ROLES:
        path = ROOT / 'input' / source
        value = unit(path.read_text(), signature)
        units[name] = value
        bindings.append({'name': name, 'source': source, 'source_sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'signature': signature, 'unit_sha256': hashlib.sha256(value.encode()).hexdigest(), 'kind': 'complete-source-unit'})
    path = ROOT / 'input/layout/generic/nsBlockFrame.cpp'
    method = unit(path.read_text(), 'void nsBlockFrame::Reflow(')
    guard = unit(method, 'if (IsHiddenByContentVisibilityOfInFlowParentForLayout() &&')
    units['block_guard'] = guard
    bindings.append({'name': 'block_guard', 'source': 'layout/generic/nsBlockFrame.cpp', 'source_sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'unit_sha256': hashlib.sha256(guard.encode()).hexdigest(), 'kind': 'exact-leading-guard-only', 'admission': 'Remaining nsBlockFrame::Reflow is replaced by the explicit fixed-size/provider facade.'})
    return units, bindings

def generate(repair, mutant='none'):
    u, _ = extract()
    measure = u['new_measure' if repair else 'old_measure']
    cache = u['cache']
    finish, update, forcing = u['finish'], u['update'], u['forcing']
    if mutant == 'drop_dirty_mark':
        measure = measure.replace('aItem.Frame()->AddStateBits(NS_FRAME_IS_DIRTY);', '(void)0;')
    elif mutant == 'reuse_dirty':
        measure = measure.replace('!aItem.Frame()->IsSubtreeDirty() &&', 'true &&')
    elif mutant == 'omit_cb_key':
        cache = cache.replace('bool operator==(const Key& aOther) const = default;', 'bool operator==(const Key& aOther) const { return mComputedSize == aOther.mComputedSize && mBorderPadding == aOther.mBorderPadding && mComputedMinBSize == aOther.mComputedMinBSize && mComputedMaxBSize == aOther.mComputedMaxBSize && mAvailableBSize == aOther.mAvailableBSize; }')
    elif mutant == 'skip_publication':
        finish = finish.replace('aKidFrame->SetSize(aWM, convertedSize);', '(void)convertedSize;')
    elif mutant == 'force_clean_query':
        update = update.replace('!aFrame || !aFrame->IsSubtreeDirty()', '!aFrame')
    elif mutant == 'ignore_forced_set':
        forcing = forcing.replace('mHiddenContentInForcedLayout.Contains(aFrame->GetContent())', 'false')
    elif mutant != 'none':
        raise ValueError(mutant)
    parts = [(ROOT / 'facade-prefix.cpp').read_text(), cache,
             (ROOT / 'facade-cache.cpp').read_text(),
             'void nsIFrame::Reflow(nsPresContext*, ReflowOutput& aMetrics, const ReflowInput& aReflowInput) {\n' + u['block_guard'] + '\n aMetrics.size = Provider(aReflowInput);\n}\n',
             u['hides'], u['hidden_parent'], u['did_reflow'], finish,
             update, u['ensure'], forcing, u['flush'], measure,
             (ROOT / 'facade-main.cpp').read_text()]
    return '\n'.join(parts)

if __name__ == '__main__':
    print(json.dumps(extract()[1], indent=2, sort_keys=True))
