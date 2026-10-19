from collections import Counter, defaultdict
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

here = Path(__file__).resolve().parent
repo = here.parents[1]
phase = sys.argv[1]
assert phase in {"baseline-v1", "candidate-v1"}
tests = ["testing/web-platform/tests/css/css-values/" + name for name in [
    "attr-registered-relative-dependencies.html", "attr-typed-fallback-eligibility.html", "attr-cycle.html"]]
paths = {*tests,
         "mozconfig", "objdir-full.noindex/.mozconfig.json", "objdir-full.noindex/mozinfo.json",
         "testing/web-platform/tests/css/css-values/attr-namespace-case-sensitivity-ref.xhtml",
         "testing/web-platform/tests/css/reference/ref-filled-green-100px-square.xht", str(Path(__file__).relative_to(repo)),
         "servo/components/style/custom_properties.rs",
         "servo/components/style/properties/mod.rs",
         "servo/components/style/properties_and_values/value.rs",
         "servo/components/style/parser.rs",
         "servo/components/style/properties/cascade.rs",
         "servo/components/style/dom.rs",
         "servo/ports/geckolib/glue.rs",
         "testing/web-platform/tests/resources/testharness.js",
         "testing/web-platform/tests/resources/testharnessreport.js",
         "testing/web-platform/tests/config.json",
         "objdir-full.noindex/dist/Nightly.app/Contents/MacOS/firefox",
         "objdir-full.noindex/dist/Nightly.app/Contents/MacOS/XUL"}
absent = set()
for test_path in tests:
    metadata = Path(test_path.replace("/tests/", "/meta/") + ".ini")
    for path in [metadata, *(parent / "__dir__.ini" for parent in metadata.parents
                            if str(parent).startswith("testing/web-platform/meta"))]:
        (paths if (repo / path).is_file() else absent).add(str(path))


def pins():
    return {name: hashlib.file_digest((repo / name).open("rb"), "sha256").hexdigest()
            for name in sorted(paths)}


raw = here / (phase + ".jsonl")
log = here / (phase + ".log")
receipt = here / (phase + "-receipt.json")
assert not any(path.exists() for path in [raw, log, receipt])
before = pins()
snapshots = here / (phase + "-sources")
snapshots.mkdir()
for name in paths:
    if name not in {"objdir-full.noindex/dist/Nightly.app/Contents/MacOS/firefox", "objdir-full.noindex/dist/Nightly.app/Contents/MacOS/XUL"}:
        (snapshots / name.replace("/", "__")).write_bytes((repo / name).read_bytes())
command = ["/Users/bgrins/venvs/firefox/bin/python", "./mach", "wpt", "--binary",
           "objdir-full.noindex/dist/Nightly.app/Contents/MacOS/firefox", "--headless",
           "--processes=1", "--log-raw", str(raw), *tests]
record = {"phase": phase, "command": command, "pins_before": before,
          "absent_before": sorted(absent), "tests": tests}
(here / (phase + "-inputs.json")).write_text(json.dumps(record, indent=2) + "\n")
with log.open("w") as stream:
    process = subprocess.run(command, cwd=repo, stdout=stream, stderr=subprocess.STDOUT,
                             env={**os.environ, "MOZ_SKIP_PATH_PERFORMANCE_CHECK": "1"})
after = pins()
events = [json.loads(line) for line in raw.read_text().splitlines()] if raw.exists() else []
statuses = [event for event in events if event.get("action") in {"test_status", "test_end"}]
counts = defaultdict(Counter)
for event in statuses:
    counts[event["test"]][event["status"]] += 1
record.update({"exit_code": process.returncode, "pins_after": after,
               "all_inputs_unchanged": before == after,
               "absent_after": sorted(name for name in absent if not (repo / name).exists()),
               "counts": dict(counts), "statuses": statuses,
               "suite_end_count": sum(event.get("action") == "suite_end" for event in events)})
receipt.write_text(json.dumps(record, indent=2) + "\n")
print(json.dumps({key: record[key] for key in ["exit_code", "all_inputs_unchanged", "counts", "suite_end_count"]}))
raise SystemExit(process.returncode if before == after and record["absent_before"] == record["absent_after"] else 2)
