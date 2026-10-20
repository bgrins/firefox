import hashlib
import json
import os
from html.parser import HTMLParser
from pathlib import Path
import subprocess
from urllib.parse import unquote, urlsplit

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PROPOSAL = ROOT / "artifacts/css-cssom-exact-traversal-proposal-v3"
SOURCES = ["layout/generic/nsIFrame.cpp", "layout/generic/nsIFrame.h",
           "layout/base/nsLayoutUtils.cpp", "layout/base/nsLayoutUtils.h"]
SOURCE = ROOT / SOURCES[2]
TESTS = json.loads((HERE / "TESTS.json").read_text())
INSTALL = {TESTS[1]: "getBoundingClientRect-untransformed-edge-precision.html"}
GIT = ["git", "-c", "core.fsmonitor=false"]
ENV = {**os.environ, "MOZ_SKIP_PATH_PERFORMANCE_CHECK": "1"}
INPUTS = json.loads((HERE / "INPUTS.json").read_text())


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def git(*args):
    return subprocess.check_output(GIT + list(args), cwd=ROOT)


def save(name, value):
    (HERE / name).write_text(json.dumps(value, indent=2) + "\n")


def command(name, args):
    with (HERE / (name + ".log")).open("w") as log:
        result = subprocess.run(args, cwd=ROOT, env=ENV, stdout=log, stderr=subprocess.STDOUT)
    save(name + ".json", {"command": args, "exit": result.returncode})
    return result.returncode


def measure(kind):
    for repeat in [1, 2]:
        name = kind + "-" + str(repeat)
        assert command(name + "-driver", ["python3", "-I", "-S", "-B", str(HERE / "run_browser.py"), name]) == 0


class Links(HTMLParser):
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag in ("link", "script", "img"):
            value = attrs.get("href") or attrs.get("src")
            if value:
                self.links.append(value)


def test_run(kind):
    directory = HERE / kind
    directory.mkdir()
    paths = set(TESTS + SOURCES + list(INSTALL) + ["dom/base/DOMRect.cpp", str(SOURCE.relative_to(ROOT)),
        "objdir-full.noindex/dist/Nightly.app/Contents/MacOS/firefox",
        "objdir-full.noindex/dist/Nightly.app/Contents/MacOS/XUL"])
    paths.update(p for p in git("diff", "--name-only").decode().splitlines()
                 if p.startswith(("layout/", "dom/", "servo/")))
    for test in TESTS:
        meta = ROOT / "testing/web-platform/meta" / Path(test).relative_to("testing/web-platform/tests")
        paths.add(str(meta.relative_to(ROOT)) + ".ini")
        paths.update(str((parent / "__dir__.ini").relative_to(ROOT)) for parent in meta.parents
                     if parent == ROOT / "testing/web-platform/meta"
                     or ROOT / "testing/web-platform/meta" in parent.parents)
    pending = list(TESTS)
    scanned = set()
    while pending:
        name = pending.pop()
        if name in scanned:
            continue
        scanned.add(name)
        parser = Links()
        parser.links = []
        parser.feed((ROOT / name).read_text())
        for link in parser.links:
            url = urlsplit(link)
            if url.scheme or url.netloc or not url.path:
                continue
            rel = unquote(url.path)
            target = ((ROOT / "testing/web-platform/tests" / rel.lstrip("/"))
                      if rel.startswith("/") else (ROOT / name).parent / rel).resolve()
            if ROOT not in target.parents or not target.is_file():
                continue
            relative = str(target.relative_to(ROOT))
            paths.add(relative)
            if target.suffix in (".html", ".xhtml"):
                pending.append(relative)
    def pins():
        return {n: sha(ROOT / n) if (ROOT / n).exists() else None for n in sorted(paths)}
    before = pins()
    for name, pin in before.items():
        if pin is None or name.startswith("objdir-full.noindex/"):
            continue
        destination = directory / "inputs" / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes((ROOT / name).read_bytes())
    code = command(kind + "-wpt", ["./mach", "wpt", "--headless", "--processes=1",
                   "--log-raw=" + str(directory / "raw.json"), *TESTS])
    events = [json.loads(line) for line in (directory / "raw.json").read_text().splitlines()]
    rows = [r for r in events if r.get("action") == "test_status"]
    ends = [r for r in events if r.get("action") == "test_end"]
    expected = {"/" + str(Path(t).relative_to("testing/web-platform/tests")) for t in TESTS}
    complete = (len(ends) == len(TESTS) and {r["test"] for r in ends} == expected
                and len({(r["test"], r["subtest"]) for r in rows}) == len(rows)
                and all(r["status"] in ("OK", "PASS", "FAIL") for r in ends)
                and sum(r.get("action") == "suite_end" for r in events) == 1)
    result = {"exit": code, "complete": complete, "before": before, "after": pins(),
              "rows": rows, "ends": ends}
    (directory / "RUN.json").write_text(json.dumps(result, indent=2) + "\n")
    assert complete and before == result["after"]
    return {"exit": code, "complete": complete, "subtests": len(rows), "files": len(ends)}


def end_map(run):
    return {r["test"]: (r["status"], r.get("expected", r["status"])) for r in run["ends"]}


def result_map(kind):
    run = json.loads((HERE / kind / "RUN.json").read_text())
    return {(r["test"], r["subtest"]): (r["status"], r.get("expected", r["status"])) for r in run["rows"]}


