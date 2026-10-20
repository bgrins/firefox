import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
parser = argparse.ArgumentParser()
parser.add_argument("phase", choices=["baseline", "candidate"])
args = parser.parse_args()
tests = ["testing/web-platform/tests/css/css-position/sticky/position-sticky-large-negative-insets.html"]
paths = {"layout/generic/StickyScrollContainer.cpp", "layout/generic/StickyScrollContainer.h"}
paths.update(tests)
paths.add(str(Path(__file__).resolve().relative_to(ROOT)))
paths.update([
    "testing/web-platform/tests/resources/testharness.js",
    "testing/web-platform/tests/resources/testharnessreport.js",
    "objdir-full.noindex/dist/Nightly.app/Contents/MacOS/firefox",
    "objdir-full.noindex/dist/Nightly.app/Contents/MacOS/XUL",
])
dirty = subprocess.check_output(["git", "-c", "core.fsmonitor=false", "diff", "--name-only"], cwd=ROOT, text=True)
paths.update(p for p in dirty.splitlines() if p.startswith(("dom/", "layout/", "servo/")))

def pins():
    result = {}
    for name in sorted(paths):
        with (ROOT / name).open("rb") as stream:
            result[name] = hashlib.file_digest(stream, "sha256").hexdigest()
    for test in tests:
        meta = ROOT / "testing/web-platform/meta" / Path(test).relative_to("testing/web-platform/tests")
        candidates = [Path(str(meta) + ".ini")]
        candidates += [parent / "__dir__.ini" for parent in meta.parents
            if parent == ROOT / "testing/web-platform/meta" or ROOT / "testing/web-platform/meta" in parent.parents]
        for candidate in candidates:
            result[str(candidate.relative_to(ROOT))] = hashlib.sha256(candidate.read_bytes()).hexdigest() if candidate.exists() else None
    return result

out = HERE / (args.phase + "-wpt-v1")
out.mkdir(exist_ok=False)
before = pins()
for name, digest in before.items():
    source = ROOT / name
    if digest is not None and not name.startswith("objdir-full.noindex/"):
        target = out / "inputs" / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(source.read_bytes())

command = ["./mach", "wpt", "--headless", "--processes=1", "--log-raw=" + str(out / "raw.json"), *tests]
record = {"phase": args.phase, "command": command, "before": before, "status": "running"}
(out / "RUN.json").write_text(json.dumps(record, indent=2) + "\n")
with (out / "wpt.log").open("w") as log:
    process = subprocess.run(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT,
        env={**os.environ, "MOZ_SKIP_PATH_PERFORMANCE_CHECK": "1"})
after = pins()
raw = [json.loads(line) for line in (out / "raw.json").read_text().splitlines()]
rows = [row for row in raw if row.get("action") == "test_status"]
ends = [row for row in raw if row.get("action") == "test_end"]
failures = [row for row in rows if row["status"] != "PASS"]
identity = lambda row: (row["test"], row["subtest"])
complete = (before == after and len(rows) == len({identity(row) for row in rows}) == 60
    and len(ends) == 1 and all(row["status"] == "OK" for row in ends)
    and sum(row.get("action") == "suite_end" for row in raw) == 1)
if args.phase == "baseline":
    complete &= process.returncode == 1 and len(failures) == 24 and all(row["status"] == "FAIL" for row in failures)
else:
    complete &= process.returncode == 0 and not failures
record.update(status="done", complete=complete, exit=process.returncode, after=after,
    stable_pins=before == after, rows=rows, harness=ends, failures=failures,
    scope="Shared local build with pinned inputs; no isolated upstream build claim.")
(out / "RUN.json").write_text(json.dumps(record, indent=2) + "\n")
print(json.dumps({"complete": complete, "exit": process.returncode, "rows": len(rows), "failures": len(failures)}))
if not complete:
    raise RuntimeError("WPT run did not meet its recorded gates")
