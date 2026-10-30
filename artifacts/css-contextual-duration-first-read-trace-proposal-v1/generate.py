import difflib
import hashlib
import json
import re
from pathlib import Path

OUT = Path(__file__).resolve().parent
PATHS = ['dom/animation/EffectCompositor.cpp', 'dom/animation/EffectCompositor.h',
         'layout/base/PresShell.h', 'layout/style/nsComputedDOMStyle.cpp']
sources = {p: (OUT / 'base' / p).read_text() for p in PATHS}
edits = []


def change(path, before, after):
    assert sources[path].count(before) == 1, (path, before[:160], sources[path].count(before))
    sources[path] = sources[path].replace(before, after, 1)
    edits.append({'path': path, 'before': before, 'after': after})


cpp, header, shell, computed = PATHS
change(cpp, '#include "EffectCompositor.h"\n', '#include "EffectCompositor.h"\n\n#include <algorithm>\n#include <cstdio>\n#include <cstdlib>\n#include "base/process_util.h"\n#include "mozilla/dom/Document.h"\n#include "nsGkAtoms.h"\n#include "nsIURI.h"\n')
change(cpp, 'namespace mozilla {\n', 'namespace mozilla {\n\n' + (OUT / 'trace-helper.inc').read_text() + '\n')
change(header, '#include "nsTArray.h"', '#include "nsTArray.h"\n#include "nsStringFwd.h"')
declarations = '''  struct DurationTraceQuery {
    uint64_t mId = 0;
    uint64_t mParent = 0;
    uint64_t mGrandparent = 0;
  };
  static DurationTraceQuery BeginDurationQuery(
      dom::Element*, const PseudoStyleRequest&, int aProperty);
  static void EndDurationQuery(DurationTraceQuery, dom::Element*,
                               const PseudoStyleRequest&, int aProperty,
                               const nsACString& aValue);
  static void TraceDurationSources(const char* aStage, dom::Element*,
                                    const PseudoStyleRequest&,
                                    const void* aStyleSource = nullptr,
                                    int aFlush = -1);
  void TraceDurationRestyle(const char* aStage, dom::Element*,
                            const PseudoStyleRequest&, int aCascade,
                            int aRequest = -1, dom::Element* aRoot = nullptr,
                            unsigned aFlags = 0);
  void TraceDurationSnapshot(dom::Element*, const PseudoStyleRequest&);

'''
change(header, '  explicit EffectCompositor(nsPresContext* aPresContext)', declarations + '  explicit EffectCompositor(nsPresContext* aPresContext)')
change(shell, '  MOZ_CAN_RUN_SCRIPT\n  void FlushPendingNotifications(FlushType aType) {', '  void TraceDurationFlush(const char* aStage, int aFlush, int aAnimations,\n                          int aNeed);\n\n  MOZ_CAN_RUN_SCRIPT\n  void FlushPendingNotifications(FlushType aType) {')
change(shell, '    if (!NeedFlush(aType, /* aFlushAnimations = */ true)) {', '    const bool durationNeedFlush = NeedFlush(aType, /* aFlushAnimations = */ true);\n    TraceDurationFlush("shell-gate-type", int(aType), 1, durationNeedFlush);\n    if (!durationNeedFlush) {')
change(shell, '    if (!NeedFlush(aType)) {', '    const bool durationNeedFlush = NeedFlush(aType);\n    TraceDurationFlush("shell-gate-changes", int(aType.mFlushType),\n                       aType.mFlushAnimations, durationNeedFlush);\n    if (!durationNeedFlush) {')
change(computed, '#include "mozilla/EffectSet.h"', '#include "mozilla/EffectSet.h"\n#include "mozilla/EffectCompositor.h"')
change(computed, '  MOZ_ASSERT(aReturn.IsEmpty());\n', '''  MOZ_ASSERT(aReturn.IsEmpty());
  const int durationTraceProperty = int(size_t(aPropId));
  const auto durationTraceQuery = EffectCompositor::BeginDurationQuery(
      mElement, mPseudo, durationTraceProperty);
  auto durationTraceReturn = MakeScopeExit([&] {
    EffectCompositor::EndDurationQuery(durationTraceQuery, mElement, mPseudo,
                                       durationTraceProperty, aReturn);
  });
''')
change(computed, 'void nsComputedDOMStyle::Flush(Document& aDocument, FlushType aFlushType) {', '''void nsComputedDOMStyle::Flush(Document& aDocument, FlushType aFlushType) {
  EffectCompositor::TraceDurationSources("flush-enter", mElement, mPseudo,
                                          nullptr, int(aFlushType));
  auto durationFlushExit = MakeScopeExit([&] {
    EffectCompositor::TraceDurationSources("flush-exit", mElement, mPseudo,
                                            nullptr, int(aFlushType));
  });''')