assert not (HERE / "BEFORE.json").exists()
assert all(not (ROOT / name).exists() for name in INSTALL)
for name, expected in INPUTS["pins"].items():
    assert sha(ROOT / name) == expected, name
head = git("rev-parse", "HEAD")
index = git("diff", "--cached", "--binary")
assert head.decode().strip() == INPUTS["head"] and not index
before = {n: (ROOT / n).read_bytes() for n in SOURCES}
for n, data in before.items():
    assert data == (PROPOSAL / "original" / Path(n).name).read_bytes(), n
    target = HERE / "source-before" / n
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
fixed_pins = {n: sha(ROOT / n) for n in git("diff", "--name-only").decode().splitlines()
              if n.startswith(("layout/", "dom/", "servo/")) and n not in SOURCES}
fixed_pins["dom/base/DOMRect.cpp"] = sha(ROOT / "dom/base/DOMRect.cpp")
save("BEFORE.json", {"head": head.decode().strip(), "sources": {n: sha(ROOT / n) for n in SOURCES},
                     "fixed_native_pins": fixed_pins, "index_diff_sha256": hashlib.sha256(index).hexdigest()})
state = {"status": "starting", "accepted": False, "variants": {}}
save("STATE.json", state)
changed = False
try:
    for target, origin in INSTALL.items():
        (ROOT / target).write_bytes((HERE / origin).read_bytes())
    state["wpt_lint_exit"] = command("wpt-lint", ["./mach", "lint", "-l", "wpt", *INSTALL])
    assert state["wpt_lint_exit"] == 0
    state["status"] = "building baseline"
    save("STATE.json", state)
    state["baseline_build_exit"] = command("baseline-build", ["./mach", "build", "binaries"])
    assert state["baseline_build_exit"] == 0
    state["status"] = "testing baseline"
    save("STATE.json", state)
    state["variants"]["baseline"] = test_run("baseline")
    baseline = result_map("baseline")
    expected = json.loads((ROOT / "artifacts/css-cssom-rectangle-standalone-runtime-v1/dom-only/RUN.json").read_text())
    expected_rows = {(r["test"], r["subtest"]): (r["status"], r.get("expected", r["status"])) for r in expected["rows"]}
    assert baseline == expected_rows, "Baseline differs from retained DOM-only calibration"
    baseline_run = json.loads((HERE / "baseline/RUN.json").read_text())
    assert end_map(baseline_run) == end_map(expected), "Baseline file outcomes differ"
    state["status"] = "measuring baseline"
    save("STATE.json", state)
    measure("baseline-before")
    for n in SOURCES:
        changed = True
        (ROOT / n).write_bytes((PROPOSAL / "candidate" / Path(n).name).read_bytes())
    state["format_check_exit"] = command("format-check", ["./mach", "lint", "-W", "-l", "clang-format", *SOURCES])
    assert state["format_check_exit"] == 0
    state["status"] = "building candidate"
    save("STATE.json", state)
    state["candidate_build_exit"] = command("candidate-build", ["./mach", "build", "binaries"])
    assert state["candidate_build_exit"] == 0
    state["status"] = "testing candidate"
    save("STATE.json", state)
    state["variants"]["candidate"] = test_run("candidate")
    candidate = result_map("candidate")
    assert set(candidate) == set(baseline)
    candidate_run = json.loads((HERE / "candidate/RUN.json").read_text())
    assert end_map(candidate_run) == end_map(baseline_run), "Candidate file outcomes differ"
    new_test = "/" + str(Path(TESTS[1]).relative_to("testing/web-platform/tests"))
    for key, outcome in candidate.items():
        assert outcome == (("PASS", "PASS") if key[0] == new_test else baseline[key]), (key, outcome)
    state["status"] = "measuring candidate"
    save("STATE.json", state)
    measure("candidate")
except BaseException as error:
    state["failure"] = {"type": type(error).__name__, "message": str(error)}
    raise
finally:
    state["status"] = "restoring"
    save("STATE.json", state)
    for n, content in before.items():
        if (ROOT / n).read_bytes() != content:
            (ROOT / n).write_bytes(content)
    for target in INSTALL:
        (ROOT / target).unlink(missing_ok=True)
    if changed:
        state["restore_build_exit"] = command("restore-build", ["./mach", "build", "binaries"])
    state["source_restored"] = all((ROOT / n).read_bytes() == content for n, content in before.items()) and all(not (ROOT / n).exists() for n in INSTALL)
    state["other_native_unchanged"] = all(sha(ROOT / n) == pin for n, pin in fixed_pins.items())
    state["head_unchanged"] = git("rev-parse", "HEAD") == head
    state["index_unchanged"] = git("diff", "--cached", "--binary") == index
    state["status"] = "terminal-failed" if "failure" in state else "restored"
    save("STATE.json", state)
    assert not changed or state["restore_build_exit"] == 0
    assert all(state[k] for k in ["source_restored", "other_native_unchanged", "head_unchanged", "index_unchanged"])
    save("RESTORED.json", {n: sha(ROOT / n) for n in SOURCES + list(fixed_pins)})
state["status"] = "measuring restored baseline"
save("STATE.json", state)
measure("baseline-after")
state["status"] = "terminal"
save("STATE.json", state)
print(json.dumps(state, indent=2))
