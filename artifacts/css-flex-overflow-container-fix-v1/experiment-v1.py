import hashlib
import json
import os
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = ROOT / "layout/generic/nsFlexContainerFrame.cpp"
TEST = ROOT / "testing/web-platform/tests/css/css-flexbox/flexbox-overflow-container-final-position.html"
GIT = ["git", "-c", "core.fsmonitor=false"]
ENV = {**os.environ, "MOZ_SKIP_PATH_PERFORMANCE_CHECK": "1"}


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def git(*args):
    return subprocess.check_output(GIT + list(args), cwd=ROOT)


def save(name, data):
    (HERE / name).write_text(json.dumps(data, indent=2) + "\n")


def command(name, args):
    with (HERE / (name + ".log")).open("w") as log:
        result = subprocess.run(args, cwd=ROOT, env=ENV, stdout=log, stderr=subprocess.STDOUT)
    save(name + ".json", {"command": args, "exit": result.returncode})
    return result.returncode


def test_run(name):
    directory = HERE / name
    directory.mkdir()
    paths = {str(SOURCE.relative_to(ROOT)), str(TEST.relative_to(ROOT)),
             "objdir-full.noindex/dist/Nightly.app/Contents/MacOS/firefox",
             "objdir-full.noindex/dist/Nightly.app/Contents/MacOS/XUL",
             "testing/web-platform/tests/resources/testharness.js",
             "testing/web-platform/tests/resources/testharnessreport.js"}
    paths.update(p for p in git("diff", "--name-only").decode().splitlines()
                 if p.startswith(("layout/", "dom/", "servo/")))
    meta = ROOT / "testing/web-platform/meta/css/css-flexbox"
    for parent in [meta, *meta.parents]:
        if parent == ROOT / "testing/web-platform/meta" or ROOT / "testing/web-platform/meta" in parent.parents:
            paths.add(str((parent / "__dir__.ini").relative_to(ROOT)))
    paths.add("testing/web-platform/meta/css/css-flexbox/" + TEST.name + ".ini")
    def pins():
        return {p: sha(ROOT / p) if (ROOT / p).exists() else None for p in sorted(paths)}
    before = pins()
    for p, pin in before.items():
        if pin is None or p.startswith("objdir-full.noindex/"):
            continue
        destination = directory / "inputs" / p
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes((ROOT / p).read_bytes())
    code = command(name + "-wpt", ["./mach", "wpt", "--headless", "--processes=1",
                   "--log-raw=" + str(directory / "raw.json"), str(TEST.relative_to(ROOT))])
    events = [json.loads(line) for line in (directory / "raw.json").read_text().splitlines()]
    rows = [r for r in events if r.get("action") == "test_status"]
    ends = [r for r in events if r.get("action") == "test_end"]
    complete = (len(rows) == 336 and len({r["subtest"] for r in rows}) == 336
                and len(ends) == 1 and ends[0]["status"] == "OK"
                and sum(r.get("action") == "suite_end" for r in events) == 1)
    result = {"exit": code, "before": before, "after": pins(), "complete": complete,
              "rows": rows, "ends": ends, "failures": [r for r in rows if r["status"] != "PASS"]}
    (directory / "RUN.json").write_text(json.dumps(result, indent=2) + "\n")
    assert complete and before == pins()
    return {"exit": code, "rows": len(rows), "failures": len(result["failures"])}


assert not TEST.exists()
before = SOURCE.read_bytes()
head = git("rev-parse", "HEAD").decode().strip()
index = git("diff", "--cached", "--binary")
(HERE / "before.cpp").write_bytes(before)
save("BEFORE.json", {"head": head, "source_sha256": sha(SOURCE),
                     "index_diff_sha256": hashlib.sha256(index).hexdigest(), "test_absent": True})
state = {"status": "testing baseline", "accepted": False}
save("STATE.json", state)
try:
    TEST.write_bytes((HERE / TEST.name).read_bytes())
    state["baseline"] = test_run("baseline")
    state["status"] = "building candidate"
    save("STATE.json", state)
    patch = HERE / "native-only.patch"
    git("apply", "--check", str(patch))
    git("apply", str(patch))
    (HERE / "candidate.cpp").write_bytes(SOURCE.read_bytes())
    state["candidate_build_exit"] = command("candidate-build", ["./mach", "build", "binaries"])
    if state["candidate_build_exit"] == 0:
        state["status"] = "testing candidate"
        save("STATE.json", state)
        state["candidate"] = test_run("candidate")
finally:
    state["status"] = "restoring source and build"
    save("STATE.json", state)
    if SOURCE.read_bytes() != before:
        SOURCE.write_bytes(before)
    TEST.unlink(missing_ok=True)
    state["restore_build_exit"] = command("restore-build", ["./mach", "build", "binaries"])
    state["source_restored"] = SOURCE.read_bytes() == before and not TEST.exists()
    state["head_unchanged"] = git("rev-parse", "HEAD").decode().strip() == head
    state["index_unchanged"] = git("diff", "--cached", "--binary") == index
    state["status"] = "terminal"
    save("STATE.json", state)
    print(json.dumps(state, indent=2))
    assert state["restore_build_exit"] == 0 and all(state[k] for k in ["source_restored", "head_unchanged", "index_unchanged"])
