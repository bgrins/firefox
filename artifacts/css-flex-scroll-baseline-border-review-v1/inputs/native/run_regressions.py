import hashlib
import json
import os
from pathlib import Path
import re
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
tests = json.loads((HERE / "REGRESSION-TESTS.json").read_text())
paths = set(tests) | {
    "layout/generic/ScrollContainerFrame.cpp",
    "layout/generic/nsFlexContainerFrame.cpp",
    "layout/generic/nsFlexContainerFrame.h",
    "objdir-full.noindex/dist/Nightly.app/Contents/MacOS/firefox",
    "objdir-full.noindex/dist/Nightly.app/Contents/MacOS/XUL",
    str(Path(__file__).resolve().relative_to(ROOT)),
    str((HERE / "REGRESSION-TESTS.json").relative_to(ROOT)),
}
for test in tests:
    source = ROOT / test
    for target in re.findall(r'<link[^>]*rel=["\']match["\'][^>]*href=["\']([^"\']+)', source.read_text()):
        reference = source.parent / target
        if reference.exists():
            paths.add(str(reference.resolve().relative_to(ROOT)))
    meta = ROOT / "testing/web-platform/meta" / Path(test).relative_to("testing/web-platform/tests")
    paths.add(str(Path(str(meta) + ".ini").relative_to(ROOT)))
    for parent in meta.parents:
        if parent == ROOT / "testing/web-platform/meta" or ROOT / "testing/web-platform/meta" in parent.parents:
            paths.add(str((parent / "__dir__.ini").relative_to(ROOT)))
dirty = subprocess.check_output(["git", "-c", "core.fsmonitor=false", "diff", "--name-only"], cwd=ROOT, text=True)
paths.update(p for p in dirty.splitlines() if p.startswith(("dom/", "layout/", "servo/")))


def pins():
    result = {}
    for name in sorted(paths):
        path = ROOT / name
        if path.exists():
            with path.open("rb") as f:
                result[name] = hashlib.file_digest(f, "sha256").hexdigest()
        else:
            result[name] = None
    return result


out = HERE / "regressions-v1"
out.mkdir(exist_ok=False)
before = pins()
command = ["./mach", "wpt", "--headless", "--processes=1", "--log-raw=" + str(out / "raw.json"), *tests]
record = {"command": command, "before": before, "status": "running"}
(out / "RUN.json").write_text(json.dumps(record, indent=2) + "\n")
with (out / "wpt.log").open("w") as log:
    result = subprocess.run(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT,
                            env={**os.environ, "MOZ_SKIP_PATH_PERFORMANCE_CHECK": "1"})
after = pins()
raw = [json.loads(line) for line in (out / "raw.json").read_text().splitlines()]
ends = [r for r in raw if r.get("action") == "test_end"]
rows = [r for r in raw if r.get("action") == "test_status"]
expected_tests = {"/" + str(Path(t).relative_to("testing/web-platform/tests")) for t in tests}
complete = (result.returncode == 0 and before == after and len(ends) == len(tests)
            and {r["test"] for r in ends} == expected_tests
            and sum(r.get("action") == "suite_end" for r in raw) == 1)
record.update(status="done", complete=complete, exit=result.returncode, after=after,
              stable_pins=before == after, tests=ends, subtests=rows)
(out / "RUN.json").write_text(json.dumps(record, indent=2) + "\n")
print(json.dumps({"complete": complete, "exit": result.returncode, "tests": len(ends), "subtests": len(rows)}))
if not complete:
    raise RuntimeError("Regression run did not meet recorded gates")
