import hashlib
import json
import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
TEST = "testing/web-platform/tests/css/css-values/animation-equal-payload-taint.html"
EXPECTED = ['setKeyframes literal to attr, same payload', 'setKeyframes literal to attr, different payload', 'Fresh literal effect', 'setKeyframes attr to literal, same payload', 'setKeyframes attr to literal, different payload', 'Fresh attr effect']


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


association = ROOT / "artifacts/css-custom-properties-map-taint-root-v1/paired/PAIR.json"
pair = json.loads(association.read_text())
assert pair["complete"] and pair["candidate_binary_validated"]
assert digest(ROOT / TEST) == digest(HERE / "test.html")
inherited = {
    **pair["stable_pins"],
    **pair["source_pins"]["candidate"],
    **{
        "objdir-full.noindex/dist/Nightly.app/Contents/MacOS/" + name: pin
        for name, pin in pair["final_binaries"].items()
    },
}
for name, pin in inherited.items():
    assert digest(ROOT / name) == pin, name
assert not (HERE / "RUN.json").exists() and not (HERE / "raw.json").exists()
pins = {**inherited, TEST: digest(ROOT / TEST), "runner": digest(Path(__file__)),
        "association": digest(association)}
command = ["./mach", "wpt", "--headless", "--processes=1",
           "--setpref=layout.css.properties-and-values.enabled=true",
           "--log-raw=" + str(HERE / "raw.json"), TEST]
with (HERE / "wpt.log").open("w") as log:
    result = subprocess.run(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT,
                            env={**os.environ, "MOZ_SKIP_PATH_PERFORMANCE_CHECK": "1"})
events = [json.loads(line) for line in (HERE / "raw.json").read_text().splitlines()]
rows = [e for e in events if e.get("action") == "test_status"]
ends = [e for e in events if e.get("action") == "test_end"]
suite = [i for i, e in enumerate(events) if e.get("action") == "suite_end"]
stable = all(digest(ROOT / name) == pin for name, pin in inherited.items())
stable = stable and digest(ROOT / TEST) == pins[TEST]
stable = stable and digest(Path(__file__)) == pins["runner"]
stable = stable and digest(association) == pins["association"]
record = {"command": command, "exit": result.returncode, "pins": pins,
          "stable_after": stable, "rows": rows, "harness": ends,
          "suite_end_positions": suite, "scope": "Existing local candidate build; diagnostic only."}
(HERE / "RUN.json").write_text(json.dumps(record, indent=2) + "\n")
assert stable and result.returncode in {0, 1}
assert [e["subtest"] for e in rows] == EXPECTED
assert all(e["test"] == "/css/css-values/animation-equal-payload-taint.html"
           and e["status"] in {"PASS", "FAIL"} for e in rows)
assert len(ends) == 1 and ends[0]["status"] == "OK"
assert len(suite) == 1
assert max(i for i, e in enumerate(events)
           if e.get("action") in {"test_status", "test_end"}) < suite[0]
print(json.dumps({s: sum(e["status"] == s for e in rows) for s in ["PASS", "FAIL"]}))
