import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit("requires isolated, no-site, nonoptimized Python")
sys.dont_write_bytecode = True
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent

def digest(data):
    return hashlib.sha256(data).hexdigest()

def body(text, anchor):
    if text.count(anchor) != 1:
        raise ValueError((anchor, "nonunique anchor"))
    start = text.index(anchor)
    opening = text.index("{", start)
    depth, i = 0, opening
    while i < len(text):
        if text.startswith("//", i):
            i = text.index("\n", i) + 1
            continue
        if text.startswith("/*", i):
            i = text.index("*/", i + 2) + 2
            continue
        ch = text[i]
        if ch in "\"'":
            quote = ch
            i += 1
            while text[i] != quote:
                i += 2 if text[i] == "\\" else 1
            i += 1
            continue
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return text[start:i + 1]
        i += 1
    raise ValueError((anchor, "unclosed body"))

ROSTER = {
    "nsIContentInlines.h": ["inline void nsIContent::SetPrimaryFrame("],
    "nsIFrame.h": ["void SetIsPrimaryFrame(bool aIsPrimary)", "bool IsPrimaryFrame() const"],
    "nsIFrame.cpp": ["void nsIFrame::InitPrimaryFrame()", "void nsIFrame::HandlePrimaryFrameStyleChange(",
        "void nsIFrame::HandleLastRememberedSize()", "void nsIFrame::Destroy(DestroyContext& aContext)"],
    "nsPresContext.h": ["void SetNeedsToUpdateHiddenByContentVisibilityForAnimations()"],
    "Document.cpp": ["void Document::ObserveForLastRememberedSize(", "void Document::UnobserveForLastRememberedSize("],
    "Element.cpp": ["void Element::RemoveLastRememberedBSize()", "void Element::RemoveLastRememberedISize()"],
    "nsImageMap.cpp": ["void nsImageMap::AreaRemoved(", "void nsImageMap::FreeAreas()",
        "void nsImageMap::Destroy()", "void nsImageMap::AddArea("],
    "nsImageFrame.cpp": ["void nsImageFrame::DisconnectMap()", "void nsImageFrame::Destroy(DestroyContext& aContext)"],
    "nsSubDocumentFrame.cpp": ["void nsSubDocumentFrame::Init("],
    "nsCSSFrameConstructor.cpp": ["nsCSSFrameConstructor::FindDataByTag(",
        "nsCSSFrameConstructor::FindHTMLData(", "nsCSSFrameConstructor::FindElementTagData(",
        "nsCSSFrameConstructor::FindElementData(", "void nsCSSFrameConstructor::AddFrameConstructionItemsInternal(",
        "void nsCSSFrameConstructor::RemoveFloatingFirstLetterFrames(",
        "void nsCSSFrameConstructor::ConstructTextFrame("],
}

def collect():
    result = []
    for name, anchors in ROSTER.items():
        data = (ROOT / "source" / name).read_bytes()
        text = data.decode()
        for anchor in anchors:
            extracted = body(text, anchor)
            result.append({"source": "source/" + name, "source_sha256": digest(data),
                "anchor": anchor, "body": extracted, "body_sha256": digest(extracted.encode())})
    return result

if __name__ == "__main__":
    actual = collect()
    target = ROOT / "SOURCE-BINDINGS.json"
    if sys.argv[1:] == ["--write"]:
        target.write_text(json.dumps(actual, indent=2) + "\n")
    elif not sys.argv[1:]:
        if actual != json.loads(target.read_text()):
            raise SystemExit("source bindings changed")
        print(json.dumps({"bindings": len(actual), "status": "PASS"}))
    else:
        raise SystemExit("unsupported arguments")
