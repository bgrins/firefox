import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise RuntimeError("Require python3 -I -S without optimization")
sys.dont_write_bytecode = True
import hashlib
import json
import os
from html.parser import HTMLParser
from pathlib import Path
import subprocess
from urllib.parse import unquote, urlsplit

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PROPOSAL = HERE
SOURCES = ["layout/generic/nsIFrame.cpp", "layout/generic/nsIFrame.h",
           "layout/base/nsLayoutUtils.cpp", "layout/base/nsLayoutUtils.h", "dom/base/DOMRect.cpp"]
SOURCE = ROOT / SOURCES[2]
TESTS = json.loads((HERE / "TESTS.json").read_text())
INSTALL = {TESTS[1]: "getBoundingClientRect-untransformed-edge-precision.html"}
GIT = ["git", "-c", "core.fsmonitor=false"]
ENV = {**os.environ, "MOZ_SKIP_PATH_PERFORMANCE_CHECK": "1", "GIT_OPTIONAL_LOCKS": "0"}
INPUTS = json.loads((HERE / "INPUTS.json").read_text())


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def git(*args):
    return subprocess.check_output(GIT + list(args), cwd=ROOT, env=ENV)


def save(name, value):
    (HERE / name).write_text(json.dumps(value, indent=2) + "\n")


def command(name, args):
    with (HERE / (name + ".log")).open("w") as log:
        result = subprocess.run(args, cwd=ROOT, env=ENV, stdout=log, stderr=subprocess.STDOUT)
    save(name + ".json", {"command": args, "exit": result.returncode})
    return result.returncode


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


assert sys.argv[1:] in ([], ["--preflight"])
assert not (HERE / "BEFORE.json").exists()
assert all(not (ROOT / name).exists() for name in INSTALL)
for name, expected in INPUTS["pins"].items():
    assert sha(ROOT / name) == expected, name
head = git("rev-parse", "HEAD")
index = git("diff", "--cached", "--binary")
index_entries = git("ls-files", "--stage", "-z")
assert head.decode().strip() == INPUTS["head"]
assert hashlib.sha256(index).hexdigest() == INPUTS["index_diff_sha256"]
assert hashlib.sha256(index_entries).hexdigest() == INPUTS["index_entries_sha256"]
staged_paths = [n.decode() for n in git("diff", "--cached", "--name-only", "-z").split(b"\0") if n]
assert len(staged_paths) == INPUTS["staged_paths"]
assert all(n.startswith("artifacts/") and HERE not in (ROOT / n).parents for n in staged_paths)
before = {n: (ROOT / n).read_bytes() for n in SOURCES}
for n, data in before.items():
    assert data == (HERE / "original" / n).read_bytes(), n
fixed_pins = {n: sha(ROOT / n) for n in git("diff", "--name-only").decode().splitlines()
              if n.startswith(("layout/", "dom/", "servo/")) and n not in SOURCES}
assert fixed_pins == INPUTS["fixed_native_pins"]
oracle = json.loads((HERE / "ORACLE.json").read_text())
oracle_rows = {(r["test"], r["subtest"]): (r["status"], r.get("expected", r["status"])) for r in oracle["rows"]}
assert len(oracle_rows) == len(oracle["rows"]) == 74
assert len(oracle["ends"]) == len(TESTS) == 23
assert oracle["exit"] == 1
assert sum(v[0] == "PASS" for v in oracle_rows.values()) == 70
assert sum(v[0] == "FAIL" for v in oracle_rows.values()) == 4
assert sum(v[0] != v[1] for v in oracle_rows.values()) == 2
if sys.argv[1:] == ["--preflight"]:
    print(json.dumps({"preflight": "PASS", "staged_paths": len(staged_paths),
                      "sources": len(SOURCES), "oracle_rows": len(oracle_rows),
                      "mutations_or_builds": False}))
    raise SystemExit(0)

