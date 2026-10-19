import hashlib, json, os, subprocess, sys
from pathlib import Path
here = Path(__file__).resolve().parent
root = here.parents[1]
worktree = Path("/private/tmp/firefox-fontface-standalone-20261019")
phase = sys.argv[1]
assert phase in ["without-support", "with-support"]
h = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
get = lambda n: h(worktree / n) if (worktree / n).exists() else None
base = json.loads((here / "without-support-build-before.json").read_text())
expected = dict(base["fixed"])
worker = "layout/style/FontFaceSetWorkerImpl.cpp"
if phase == "with-support":
    expected[worker] = "a631561784f71dc3a81941e9737fae8c5d40c2e0920600347774a5a4b218cd33"
for n, pin in expected.items():
    assert get(n) == pin, n
integration = root / "artifacts/css-fontface-provider-integration-v3"
run = json.loads((integration / "RUN.json").read_text())
tests = run["matrix"] + ["testing/web-platform/tests/css/css-font-loading/fontface-loaded-descriptor-retirement.any.js"]
tests += [n for n in run["regressions"] if not n.endswith("fontfaceset-remove-canvas.any.js")]
names = set(expected)
for group in ["RESOURCE-PINS.json", "CONTEXT-PINS.json", "METADATA-PINS.json"]:
    names.update(json.loads((integration / group).read_text()))
names.update(tests)
for n in tests:
    meta = n.replace("testing/web-platform/tests/", "testing/web-platform/meta/")
    names.add(meta + ".ini")
    if meta.endswith(".any.js"):
        names.update([meta[:-3] + ".html.ini", meta[:-3] + ".worker.html.ini"])
names.update(["testing/web-platform/tests/config.json", "objdir-full.noindex/mozinfo.json", "objdir-full.noindex/.mozconfig.json"])
fixed = {n: get(n) for n in sorted(names)}
binaries = {n: get(n) for n in run["binary_pins"]}
assert all(binaries.values())
snapshot = dict(base=base["base"], phase=phase, worktree=str(worktree), fixed=fixed, binaries=binaries, tests=tests)
(here / (phase + "-before.json")).write_text(json.dumps(snapshot, indent=2) + "\n")
raw_path = here / (phase + "-raw.jsonl")
command = [run["python"], "./mach", "wpt", "--binary", run["binary"], "--headless", "--processes=1", "--log-raw", str(raw_path)] + tests
log = here / (phase + "-console.log")
with log.open("w") as output:
    r = subprocess.run(command, cwd=worktree, env=dict(os.environ, MOZ_SKIP_PATH_PERFORMANCE_CHECK="1"), stdout=output, stderr=subprocess.STDOUT)
(here / (phase + "-exit.json")).write_text(json.dumps(dict(command=command, exit_code=r.returncode, console_sha256=h(log)), indent=2) + "\n")
for group in [fixed, binaries]:
    for n, pin in group.items():
        assert get(n) == pin, n
(here / (phase + "-after.json")).write_text(json.dumps(snapshot, indent=2) + "\n")
raw = [json.loads(s) for s in raw_path.read_text().splitlines()]
assert any(x["action"] == "suite_end" for x in raw)
rows = [{k:x[k] for k in ["action","test","subtest","status","expected","message"] if k in x} for x in raw if x["action"] in ["test_status","test_end"]]
keys = [(x["action"],x["test"],x.get("subtest")) for x in rows]
assert len(keys) == len(set(keys))
assert sum(x["action"] == "test_end" for x in rows) == 11
new = [x for x in rows if x["action"] == "test_status" and "/fontface-loaded-" in x["test"]]
assert len(new) == 76
summary = dict(exit_code=r.returncode, stable_pins=True, rows=rows, new_subtests=len(new), new_pass=sum(x["status"]=="PASS" for x in new), new_fail=sum(x["status"]=="FAIL" for x in new), raw_sha256=h(raw_path), console_sha256=h(log))
(here / (phase + "-result.json")).write_text(json.dumps(summary,indent=2) + "\n")
print(json.dumps({k:v for k,v in summary.items() if k!="rows"},indent=2))
