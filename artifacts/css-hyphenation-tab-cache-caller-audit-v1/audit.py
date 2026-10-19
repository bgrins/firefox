import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def load_extractor():
    path = ROOT / "extract.py"
    assert hashlib.sha256(path.read_bytes()).hexdigest() == "39995d1afa7bdbe60c61b9d07bf11434d6d67ed73d93c75fc15ad0ff39266c0a"
    spec = importlib.util.spec_from_file_location("bound_extract", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


TARGETS = {
    "layout/generic/nsTextFrame.cpp": [
        "nsTextFrame::TrimmedOffsets nsTextFrame::GetTrimmedOffsets(",
        "static uint32_t GetTrimmableWhitespaceCount(",
        "static bool IsTrimmableSpace(char aCh)",
        "static bool IsTrimmableSpace(const char16_t* aChars, uint32_t aLength)",
        "void nsTextFrame::SetLength(",
        "nsresult nsTextFrame::CharacterDataChanged(",
        "void nsTextFrame::ClearTextRun(",
        "static void InvalidateFrameDueToGlyphsChanged(",
        "static nsTextFrameUtils::CompressionMode GetCSSWhitespaceToCompressionMode(",
        "bool nsTextFrame::ShouldSuppressLineBreak() const",
        "nsTextFrame::TrimOutput nsTextFrame::TrimTrailingWhiteSpace(",
        "OverflowAreas nsTextFrame::RecomputeOverflow(",
    ],
    "layout/mathml/nsMathMLTokenFrame.cpp": [
        "void nsMathMLTokenFrame::MarkTextFramesAsTokenMathML()",
        "void nsMathMLTokenFrame::SetInitialChildList(",
        "void nsMathMLTokenFrame::AppendFrames(",
        "void nsMathMLTokenFrame::InsertFrames(",
    ],
    "layout/generic/nsInlineFrame.cpp": ["void nsInlineFrame::ReflowInlineFrame("],
    "layout/generic/nsLineLayout.cpp": ["void nsLineLayout::ReflowFrame("],
    "layout/style/nsStyleStruct.cpp": ["nsChangeHint nsStyleText::CalcDifference("],
    "layout/style/nsStyleStructInlines.h": ["bool nsStyleText::NewlineIsSignificant("],
    "layout/generic/nsTextFrameUtils.cpp": ["CharT* nsTextFrameUtils::TransformText("],
    "layout/base/FrameProperties.h": [
        "inline void FrameProperties::SetInternal(",
        "void RemoveAll(const nsIFrame* aFrame)",
    ],
    "dom/base/AbstractRange.cpp": [
        "void AbstractRange::CollectClientRectsAndText(",
        "already_AddRefed<DOMRect> AbstractRange::GetBoundingClientRect(",
        "already_AddRefed<DOMRectList> AbstractRange::GetClientRects(",
    ],
    "servo/components/style/style_adjuster.rs": ["fn should_suppress_linebreak<E>("],
}


def run():
    extractor = load_extractor()
    records = []
    for file, markers in TARGETS.items():
        source = (ROOT / "current-source" / file).read_text()
        for marker in markers:
            body = extractor.extract(source, marker)
            record = {"file": "current-source/" + file, "marker": marker,
                      "sha256": hashlib.sha256(body.encode()).hexdigest()}
            old = ROOT / "source" / Path(file).name
            if old.is_file():
                old_body = extractor.extract(old.read_text(), marker)
                record["historical_body_equal"] = old_body == body
                record["historical_sha256"] = hashlib.sha256(old_body.encode()).hexdigest()
            records.append(record)
    comparisons = []
    for name, file, marker in extractor.TARGETS:
        current = ROOT / "current-source/layout/generic" / file
        if not current.exists():
            continue
        old = extractor.extract((ROOT / "source" / file).read_text(), marker)
        new = extractor.extract(current.read_text(), marker)
        comparisons.append({"name": name, "baseline": "source/" + file,
                            "current": str(current.relative_to(ROOT)), "marker": marker,
                            "baseline_sha256": hashlib.sha256(old.encode()).hexdigest(),
                            "current_sha256": hashlib.sha256(new.encode()).hexdigest(),
                            "equal": old == new})
    assert comparisons == json.loads((ROOT / "BODY-COMPARISON.json").read_text())
    return records


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