for n, data in before.items():
    target = HERE / "source-before" / n
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
save("BEFORE.json", {"head": head.decode().strip(), "sources": {n: sha(ROOT / n) for n in SOURCES},
                     "fixed_native_pins": fixed_pins,
                     "index_diff_sha256": hashlib.sha256(index).hexdigest(),
                     "index_entries_sha256": hashlib.sha256(index_entries).hexdigest()})
state = {"status": "starting", "accepted": False, "variant": "v4-without-fix102"}
save("STATE.json", state)
changed = False
try:
    for target, origin in INSTALL.items():
        (ROOT / target).write_bytes((HERE / origin).read_bytes())
    state["wpt_lint_exit"] = command("wpt-lint", ["./mach", "lint", "-l", "wpt", *INSTALL])
    assert state["wpt_lint_exit"] == 0
    for n in SOURCES:
        changed = True
        (ROOT / n).write_bytes((HERE / "candidate" / n).read_bytes())
    state["format_check_exit"] = command("format-check", ["./mach", "lint", "-W", "-l", "clang-format", *SOURCES])
    assert state["format_check_exit"] == 0
    assert all((ROOT / n).read_bytes() == (HERE / "candidate" / n).read_bytes() for n in SOURCES)
    state["status"] = "building standalone candidate"
    save("STATE.json", state)
    state["candidate_build_exit"] = command("candidate-build", ["./mach", "build", "binaries"])
    assert state["candidate_build_exit"] == 0
    assert all((ROOT / n).read_bytes() == (HERE / "candidate" / n).read_bytes() for n in SOURCES)
    state["status"] = "testing standalone candidate"
    save("STATE.json", state)
    state["candidate"] = test_run("standalone")
    run = json.loads((HERE / "standalone/RUN.json").read_text())
    assert result_map("standalone") == oracle_rows, "Standalone keyed outcomes differ from integer-only oracle"
    assert end_map(run) == end_map(oracle), "Standalone file outcomes differ from integer-only oracle"
    assert run["exit"] == oracle["exit"], "Standalone exit differs from expected-failure oracle"
    state["exact_oracle_match"] = True
except BaseException as error:
    state["failure"] = {"type": type(error).__name__, "message": str(error)}
    raise
finally:
    state["status"] = "restoring"
    save("STATE.json", state)
    for n, content in before.items():
        if not (ROOT / n).exists() or (ROOT / n).read_bytes() != content:
            (ROOT / n).write_bytes(content)
    for target in INSTALL:
        (ROOT / target).unlink(missing_ok=True)
    if changed:
        state["restore_build_exit"] = command("restore-build", ["./mach", "build", "binaries"])
    final = {"head": git("rev-parse", "HEAD").decode().strip(),
             "index_diff_sha256": hashlib.sha256(git("diff", "--cached", "--binary")).hexdigest(),
             "index_entries_sha256": hashlib.sha256(git("ls-files", "--stage", "-z")).hexdigest(),
             "sources": {n: sha(ROOT / n) for n in SOURCES},
             "fixed_native_pins": {n: sha(ROOT / n) for n in fixed_pins},
             "temporary_tests_absent": all(not (ROOT / n).exists() for n in INSTALL)}
    save("FINAL.json", final)
    state["source_restored"] = final["sources"] == {n: hashlib.sha256(data).hexdigest() for n, data in before.items()} and final["temporary_tests_absent"]
    state["other_native_unchanged"] = final["fixed_native_pins"] == fixed_pins
    state["head_unchanged"] = final["head"] == INPUTS["head"]
    state["index_unchanged"] = final["index_diff_sha256"] == INPUTS["index_diff_sha256"] and final["index_entries_sha256"] == INPUTS["index_entries_sha256"]
    state["status"] = "terminal-failed" if "failure" in state else "restored"
    save("STATE.json", state)
    assert not changed or state["restore_build_exit"] == 0
    assert all(state[k] for k in ["source_restored", "other_native_unchanged", "head_unchanged", "index_unchanged"])
    save("RESTORED.json", {**final["sources"], **final["fixed_native_pins"]})
state["status"] = "terminal"
save("STATE.json", state)
print(json.dumps(state, indent=2))


