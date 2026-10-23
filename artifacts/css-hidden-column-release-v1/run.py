import hashlib
import json
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
RUNTIME = ROOT / "artifacts/css-hidden-layout-compact-runtime-v3"
FIXTURE = ROOT / "artifacts/css-hidden-column-diagnostic-v1/hidden-column-independent-trigger.html"
TEST = ROOT / "testing/web-platform/tests/css/css-contain/content-visibility/hidden-column-independent-trigger.html"
BINARY = Path("/Applications/Firefox.app/Contents/MacOS/firefox")
ENV = dict(os.environ, MOZ_SKIP_PATH_PERFORMANCE_CHECK="1", GIT_OPTIONAL_LOCKS="0",
           GIT_CONFIG_COUNT="1", GIT_CONFIG_KEY_0="core.fsmonitor", GIT_CONFIG_VALUE_0="false")
ENV["MOZ_DISABLE_SAFE_MODE_KEY"] = "1"
ENV.pop("MOZ_SAFE_MODE_RESTART", None)
def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else None
def save(n, value):
    (HERE / n).write_text(json.dumps(value, indent=2) + "\n")
state = json.loads((RUNTIME / "STATE.json").read_text())
assert state["status"] in ["restoring original sources", "terminal"]
assert len(state["phases"]) == 6 and len(state["traces"]) == 2
assert not TEST.exists() and not TEST.is_symlink() and not (HERE / "BEFORE.json").exists()
assert digest(FIXTURE) == "4633f2c6c7a60e9b9d63c30a64628127c4244ae10b1019770d179af360e16c2e"
paths = [BINARY, BINARY.parent / "XUL", FIXTURE,
         ROOT / "testing/web-platform/tests/resources/testharness.js",
         ROOT / "testing/web-platform/tests/resources/testharnessreport.js"]
meta = ROOT / "testing/web-platform/meta" / TEST.relative_to(ROOT / "testing/web-platform/tests")
paths.append(Path(str(meta) + ".ini"))
paths.extend(p / "__dir__.ini" for p in meta.parents if p == ROOT / "testing/web-platform/meta" or ROOT / "testing/web-platform/meta" in p.parents)
paths.extend(ROOT / n for n in json.loads((RUNTIME / "INPUTS.json").read_text())["source_pins"])
before = {str(p): digest(p) for p in paths}
assert all(before[str(p)] is not None for p in [BINARY, BINARY.parent / "XUL", FIXTURE])
save("BEFORE.json", before)
command = ["./mach", "wpt", "--headless", "--processes=1", "--binary=" + str(BINARY),
           "--log-raw=" + str(HERE / "raw.json"), str(TEST.relative_to(ROOT))]
save("COMMAND.json", command)
owned = False
try:
    with TEST.open("xb") as f:
        owned = True
        f.write(FIXTURE.read_bytes())
    with (HERE / "wpt.log").open("w") as log:
        code = subprocess.run(command, cwd=ROOT, env=ENV, stdout=log, stderr=subprocess.STDOUT).returncode
    events = [json.loads(line) for line in (HERE / "raw.json").read_text().splitlines()]
    rows = [r for r in events if r.get("action") == "test_status"]
    ends = [r for r in events if r.get("action") == "test_end"]
    expected = [f"Independent hidden column trigger: {route}, {selector}" for route in ["outer-width", "table-width"] for selector in ["col", "colgroup", "td", "table"]]
    complete = code in [0, 1] and len(ends) == 1 and ends[0]["status"] == "OK" and [r["subtest"] for r in rows] == expected and all(r["status"] in ["PASS", "FAIL"] for r in rows) and sum(e.get("action") == "suite_end" for e in events) == 1
    save("RESULT.json", {"exit":code,"complete":complete,"rows":rows,"ends":ends})
    assert complete
finally:
    if owned:
        TEST.unlink()
    after = {str(p):digest(p) for p in paths}
    save("AFTER.json", after)
    save("CLEANUP.json", {"temporary_test_absent":not TEST.exists(),"inputs_stable":before == after})
    assert before == after and not TEST.exists()
print(json.dumps({"complete":complete,"counts":{s:sum(r["status"] == s for r in rows) for s in ["PASS","FAIL"]}},indent=2))
