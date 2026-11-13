import difflib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
GRID = "layout/generic/nsGridContainerFrame.cpp"
BLOCK = "layout/generic/nsBlockFrame.cpp"
PRIOR = HERE.parent / "css-grid-baseline-demand-provider-trace-plan-20261112-v1"
WORK = HERE.parent / "css-grid-baseline-measurement-work-trace-plan-20261112-v2"


def generate(stage):
    base = HERE / stage
    sources = {str(path.relative_to(base / "original")): path.read_text()
               for path in (base / "original").rglob("*") if path.is_file()}
    edits = []

    def replace(name, old, new):
        assert sources[name].count(old) == 1, (stage, name, old[:90], sources[name].count(old))
        sources[name] = sources[name].replace(old, new)
        edits.append(dict(file=name, old=old, new=new))

    replace(GRID, "#include <stdlib.h>  // for div()", "#include <stdlib.h>  // for div()\n#include <stdio.h>")
    replace(GRID, '#include "mozilla/dom/Grid.h"', '#include "mozilla/dom/Element.h"\n#include "mozilla/dom/Grid.h"')
    replace(GRID, "enum class MeasuringReflowRequest", (HERE / (stage + "-helper.cpp.txt")).read_text() + "enum class MeasuringReflowRequest")
    if stage == "provider":
        for edit in json.loads((HERE / "provider-edits.json").read_text()):
            replace(edit["file"], edit["old"], edit["new"])
        replace(GRID, "    Snapshot result;", '''    AutoRestore<const nsIFrame*> captureRestore(sGridSnapshotCapture);
    AutoRestore<uint64_t> captureIdRestore(sGridSnapshotCaptureId);
    static uint64_t captureCounter = 0;
    sGridSnapshotCapture = aFrame;
    sGridSnapshotCaptureId = ++captureCounter;
    Snapshot result;''')
        replace(GRID, "    result.mGeometry.mUsedMargin = aFrame->GetUsedMargin();", '''    result.mGeometry.mUsedMargin = aFrame->GetUsedMargin();
    GridSnapshotProviderTrace(
        aFrame, "capture-begin", aBSize, aContentBSize, int(aRequest),
        aFrame->HasAnyStateBits(NS_STATE_GRID_PRODUCED_BASELINES),
        !aFrame->IsSubtreeDirty(), aFrame->IsGridContainerFrame());''')
        prior = json.loads((PRIOR / "EDITS.json").read_text())
        for edit in prior:
            if edit["file"] != GRID:
                continue
            old, new = edit["old"], edit["new"]
            if "result.mBaseline = aFrame" in old or old.startswith("            BaselineExportContext::Other);\n        break;") or old.startswith("      case MeasuringReflowRequest::Grid") or old.startswith("                aRequest == MeasuringReflowRequest::Grid"):
                replace(GRID, old.replace("result.mBaseline", "baseline"), new.replace("result.mBaseline", "baseline"))
            elif old.startswith("    MeasuringReflowRequest aRequest =") or old.startswith("          request);\n\n      const auto frameSize") or old.startswith("nscoord nsGridContainerFrame::SynthesizeBaseline("):
                replace(GRID, old, new)
        replace(GRID, "      return *result;", '      GridSnapshotProviderTrace(aChild, "cache-hit", int(aRequest), 0, 0, 0, 0, 0);\n      return *result;')
        replace(GRID, "  const auto snapshot = GridItemCachedBAxisMeasurement::Capture(", '''  GridSnapshotProviderTrace(aChild, "post-finish", childStatus.IsFullyComplete(),
                            aAvailableSize.ISize(wm), aAvailableSize.BSize(wm),
                            childSize.ISize(wm), childSize.BSize(wm), int(aRequest));
  const auto snapshot = GridItemCachedBAxisMeasurement::Capture(''')
    else:
        prior = json.loads((WORK / "demand/EDITS.json").read_text())
        for edit in prior:
            if edit["file"] == BLOCK or edit["old"].startswith("    if (aFrame->IsSubtreeDirty())") or edit["old"].startswith("      const auto measurement"):
                replace(edit["file"], edit["old"], edit["new"])
        replace(GRID, "        return Some(Project(aRequest));", '''        GridWorkLog("demand-hit", int(aRequest), int(mRequest),
                    mHasGridBaselines, mHasBaseline);
        return Some(Project(aRequest));''')
        replace(GRID, "      return Nothing();\n    }\n  };", '''      GridWorkLog("demand-miss", int(aRequest), int(mRequest),
                  mHasGridBaselines, mHasBaseline);
      return Nothing();
    }
  };''')
        start = sources[GRID].index("static MeasuringReflowResult MeasuringReflow(")
        end = sources[GRID].index("\n}\n", start) + 3
        old = sources[GRID][start:end]
        new = old.replace('''  if (const auto* cachedMeasurement =
          aChild->GetProperty(GridItemCachedBAxisMeasurement::Prop());
      cachedMeasurement && cachedMeasurement->IsValidFor(aChild, aCBSize)) {''', '''  {
    const auto* cachedMeasurement =
        aChild->GetProperty(GridItemCachedBAxisMeasurement::Prop());
    if (!cachedMeasurement) {
      GridWorkLog("cache-absent");
    }
    if (cachedMeasurement && cachedMeasurement->IsValidFor(aChild, aCBSize)) {''')
        new = new.replace("\n  auto* parent =", '\n  }\n  GridWorkLog("measure-begin");\n  auto* parent =')
        new = new.replace("      return *result;", '      GridWorkLog("cache-hit");\n      return *result;')
        new = new.replace("  return result;", '  GridWorkLog("measure-end", result.mBSize, result.mContentBSize);\n  return result;')
        for suffix, anchor in [("update", "    cachedMeasurement->Update(aChild, aCBSize, snapshot);"),
                               ("create", "    aChild->SetProperty(GridItemCachedBAxisMeasurement::Prop(),\n                        cachedMeasurement);")]:
            assert new.count(anchor) == 1
            new = new.replace(anchor, anchor + f'\n    GridWorkLog("store-{suffix}", int(snapshot.mRequest),\n                snapshot.mHasBaseline, snapshot.mHasGridBaselines);')
        replace(GRID, old, new)
        replace(GRID, "    result.mGeometry.mUsedMargin = aFrame->GetUsedMargin();", '''    result.mGeometry.mUsedMargin = aFrame->GetUsedMargin();
    GridWorkLog("capture-begin", int(aRequest), aFrame->IsGridContainerFrame(),
                aFrame->HasAnyStateBits(NS_STATE_GRID_PRODUCED_BASELINES),
                aFrame->IsSubtreeDirty());''')
        for last, first, kind in [("NaturalLast", "NaturalFirst", 0), ("GridBlockLast", "GridBlockFirst", 1), ("GridInlineLast", "GridInlineFirst", 2)]:
            marker = f"      case MeasuringReflowRequest::{last}:\n"
            start = sources[GRID].index(marker)
            end = sources[GRID].index("        break;", start) + len("        break;")
            old = sources[GRID][start:end]
            new = old.replace(marker, marker.rstrip("\n") + " {\n" + f'''        GridWorkQuery workQuery(
            {kind}, int(aRequest == MeasuringReflowRequest::{first}
                       ? BaselineSharingGroup::First : BaselineSharingGroup::Last));
''') + "\n      }"
            replace(GRID, old, new)
        for statement, event in [("  RemoveStateBits(NS_STATE_GRID_PRODUCED_BASELINES);", "producer-reset"),
                                  ("  AddStateBits(NS_STATE_GRID_PRODUCED_BASELINES);", "producer-complete")]:
            replace(GRID, statement, statement + f'''
  if (sGridWorkCall && sGridWorkCall->mFrame == this) {{
    GridWorkLog("{event}", HasAnyStateBits(NS_STATE_GRID_PRODUCED_BASELINES));
  }}''')
    for axis, kind in [("Block", 1), ("Inline", 2)]:
        for group in ("First", "Last"):
            getter = "GetBBaseline" if axis == "Block" else "GetIBaseline"
            old = f'''        result.mBaselines[LogicalAxis::{axis}][BaselineSharingGroup::{group}] =
            grid->{getter}(BaselineSharingGroup::{group});'''
            if stage == "provider":
                new = f'''        GridSnapshotProviderTrace(aFrame, "grid-before", int(BaselineSharingGroup::{group}),
                                  int(LogicalAxis::{axis}), 0, 0, 0, 0);
''' + old + f'''
        GridSnapshotProviderTrace(aFrame, "grid-after", int(BaselineSharingGroup::{group}),
                                  result.mBaselines[LogicalAxis::{axis}][BaselineSharingGroup::{group}],
                                  int(LogicalAxis::{axis}), 0, 0, 0);'''
            else:
                new = f'''        {{
          GridWorkQuery workQuery({kind}, int(BaselineSharingGroup::{group}));
''' + old + "\n        }"
            replace(GRID, old, new)
    start = sources[GRID].index("  static Snapshot Capture(")
    end = sources[GRID].index("\n  void Update(", start)
    old = sources[GRID][start:end]
    event = ('GridSnapshotProviderTrace(aFrame, "capture-end", result.mHasGridBaselines,\n'
             '                              result.mHasBaseline, int(result.mRequest), 0, 0, 0);') if stage == "provider" else (
             'GridWorkLog("capture-end", int(result.mRequest), result.mHasBaseline,\n'
             '                result.mHasGridBaselines);')
    new = old.replace("        return result;", "        " + event + "\n        return result;")
    new = new.replace("    return result;\n  }", "    " + event + "\n    return result;\n  }")
    assert new.count('"capture-end"') == 2
    replace(GRID, old, new)
    patch = ""
    for name, text in sources.items():
        dest = base / "candidate" / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(text)
        patch += "".join(difflib.unified_diff((base / "original" / name).read_text().splitlines(True),
                        text.splitlines(True), fromfile="a/" + name, tofile="b/" + name))
    (base / "DIAGNOSTIC.patch").write_text(patch)
    (base / "EDITS.json").write_text(json.dumps(edits, indent=2) + "\n")
    print(stage, len(edits), "source-only diagnostic edits")


if __name__ == "__main__":
    generate("provider")
    generate("work")
