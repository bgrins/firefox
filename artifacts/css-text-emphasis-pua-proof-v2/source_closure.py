import hashlib
import json
from extract import definition


CALLERS = {
    "candidate/layout/generic/nsTextFrame.cpp": [
        "void BuildTextRunsScanner::FlushFrames",
        "already_AddRefed<gfxTextRun> BuildTextRunsScanner::BuildTextRunForFrames",
        "gfx::ShapedTextFlags nsTextFrame::GetSpacingFlags",
        "bool nsTextFrame::PropertyProvider::GetSpacing(",
        "bool nsTextFrame::PropertyProvider::GetSpacingInternal",
        "static void ComputeTextEmphasisStyleString",
        "static already_AddRefed<gfxTextRun> GenerateTextRunForEmphasisMarks",
        "static nsRubyFrame* FindFurthestInlineRubyAncestor",
        "nsRect nsTextFrame::UpdateTextEmphasis",
        "void nsTextFrame::DrawEmphasisMarks",
        "void nsTextFrame::DrawTextRunAndDecorations",
        "void nsTextFrame::DrawText(Range",
        "OverflowAreas nsTextFrame::RecomputeOverflow",
    ],
    "sources/layout/style/nsStyleStruct.h": ["bool HasEffectiveTextEmphasis() const"],
    "sources/layout/style/nsStyleStruct.cpp": ["nsChangeHint nsStyleText::CalcDifference", "LogicalSide nsStyleText::TextEmphasisSide"],
    "sources/gfx/thebes/gfxTextRun.cpp": ["already_AddRefed<gfxTextRun> gfxFontGroup::MakeTextRun("],
}


def retain(root, output):
    output.mkdir(parents=True)
    records = []
    for path, markers in CALLERS.items():
        source = (root / path).read_text()
        for marker in markers:
            body = definition(source, marker)
            name = f"{len(records):02}.cpp.txt"
            (output / name).write_text(body + "\n")
            records.append({"source": path, "marker": marker, "body_sha256": hashlib.sha256(body.encode()).hexdigest(), "body_bytes": len(body.encode()), "retained": name, "status": "source-only external caller/provider; not compiled by native bridge"})
    (output / "INVENTORY.json").write_text(json.dumps(records, indent=2) + "\n")
    return records
