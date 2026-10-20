import hashlib
import json
import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
AUDIT = ROOT / "artifacts/css-animation-base-metadata-audit-v1"
TEST = "testing/web-platform/tests/css/css-values/animation-base-equal-payload-taint.html"


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


assert sha(AUDIT / "FREEZE.json") == "7b319a18ea483bb42ded05b4ff4fc65967bd6c78d0707a124208325952867c58"
assert sha(AUDIT / "MANIFEST.json") == "7e8fb1b57a256c7e80bac13aa6715a99148ef2628987b81f175f40b728851b27"
for name, digest in json.loads((AUDIT / "MANIFEST.json").read_text()).items():
    assert not Path(name).is_absolute() and ".." not in Path(name).parts
    assert sha(AUDIT / name) == digest
assert not (ROOT / TEST).exists()
(ROOT / TEST).write_bytes((AUDIT / "probe.html").read_bytes())
pair_path = ROOT / "artifacts/css-animation-endpoint-paired-root-v1/PAIR.json"
pair = json.loads(pair_path.read_text())
assert pair["complete"]
pins = dict(pair["candidate_pins"])
transfer = json.loads((ROOT / "artifacts/css-animation-endpoint-final-root-v1/FORMAT-TRANSFER.json").read_text())
assert pins[transfer["path"]] == transfer["before_sha256"]
pins[transfer["path"]] = transfer["after_sha256"]
pins[TEST] = sha(ROOT / TEST)
pins.update({"objdir-full.noindex/dist/Nightly.app/Contents/MacOS/" + name: digest
             for name, digest in pair["candidate_binaries"].items()})


def stable():
    return all(sha(ROOT / name) == digest for name, digest in pins.items())


assert stable()
command = ["./mach", "wpt", "--headless", "--processes=1",
           "--setpref=layout.css.properties-and-values.enabled=true",
           "--log-raw=" + str(HERE / "raw.json"), TEST]
with (HERE / "wpt.log").open("w") as stream:
    status = subprocess.run(command, cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT,
                            env={**os.environ, "MOZ_SKIP_PATH_PERFORMANCE_CHECK": "1"}).returncode
raw = [json.loads(line) for line in (HERE / "raw.json").read_text().splitlines()]
rows = [row for row in raw if row.get("action") == "test_status"]
ends = [row for row in raw if row.get("action") == "test_end"]
record = {"pair_sha256": sha(pair_path), "pins": pins, "command": command, "exit": status,
          "rows": rows, "harness": ends, "stable_after": stable(),
          "suite_ends": sum(row.get("action") == "suite_end" for row in raw)}
(HERE / "RUN.json").write_text(json.dumps(record, indent=2) + "\n")
assert record["stable_after"] and record["suite_ends"] == 1
assert len(rows) == 8 and len({row["subtest"] for row in rows}) == 8
assert len(ends) == 1 and ends[0]["status"] == "OK"
for row in rows:
    print(row["status"], row["subtest"], row.get("message", ""))
