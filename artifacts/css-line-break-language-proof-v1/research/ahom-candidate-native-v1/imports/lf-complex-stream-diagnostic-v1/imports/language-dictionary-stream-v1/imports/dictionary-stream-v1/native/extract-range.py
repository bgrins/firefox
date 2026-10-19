import json
import runpy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
helper = runpy.run_path(str(ROOT / "native/extract-full.py"))
full = helper["full"]
OUT = ROOT / "development-build/full"

for flavor in ["original", "candidate", "standalone"]:
    complete = helper["generate"](flavor).read_text()
    runner = (ROOT / "native/full-runner.cpp").read_text()
    assert complete.endswith(runner)
    complete = complete[:-len(runner)]
    source = ROOT / f"source/{flavor}/layout/generic/nsTextFrame.cpp"
    mapped = full(source, "struct MappedFlow {", True)
    structure = "class BuildTextRunsScanner { public:\n" + mapped + "\n" + (ROOT / "native/scanner-members.hpp").read_text() + "\n};\n"
    functions = "\n".join(full(source, name) for name in [
        "void BuildTextRunsScanner::AccumulateRunInfo(",
        "static bool HasCompressedLeadingWhitespace(",
        "void BuildTextRunsScanner::SetupBreakSinksForTextRun(",
        "void BuildTextRunsScanner::FlushLineBreaks(",
    ])
    (OUT / f"range-{flavor}.cpp").write_text(complete + structure + functions + "\n" + (ROOT / "native/range-runner.cpp").read_text())
(OUT / "range-extraction.json").write_text(json.dumps(helper["records"], indent=2) + "\n")
