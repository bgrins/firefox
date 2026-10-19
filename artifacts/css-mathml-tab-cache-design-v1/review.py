import difflib
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def inspect():
    digest = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    receipt = json.loads((ROOT / "evidence/receipt.json").read_text())
    assert receipt["inputs_before"] == receipt["inputs_after"]
    imported = json.loads((ROOT / "IMPORT.json").read_text())
    assert digest(ROOT / "evidence/receipt.json") == imported["receipt_sha256"]
    for name, expected in receipt["inputs_before"].items():
        relative = name.split("/code/firefox/", 1)[1]
        if relative.startswith("objdir-"):
            continue
        assert digest(ROOT / "sources" / relative) == expected
    for entry in receipt["http"]:
        if entry["path"].endswith(("mathml-cache-origin.html", "Ahem.ttf")):
            assert entry["status"] == 200
            assert digest(ROOT / "sources" / entry["path"].lstrip("/")) == entry["sha256"]
    first, second = receipt["observed"]["first"], receipt["observed"]["second"]
    assert first == second
    assert first["fontLoaded"]
    rows = first["rows"]
    assert len(rows) == 12
    by_id = {row["id"]: row for row in rows}
    calibration = {}
    for kind in ["math", "html"]:
        c = by_id[kind + "-glyph-calibration"]
        calibration[kind] = c["samples"][0]["chars"][0]["width"]
        assert calibration[kind] == 20
    observations = []
    failures = []
    for row in rows:
        samples = row["samples"]
        assert len(samples) == 3
        assert all({k: v for k, v in s.items() if k != "pass"} ==
                   {k: v for k, v in samples[0].items() if k != "pass"} for s in samples)
        chars = samples[0]["chars"]
        observed = {"id": row["id"], "text": row["text"], "element_width": row["width"],
                    "whole_range_width": samples[0]["whole"]["width"],
                    "chars": [{"char": c["char"], "index": c["index"],
                               "relative_x": c["x"] - row["x"], "width": c["width"]} for c in chars]}
        observations.append(observed)
        for c in chars:
            if c["char"] in "AB":
                expected = calibration[row["id"].split("-", 1)[0]]
                if abs(c["width"] - expected) > 0.01:
                    failures.append({"id": row["id"], "char": c["char"], "index": c["index"],
                                     "observed": c["width"], "calibrated": expected})
    assert len(failures) == 4
    extractor = ROOT / "extract.py"
    assert digest(extractor) == "39995d1afa7bdbe60c61b9d07bf11434d6d67ed73d93c75fc15ad0ff39266c0a"
    spec = importlib.util.spec_from_file_location("extract", extractor)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    original = (ROOT / "sources/layout/generic/nsTextFrame.cpp").read_text()
    candidate = (ROOT / "proposal/nsTextFrame.cpp").read_text()
    marker = "nsTextFrame::TrimmedOffsets nsTextFrame::GetTrimmedOffsets("
    old = module.extract(original, marker)
    new = module.extract(candidate, marker)
    assert original.replace(old, new, 1) == candidate
    patch = ''.join(difflib.unified_diff(original.splitlines(True), candidate.splitlines(True),
                   fromfile="a/layout/generic/nsTextFrame.cpp", tofile="b/layout/generic/nsTextFrame.cpp"))
    assert patch == (ROOT / "proposal/leading-origin.patch").read_text()
    bindings = []
    targets = {
        "layout/generic/nsTextFrame.cpp": [marker,
            "void nsTextFrame::ReflowText(",
            "void nsTextFrame::PropertyProvider::InitializeForDisplay(",
            "void nsTextFrame::PropertyProvider::InitializeForMeasure(",
            "void nsTextFrame::PropertyProvider::CalcTabWidths(",
            "void nsTextFrame::TabWidthStore::ApplySpacing(",
            "void nsTextFrame::UpdateIteratorFromOffset(",
            "nsPoint nsTextFrame::GetPointFromIterator(",
            "nsresult nsTextFrame::GetPointFromOffset(",
            "nsTextFrame::TrimOutput nsTextFrame::TrimTrailingWhiteSpace("],
        "dom/base/AbstractRange.cpp": ["static void ExtractRectFromOffset(",
            "static void GetPartialTextRect(", "void AbstractRange::CollectClientRectsAndText("],
        "layout/mathml/nsMathMLTokenFrame.cpp": ["void nsMathMLTokenFrame::MarkTextFramesAsTokenMathML("],
        "gfx/thebes/gfxTextRun.cpp": ["uint32_t gfxTextRun::BreakAndMeasureText("],
    }
    for name, markers in targets.items():
        text = (ROOT / "sources" / name).read_text()
        for item in markers:
            body = module.extract(text, item)
            bindings.append({"file": name, "marker": item, "sha256": hashlib.sha256(body.encode()).hexdigest()})
    return {"stable_input_pins": len(receipt["inputs_before"]), "runs": 2, "samples_per_run": 3,
            "calibration": calibration, "glyph_width_failures": failures, "observations": observations,
            "source_bindings": bindings, "candidate_sha256": hashlib.sha256(candidate.encode()).hexdigest(),
            "candidate_status": "proposal only; not compiled or executed"}


if __name__ == "__main__":
    print(json.dumps(inspect(), indent=2))
