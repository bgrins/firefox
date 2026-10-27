from pathlib import Path
import subprocess, hashlib, json, difflib
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
HEAD = '90e7c8a3c46c5e84ec0bfffc239e52ea72b2085e'
paths = ['dom/base/FlushType.h', 'dom/base/Document.cpp', 'dom/svg/SVGLength.h', 'dom/svg/SVGLength.cpp', 'dom/svg/DOMSVGLength.cpp']
def replace(s, old, new):
    assert s.count(old) == 1, old
    return s.replace(old, new)
def edit(path, s, standalone):
    if path == 'dom/base/FlushType.h':
        return replace(s, '  bool mUpdateRelevancy;\n', '  bool mUpdateRelevancy;\n  bool mFlushHiddenEmbeddingFrames = false;\n')
    if path == 'dom/base/Document.cpp':
        s = replace(s, '''  if (StyleOrLayoutObservablyDependsOnParentDocumentLayout() &&
      mParentDocument->MayStartLayout() && IsSafeToFlush()) {
    ChangesToFlush parentFlush = aFlush;''', '''  auto canFlushParent = [this] {
    return StyleOrLayoutObservablyDependsOnParentDocumentLayout() &&
           mParentDocument->MayStartLayout() && IsSafeToFlush();
  };
  if (canFlushParent()) {
    RefPtr<Document> parentDocument = mParentDocument;
    ChangesToFlush parentFlush = aFlush;''')
        return replace(s, '''    mParentDocument->FlushPendingNotifications(parentFlush);
  }

  if (RefPtr<PresShell> presShell = GetPresShell()) {''', '''    parentDocument->FlushPendingNotifications(parentFlush);
    if (aFlush.mFlushHiddenEmbeddingFrames &&
        mParentDocument == parentDocument && canFlushParent()) {
      RefPtr<Element> embedder = GetEmbedderElement();
      if (embedder && embedder->GetComposedDoc() == parentDocument) {
        embedder->GetPrimaryFrame(FlushType::Layout);
      }
    }
  }

  if (RefPtr<PresShell> presShell = GetPresShell()) {''')
    if path == 'dom/svg/SVGLength.h':
        return replace(s, '  static bool IsFontRelativeUnit(uint16_t aUnit);', '  static bool IsFontRelativeUnit(uint16_t aUnit);\n\n  static bool IsViewportRelativeUnit(uint16_t aUnit);')
    if path == 'dom/svg/SVGLength.cpp':
        marker = 'void SVGLength::GetValueAsString(nsAString& aValue) const {'
        return replace(s, marker, '''bool SVGLength::IsViewportRelativeUnit(uint16_t aUnit) {
  return aUnit >= SVG_LENGTHTYPE_VW && aUnit <= SVG_LENGTHTYPE_VMAX;
}

''' + marker)
    if standalone:
        s = replace(s, '''    } else if (SVGLength::IsFontRelativeUnit(aUnitType)) {
      flushType = FlushType::Style;''', '''    } else if (SVGLength::IsFontRelativeUnit(aUnitType) ||
               SVGLength::IsViewportRelativeUnit(aUnitType)) {
      flushType = FlushType::Style;''')
        pos = s.index('void DOMSVGLength::ConvertToSpecifiedUnits(')
        before, after = s[:pos], s[pos:]
        after = replace(after, '''  if (!SVGLength::IsValidUnitType(aUnit)) {
    aRv.ThrowNotSupportedError("Unknown unit type");
    return;
  }

  if (nsCOMPtr<SVGElement> svg = do_QueryInterface(mOwner)) {''', '''  if (!SVGLength::IsValidUnitType(aUnit)) {
    aRv.ThrowNotSupportedError("Unknown unit type");
    return;
  }

  if (SVGLength::IsViewportRelativeUnit(ToSVGLength().GetUnit())) {
    FlushIfNeeded();
  }

  if (nsCOMPtr<SVGElement> svg = do_QueryInterface(mOwner)) {''')
        s = before + after
    return replace(s, '''      currentDoc->FlushPendingNotifications(flushType);''', '''      ChangesToFlush flush(flushType, flushType >= FlushType::Style,
                           flushType >= FlushType::Layout);
      flush.mFlushHiddenEmbeddingFrames =
          SVGLength::IsViewportRelativeUnit(aUnitType);
      currentDoc->FlushPendingNotifications(flush);''')
sha = lambda s: hashlib.sha256(s.encode()).hexdigest()
metadata = {}; patches = {'standalone': [], 'installed-overlay': []}
for path in paths:
    head = subprocess.check_output(['git', '-c', 'core.fsmonitor=false', 'show', HEAD + ':' + path], cwd=ROOT, text=True)
    installed = (ROOT / path).read_text()
    candidate, overlay = edit(path, head, True), edit(path, installed, False)
    for kind, original, result in [('standalone', head, candidate), ('installed-overlay', installed, overlay)]:
        patches[kind].extend(difflib.unified_diff(original.splitlines(True), result.splitlines(True), fromfile='a/' + path, tofile='b/' + path))
    for dirname, body in [('baseline', head), ('candidate', candidate), ('installed-candidate', overlay)]:
        p = HERE / dirname / path; p.parent.mkdir(parents=True, exist_ok=True); p.write_text(body)
    metadata[path] = {'head_sha256': sha(head), 'installed_sha256': sha(installed), 'candidate_sha256': sha(candidate), 'installed_candidate_sha256': sha(overlay)}
for kind, chunks in patches.items():
    (HERE / (kind + '.patch')).write_text(''.join(chunks))
(HERE / 'SOURCE-PINS.json').write_text(json.dumps(metadata, indent=2) + '\n')
print(json.dumps(metadata, indent=2))
