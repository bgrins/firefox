import hashlib
import json
import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
PAIR = ROOT / "artifacts/css-animation-endpoint-paired-root-v1/PAIR.json"
TEST = "testing/web-platform/tests/web-animations/interfaces/KeyframeEffect/setKeyframes.html"


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


pair = json.loads(PAIR.read_text())
assert pair["complete"] and pair["build"]["exit"] == 0
pins = dict(pair["candidate_pins"])
binary = "objdir-full.noindex/dist/Nightly.app/Contents/MacOS/"
pins.update({binary + name: digest for name, digest in pair["candidate_binaries"].items()})
pins[TEST] = sha(ROOT / TEST)


def stable():
    return all(sha(ROOT / name) == digest for name, digest in pins.items())


assert stable()
command = ["./mach", "wpt", "--headless", "--processes=1",
           "--setpref=layout.css.properties-and-values.enabled=true",
           "--log-raw=" + str(HERE / "setKeyframes-raw.json"), TEST]
with (HERE / "setKeyframes.log").open("w") as stream:
    status = subprocess.run(command, cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT,
                            env={**os.environ, "MOZ_SKIP_PATH_PERFORMANCE_CHECK": "1"}).returncode
raw = [json.loads(line) for line in (HERE / "setKeyframes-raw.json").read_text().splitlines()]
rows = [row for row in raw if row.get("action") == "test_status"]
ends = [row for row in raw if row.get("action") == "test_end"]
record = {"pair_sha256": sha(PAIR), "pins": pins, "command": command, "exit": status,
          "rows": rows, "harness": ends, "stable_after": stable(),
          "suite_ends": sum(row.get("action") == "suite_end" for row in raw)}
(HERE / "REGRESSIONS.json").write_text(json.dumps(record, indent=2) + "\n")
assert status == 0 and rows and all(row["status"] == "PASS" for row in rows)
assert len(ends) == 1 and ends[0]["status"] == "OK"
assert record["stable_after"] and record["suite_ends"] == 1
print(f"{len(rows)} PASS; one harness OK; source and binary pins stable")