branch = json.loads((OUT.parent / 'css-contextual-duration-first-read-branch-join-v1/FUNCTIONS.json').read_text())
original = branch['void nsComputedDOMStyle::UpdateCurrentStyleSources(']['current_body']
modified = original.replace('  nsCOMPtr<Document> document(mDocumentWeak);', '''  const char* durationTraceExit = "sources-complete";
  EffectCompositor::TraceDurationSources("sources-enter", mElement, mPseudo);
  auto durationTraceSourcesExit = MakeScopeExit([&] {
    EffectCompositor::TraceDurationSources(durationTraceExit, mElement, mPseudo,
                                            mComputedStyle.get());
  });
  nsCOMPtr<Document> document(mDocumentWeak);''')
reasons = ['sources-no-document', 'sources-disconnected', 'sources-empty',
           'sources-no-shell', 'sources-cached', 'sources-unresolved']
assert modified.count('    return;') == len(reasons)
reason_iter = iter(reasons)
modified = re.sub(r'(?m)^([ \t]*)return;', lambda match: match[1] + f'durationTraceExit = "{next(reason_iter)}";\n' + match[1] + 'return;', modified)
modified = modified.replace('  if (NeedsToFlushStyle(aPropId)) {', '''  const bool durationNeedsStyle = NeedsToFlushStyle(aPropId);
  EffectCompositor::TraceDurationSources(
      durationNeedsStyle ? "style-needed" : "style-not-needed", mElement, mPseudo);
  if (durationNeedsStyle) {''')
change(computed, original, modified)

change(cpp, '  RestyleState previousState;\n', '  TraceDurationRestyle("request-before", aElement, aPseudoRequest,\n                       int(aCascadeLevel), int(aRestyleType));\n  RestyleState previousState;\n')
change(cpp, '  if (aRestyleType == RestyleType::Throttled) {\n', '  TraceDurationRestyle("request-state", aElement, aPseudoRequest,\n                       int(aCascadeLevel), int(aRestyleType));\n  if (aRestyleType == RestyleType::Throttled) {\n')
change(cpp, '  if (aRestyleType == RestyleType::Layer) {\n', '  TraceDurationRestyle("request-after", aElement, aPseudoRequest,\n                       int(aCascadeLevel), int(aRestyleType));\n  if (aRestyleType == RestyleType::Layer) {\n')
change(cpp, '  Element* element = aElement->GetPseudoElement(aPseudoRequest);\n', '  TraceDurationRestyle("post-enter", aElement, aPseudoRequest, int(aCascadeLevel));\n  Element* element = aElement->GetPseudoElement(aPseudoRequest);\n')
change(cpp, '  if (!element) {\n    return;\n  }\n\n  RestyleHint hint', '  if (!element) {\n    TraceDurationRestyle("post-no-element", aElement, aPseudoRequest, int(aCascadeLevel));\n    return;\n  }\n\n  RestyleHint hint')
change(cpp, '  if (ServoStyleSet::IsInServoTraversal() || mIsInPreTraverse) {\n', '  if (ServoStyleSet::IsInServoTraversal() || mIsInPreTraverse) {\n    TraceDurationRestyle("post-deferred-traversal", aElement, aPseudoRequest, int(aCascadeLevel));\n')
change(cpp, '  if (mPresContext->RestyleManager()->IsInStyleRefresh()) {\n', '  if (mPresContext->RestyleManager()->IsInStyleRefresh()) {\n    TraceDurationRestyle("post-deferred-refresh", aElement, aPseudoRequest, int(aCascadeLevel));\n')
change(cpp, '  mPresContext->PresShell()->RestyleForAnimation(element, hint);', '  TraceDurationRestyle("post-attempt", aElement, aPseudoRequest, int(aCascadeLevel));\n  mPresContext->PresShell()->RestyleForAnimation(element, hint);')
change(cpp, '      if (iter.Data() != RestyleState::Throttled) {\n', '      TraceDurationRestyle("forced-inspect", iter.Key().mElement,\n                           iter.Key().mPseudoRequest, int(cascadeLevel));\n      if (iter.Data() != RestyleState::Throttled) {\n')

