import hashlib, json, os, subprocess, sys
from pathlib import Path

here = Path(__file__).resolve().parent
root = here.parents[1]
phase = sys.argv[1]
assert phase in ["baseline", "candidate"]
h = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
snapshot = json.loads((here / (phase + "-input.json")).read_text())
def verify():
    for group in ["fixed", "binaries"]:
        for name, pin in snapshot[group].items():
            p = root / name
            assert (h(p) if p.exists() else None) == pin, name
verify()
(here / (phase + "-before.json")).write_text(json.dumps(snapshot, indent=2) + "\n")
raw_path = here / (phase + "-raw.jsonl")
command = ["/Users/bgrins/venvs/firefox/bin/python", "./mach", "wpt", "--binary", "objdir-full.noindex/dist/Nightly.app/Contents/MacOS/firefox", "--headless", "--processes=1", "--log-raw", str(raw_path)]
command += ["testing/web-platform/tests/" + n for n in snapshot["tests"]]
log = here / (phase + "-console.log")
with log.open("w") as out:
    r = subprocess.run(command, cwd=root, env=dict(os.environ, MOZ_SKIP_PATH_PERFORMANCE_CHECK="1"), stdout=out, stderr=subprocess.STDOUT)
(here / (phase + "-exit.json")).write_text(json.dumps(dict(command=command, exit_code=r.returncode), indent=2) + "\n")
verify()
(here / (phase + "-after.json")).write_text(json.dumps(snapshot, indent=2) + "\n")
raw = [json.loads(s) for s in raw_path.read_text().splitlines()]
assert any(x["action"] == "suite_end" for x in raw)
rows = [{k:x[k] for k in ["action", "test", "subtest", "status", "expected", "message"] if k in x} for x in raw if x["action"] in ["test_status", "test_end"]]
keys = [(x["action"], x["test"], x.get("subtest")) for x in rows]
assert len(keys) == len(set(keys)) == 33
numeric = [x for x in rows if x["action"] == "test_status" and x["test"].endswith("/numeric-compensated-exponent.html")]
assert len(numeric) == 11
result = dict(exit_code=r.returncode, stable_pins=True, numeric_pass=sum(x["status"] == "PASS" for x in numeric), numeric_fail=sum(x["status"] == "FAIL" for x in numeric), rows=rows, raw_sha256=h(raw_path), console_sha256=h(log))
(here / (phase + "-result.json")).write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps({k:v for k,v in result.items() if k != "rows"}, indent=2))
