import hashlib, json, os, subprocess
from pathlib import Path
root = Path(__file__).resolve().parents[2]
here = Path(__file__).resolve().parent
h = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
v = json.loads((here / "candidate-v3-build-after.json").read_text())
def verify():
    for group in ["fixed", "binaries"]:
        for n, expected in v[group].items():
            p = root / n
            assert (h(p) if p.exists() else None) == expected, n
verify()
(here / "candidate-v3-before.json").write_text(json.dumps(v, indent=2) + "\n")
command = ["/Users/bgrins/venvs/firefox/bin/python", "./mach", "wpt", "--binary", "objdir-full.noindex/dist/Nightly.app/Contents/MacOS/firefox", "--headless", "--processes=1", "--log-raw", str(here / "candidate-v3-raw.jsonl")]
command += ["testing/web-platform/tests/" + n for n in v["tests"]]
with (here / "candidate-v3-console.log").open("w") as out:
    r = subprocess.run(command, cwd=root, env=dict(os.environ, MOZ_SKIP_PATH_PERFORMANCE_CHECK="1"), stdout=out, stderr=subprocess.STDOUT)
(here / "candidate-v3-exit.json").write_text(json.dumps(dict(command=command, exit_code=r.returncode), indent=2) + "\n")
verify()
(here / "candidate-v3-after.json").write_text(json.dumps(v, indent=2) + "\n")
def rows(name):
    raw = [json.loads(s) for s in (here / name).read_text().splitlines()]
    assert any(x["action"] == "suite_end" for x in raw)
    result = {}
    for x in raw:
        if x["action"] not in ["test_status", "test_end"]:
            continue
        key = (x["action"], x["test"], x.get("subtest"))
        assert key not in result
        result[key] = (x["status"], x.get("expected", x["status"]))
    return result
before = rows("baseline-raw.jsonl")
regressions = rows("regressions-baseline-raw.jsonl")
assert not before.keys() & regressions.keys()
before.update(regressions)
after = rows("candidate-v3-raw.jsonl")
assert before.keys() == after.keys() and len(after) == 21
improvements = []
for key, old in before.items():
    new = after[key]
    if old != new:
        assert key[1] == "/css/css-syntax/identifier-start-escaped-newline.html"
        assert key[2].startswith("Invalid escaped ")
        assert old == ("FAIL", "PASS") and new == ("PASS", "PASS")
        improvements.append(list(key))
assert len(improvements) == 4 and r.returncode == 0
assert all(status == expected for status, expected in after.values())
result = dict(status="PASS", exit_code=r.returncode, checks=21, improvements=improvements, unchanged_checks=17, new_wpt_pass=11, prior_regression_checks=9, prior_expected_failures=4, pins_stable=True, raw_sha256=h(here / "candidate-v3-raw.jsonl"), console_sha256=h(here / "candidate-v3-console.log"), runtime_scope="Shared experimental tree; no isolated-base run")
(here / "candidate-v3-pair.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))