pre_start = sources[cpp].index('bool EffectCompositor::PreTraverseInSubtree(')
pre_end = sources[cpp].index('\nvoid EffectCompositor::NoteElementForReducing(', pre_start)
pre = sources[cpp][pre_start:pre_end]
updated = pre.replace('const ElementsToRestyleIterType& aIter)', 'const ElementsToRestyleIterType& aIter, CascadeLevel aCascadeLevel)')
assert pre.count('getNeededRestyleTarget(iter)') == 2
updated = updated.replace('getNeededRestyleTarget(iter)', 'getNeededRestyleTarget(iter, cascadeLevel)')
for anchor, stage in [
    ('    if (!flushThrottledRestyles && aIter.Data() == RestyleState::Throttled) {', 'pre-skip-throttled'),
    ('    if (!nsContentUtils::GetPresShellForContent(target.mElement)) {', 'pre-skip-no-shell'),
    ('                     target.mElement, aRoot)) {', 'pre-skip-subtree'),
]:
    assert updated.count(anchor) == 1
    updated = updated.replace(anchor, anchor + f'\n      TraceDurationRestyle("{stage}", aIter.Key().mElement,\n                           aIter.Key().mPseudoRequest, int(aCascadeLevel), -1, aRoot, unsigned(aFlags));')
updated = updated.replace('    returnTarget = target;', '    TraceDurationRestyle("pre-selected", target.mElement, target.mPseudoRequest,\n                         int(aCascadeLevel), -1, aRoot, unsigned(aFlags));\n    returnTarget = target;')
for anchor, stage in [
    ('      if (target.mElement->GetComposedDoc() != mPresContext->Document()) {', 'pre-remove-wrong-document'),
    ('      if (!effects) {\n        // Drop EffectSets that have been destroyed.', 'pre-remove-no-effects'),
]:
    assert updated.count(anchor) == 1
    updated = updated.replace(anchor, anchor + f'\n        TraceDurationRestyle("{stage}", target.mElement,\n                             target.mPseudoRequest, int(cascadeLevel), -1, aRoot, unsigned(aFlags));')
for anchor, stage in [
    ('      mPresContext->RestyleManager()->PostRestyleEventForAnimations(', 'pre-post-hint'),
    ('        effect->GetAnimation()->WillComposeStyle();', 'pre-will-compose'),
    ('      iter.Remove();\n    }', 'pre-remove-consumed'),
]:
    assert updated.count(anchor) == 1
    indent = '        ' if 'WillComposeStyle' in anchor else '      '
    updated = updated.replace(anchor, indent + f'TraceDurationRestyle("{stage}", target.mElement,\n' + indent + '                     target.mPseudoRequest, int(cascadeLevel), -1, aRoot, unsigned(aFlags));\n' + anchor)
updated = updated.replace('      elementSet.Clear();', '''      if (DurationTraceEnabled() && !sDurationCapped) {
        for (auto iter = elementSet.ConstIter(); !iter.Done(); iter.Next()) {
          TraceDurationRestyle("pre-clear", iter.Key().mElement,
                               iter.Key().mPseudoRequest, int(cascadeLevel), -1,
                               aRoot, unsigned(aFlags));
        }
      }
      elementSet.Clear();''')
change(cpp, pre, updated)

patch = ''
for path in PATHS:
    target = OUT / 'candidate' / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(sources[path])
    patch += ''.join(difflib.unified_diff((OUT / 'base' / path).read_text().splitlines(True), sources[path].splitlines(True), fromfile='a/' + path, tofile='b/' + path))
(OUT / 'native.patch').write_text(patch)
(OUT / 'EDITS.json').write_text(json.dumps(edits, indent=2) + '\n')
roles = {p: {'base_sha256': hashlib.sha256((OUT / 'base' / p).read_bytes()).hexdigest(), 'candidate_sha256': hashlib.sha256((OUT / 'candidate' / p).read_bytes()).hexdigest()} for p in PATHS}
(OUT / 'SOURCE-ROLES.json').write_text(json.dumps(roles, indent=2, sort_keys=True) + '\n')
print('Prepared four diagnostic source roles; matching.rs remains c3b2ddf2 unchanged.')
