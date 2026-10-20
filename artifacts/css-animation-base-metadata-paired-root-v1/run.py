import hashlib
import json
import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
SOURCE = "dom/animation/KeyframeEffect.cpp"
TEST = "testing/web-platform/tests/css/css-values/animation-base-equal-payload-taint.html"
PROPOSAL = ROOT / "artifacts/css-animation-base-metadata-review-v1"


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def read(path):
    return json.loads(path.read_text())


original = read(ROOT / "artifacts/css-animation-base-metadata-root-v1/RUN.json")
pins = original["pins"].copy()
assert all(sha(ROOT / name) == digest for name, digest in pins.items())
assert pins[SOURCE] == "02ffed21d1fbbce1bd58d0df9964fa23cf1d162f3bb74212bf9e4096296463bf"
assert sha(PROPOSAL / "KeyframeEffect.candidate.cpp") == "ace5479efb2168a67e994c236851693d719f074aa1a978bedd6d0f7b47397da4"
assert sha(PROPOSAL / "native.patch") == "c411d12dbd01eafb122f95b3f02bf1df54b779f22e4bc04b0db623adfcae2e39"
probe = (ROOT / TEST).read_text()
needle = "  animation.currentTime = time + 1;"
assert probe.count(needle) == 1
probe = probe.replace(needle, """  const beforeSeek = observe(target);
  assert_equals(beforeSeek.payload, immediate.payload,
                "Control flushes preserve sampled payload");
  assert_equals(beforeSeek.image, immediate.image,
                "Control flushes preserve sampled URL taint");
""" + needle)
(ROOT / TEST).write_text(probe)
(HERE / "probe-v2.html").write_text(probe)
pins[TEST] = sha(ROOT / TEST)
record = {"phase": "baseline", "complete": False, "pins_before": pins.copy(),
          "scope": "Shared local tree; endpoint fix78 already present; only base comparison changes after strengthened baseline."}


def save():
    (HERE / "PAIR.json").write_text(json.dumps(record, indent=2) + "\n")


def stable():
    return all(sha(ROOT / name) == digest for name, digest in pins.items())


def run(command, log):
    with log.open("w") as stream:
        return subprocess.run(command, cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT,
                              env={**os.environ, "MOZ_SKIP_PATH_PERFORMANCE_CHECK": "1"}).returncode


def collect(path):
    raw = [json.loads(line) for line in path.read_text().splitlines()]
    assert sum(row.get("action") == "suite_end" for row in raw) == 1
    return ([row for row in raw if row.get("action") == "test_status"],
            [row for row in raw if row.get("action") == "test_end"])


save()
baseline = HERE / "baseline"
baseline.mkdir(exist_ok=False)
command = ["./mach", "wpt", "--headless", "--processes=1",
           "--setpref=layout.css.properties-and-values.enabled=true",
           "--log-raw=" + str(baseline / "raw.json"), TEST]
status = run(command, baseline / "wpt.log")
rows, ends = collect(baseline / "raw.json")
record["baseline"] = {"command": command, "exit": status, "rows": rows, "harness": ends, "stable": stable()}
save()
assert [row["subtest"] for row in rows] == [row["subtest"] for row in original["rows"]]
assert [row["status"] for row in rows] == ["FAIL", "PASS", "FAIL", "PASS", "FAIL", "PASS", "FAIL", "PASS"]
assert all("Immediate effect URL taint" in row.get("message", "") for row in rows if row["status"] == "FAIL")
assert len(ends) == 1 and ends[0]["status"] == "OK" and stable()
(ROOT / SOURCE).write_bytes((PROPOSAL / "KeyframeEffect.candidate.cpp").read_bytes())
command = ["./mach", "format", "--path", SOURCE]
record["format"] = {"command": command, "exit": run(command, HERE / "format.log")}
assert record["format"]["exit"] == 0
pins[SOURCE] = sha(ROOT / SOURCE)
(HERE / "KeyframeEffect.formatted.cpp").write_bytes((ROOT / SOURCE).read_bytes())
record.update(phase="building", candidate_source_sha256=pins[SOURCE])
save()
candidate = HERE / "candidate"
candidate.mkdir(exist_ok=False)
command = ["./mach", "build", "binaries"]
record["build"] = {"command": command, "exit": run(command, candidate / "build.log")}
assert record["build"]["exit"] == 0
for name in pins:
    if name.startswith("objdir-full.noindex/dist/Nightly.app/Contents/MacOS/"):
        pins[name] = sha(ROOT / name)
assert stable()
record.update(phase="candidate-wpt", pins_after=pins.copy())
save()
endpoint = read(ROOT / "artifacts/css-animation-endpoint-paired-root-v1/PAIR.json")
regression = read(ROOT / "artifacts/css-animation-endpoint-final-root-v1/REGRESSIONS.json")
tests = [arg for arg in endpoint["candidate_wpt"]["command"] if arg.startswith("testing/")]
tests += ["testing/web-platform/tests/web-animations/interfaces/KeyframeEffect/setKeyframes.html", TEST]
command = ["./mach", "wpt", "--headless", "--processes=1",
           "--setpref=layout.css.properties-and-values.enabled=true",
           "--log-raw=" + str(candidate / "raw.json"), *tests]
status = run(command, candidate / "wpt.log")
after, ends = collect(candidate / "raw.json")
key = lambda row: (row["test"], row["subtest"])
before = {key(row): row["status"] for row in endpoint["candidate_wpt"]["rows"] + regression["rows"] + rows}
after_map = {key(row): row["status"] for row in after}
record["candidate"] = {"command": command, "exit": status, "rows": after, "harness": ends}
record["changes"] = [{"identity": list(k), "before": before[k], "after": after_map.get(k)} for k in before if before[k] != after_map.get(k)]
record["complete"] = (status == 0 and len(before) == len(after_map) == len(after) == 189
                      and before.keys() == after_map.keys() and all(row["status"] == "PASS" for row in after)
                      and len(ends) == 14 and all(row["status"] == "OK" for row in ends) and stable())
record.update(phase="done", stable_after=stable())
save()
assert record["complete"]
print("189 PASS / 14 OK; four improvements; sources and binaries stable")
