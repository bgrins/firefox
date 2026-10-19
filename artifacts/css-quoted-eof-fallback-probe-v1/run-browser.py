import hashlib
import json
import os
from pathlib import Path
import subprocess

here = Path(__file__).resolve().parent
root = here.parents[1]
snapshot = json.loads((here / "browser-input.json").read_text())


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None


def verify():
    for group in ["fixed", "binaries"]:
        for name, expected in snapshot[group].items():
            assert digest(root / name) == expected, name


verify()
(here / "browser-before.json").write_text(json.dumps(snapshot, indent=2) + "\n")
raw_path = here / "browser-raw.jsonl"
command = [
    "/Users/bgrins/venvs/firefox/bin/python", "./mach", "wpt", "--binary",
    "objdir-full.noindex/dist/Nightly.app/Contents/MacOS/firefox",
    "--headless", "--processes=1", "--log-raw", str(raw_path),
] + ["testing/web-platform/tests/" + name for name in snapshot["tests"]]
with (here / "browser-console.log").open("w") as output:
    result = subprocess.run(command, cwd=root,
        env=dict(os.environ, MOZ_SKIP_PATH_PERFORMANCE_CHECK="1"),
        stdout=output, stderr=subprocess.STDOUT)
(here / "browser-exit.json").write_text(json.dumps(
    dict(command=command, exit_code=result.returncode), indent=2) + "\n")
verify()
(here / "browser-after.json").write_text(json.dumps(snapshot, indent=2) + "\n")
raw = [json.loads(line) for line in raw_path.read_text().splitlines()]
assert any(row["action"] == "suite_end" for row in raw)
rows = [{key: row[key] for key in ["action", "test", "subtest", "status", "expected", "message"]
         if key in row} for row in raw if row["action"] in ["test_status", "test_end"]]
assert {row["test"] for row in rows} == {"/" + name for name in snapshot["tests"]}
assert len(rows) == len({(row["action"], row["test"], row.get("subtest")) for row in rows})
record = dict(exit_code=result.returncode, stable_pins=True, rows=rows,
              raw_sha256=digest(raw_path), console_sha256=digest(here / "browser-console.log"))
(here / "browser-result.json").write_text(json.dumps(record, indent=2) + "\n")
print(json.dumps(dict(exit_code=result.returncode, outcomes=len(rows),
    unexpected=[row for row in rows if "expected" in row]), indent=2))
