#!/usr/bin/env python3
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parent

def extract(path, marker):
    source = path.read_text()
    start = source.index(marker)
    opening = source.index("{", start)
    depth = 1
    end = opening + 1
    while depth:
        depth += (source[end] == "{") - (source[end] == "}")
        end += 1
    return source[start:end]

def main():
    source = ROOT / "sources"
    chunks = []
    roles = []
    for filename, marker in [
        ("WritingModes.h", "  LogicalPoint(WritingMode aWritingMode, const nsPoint& aPoint,"),
        ("WritingModes.h", "  nsPoint GetPhysicalPoint(WritingMode aWritingMode,"),
        ("nsIFrameInlines.h", "nsPoint nsIFrame::GetNormalPosition("),
        ("nsIFrameInlines.h", "mozilla::LogicalPoint nsIFrame::GetLogicalNormalPosition("),
        ("ReflowInput.cpp", "void ReflowInput::ApplyRelativePositioning(nsIFrame* aFrame,\n                                           const nsMargin&"),
        ("ReflowInput.cpp", "void ReflowInput::ApplyRelativePositioning(\n    nsIFrame* aFrame, WritingMode"),
        ("nsContainerFrame.cpp", "void nsContainerFrame::FinishReflowChild(\n    nsIFrame* aKidFrame, nsPresContext* aPresContext,"),
    ]:
        text = extract(source / filename, marker)
        chunks.append(text)
        roles.append({"source": "sources/" + filename, "marker": marker,
                      "sha256": hashlib.sha256(text.encode()).hexdigest(), "bytes": len(text)})
    facade = (ROOT / "native-facade.cpp.in").read_text()
    for index, chunk in enumerate(chunks):
        facade = facade.replace("@@SOURCE" + str(index) + "@@", chunk)
    candidate = (ROOT / "candidate-nsContainerFrame.cpp").read_text()
    start = candidate.index("      const bool isRelative = frame->IsRelativelyPositioned();")
    end = candidate.index("      nsReflowStatus frameStatus;", start)
    selection = candidate[start:end]
    facade = facade.replace("@@SELECTION@@", selection)
    start = candidate.index("      FinishReflowChild(\n          frame, aPresContext, desiredSize")
    end = candidate.index(";", start) + 1
    finish = candidate[start:end]
    facade = facade.replace("@@FINISH@@", finish)
    roles += [{"source":"candidate-nsContainerFrame.cpp", "role":name,
               "sha256":hashlib.sha256(text.encode()).hexdigest(), "bytes":len(text)}
              for name, text in [("relative-guard-and-position", selection), ("finish-flags", finish)]]
    restyle = (source / "RestyleManager.cpp").read_text()
    start = restyle.index("        bool hasProperty;", restyle.index("static bool RecomputePosition("))
    end = restyle.index("nsPoint(newOffsets.left, newOffsets.top));", start) + len("nsPoint(newOffsets.left, newOffsets.top));")
    update = restyle[start:end]
    facade = facade.replace("@@UPDATE@@", update)
    roles.append({"source":"sources/RestyleManager.cpp", "role":"relative-continuation-cache-and-position",
                  "sha256":hashlib.sha256(update.encode()).hexdigest(), "bytes":len(update)})
    rect = extract(source / "WritingModes.h", "  nsRect GetPhysicalRect(WritingMode aWritingMode,")
    facade = facade.replace("@@RECT@@", rect)
    roles.append({"source":"sources/WritingModes.h", "role":"final-rect-end-before-subtraction",
                  "sha256":hashlib.sha256(rect.encode()).hexdigest(), "bytes":len(rect)})
    assert "@@" not in facade
    original = (source / "nsContainerFrame.cpp").read_text()
    old_selection = "      const LogicalPoint pos(wm, prevInFlow->IStart(wm, containerSize), 0);\n"
    assert original.count(old_selection) == 1
    start = original.index("      FinishReflowChild(frame, aPresContext, desiredSize, &reflowInput, wm, pos,")
    end = original.index(";", start) + 1
    old_finish = original[start:end]
    before = facade.replace(selection, old_selection).replace(finish, old_finish)
    assert before != facade and "const bool isRelative" not in before
    (ROOT / "native-before-generated.cpp").write_text(before)
    roles += [{"source":"sources/nsContainerFrame.cpp", "role":name,
               "sha256":hashlib.sha256(text.encode()).hexdigest(), "bytes":len(text)}
              for name, text in [("original-position",old_selection), ("original-finish-flags",old_finish)]]
    (ROOT / "native-generated.cpp").write_text(facade)
    (ROOT / "EXTRACTIONS.json").write_text(json.dumps(roles, indent=2) + "\n")

if __name__ == "__main__":
    main()
