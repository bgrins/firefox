import hashlib
import json
import os
from html.parser import HTMLParser
from pathlib import Path
import subprocess
from urllib.parse import unquote, urlsplit

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PROPOSAL = ROOT / "artifacts/css-exact-size-observer-repair-proposal-v1"
SOURCE = ROOT / "layout/base/nsLayoutUtils.cpp"
SOURCES = ["layout/base/nsLayoutUtils.cpp", "dom/base/DOMRect.cpp"]
TESTS = json.loads((HERE / "TESTS.json").read_text())
NEW_TEST = ROOT / TESTS[0]
INSTALL = {TESTS[0]: NEW_TEST.name}
GIT = ["git", "-c", "core.fsmonitor=false"]
ENV = {**os.environ, "MOZ_SKIP_PATH_PERFORMANCE_CHECK": "1"}


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
    paths = set(TESTS + SOURCES + list(INSTALL) + [str(SOURCE.relative_to(ROOT)),
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


assert not NEW_TEST.exists()
assert not (HERE / "BEFORE.json").exists()
before = {n: (ROOT / n).read_bytes() for n in SOURCES}
for n in SOURCES:
    assert before[n] == (PROPOSAL / "original" / Path(n).name).read_bytes(), n
head = git("rev-parse", "HEAD")
index = git("diff", "--cached", "--binary")
assert head.decode().strip() == "9c6b4af2a64296b2b24a162879907d4b2c439026"
assert not index
restored = json.loads((ROOT / "artifacts/css-exact-size-supplement-runtime-v1/RESTORED.json").read_text())
for name, pin in restored.items():
    assert sha(ROOT / name) == pin, name
for n, data in before.items():
    p = HERE / "source-before" / n
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(data)
save("BEFORE.json", {"head": head.decode().strip(), "sources": {n: sha(ROOT / n) for n in SOURCES}, "restored_baseline_pins": restored, "index_diff_sha256": hashlib.sha256(index).hexdigest(), "proposal_manifest_sha256": sha(PROPOSAL / "FILES.json")})
state = {"status": "baseline", "accepted": False, "variants": {}}
save("STATE.json", state)
changed = False
try:
    NEW_TEST.write_bytes((HERE / NEW_TEST.name).read_bytes())
    for kind, changes in [("baseline", []), ("dom-only", ["dom/base/DOMRect.cpp"]), ("both", SOURCES), ("integer-only", ["layout/base/nsLayoutUtils.cpp"])]:
        state["status"] = kind
        save("STATE.json", state)
        if kind != "baseline":
            for n in SOURCES:
                target = ROOT / n
                content = (PROPOSAL / "candidate" / Path(n).name).read_bytes() if n in changes else before[n]
                if target.read_bytes() != content:
                    target.write_bytes(content)
            changed = True
            for n in SOURCES:
                p = HERE / ("source-" + kind) / n
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_bytes((ROOT / n).read_bytes())
            state["status"] = "building " + kind
            save("STATE.json", state)
            state[kind + "_build_exit"] = command(kind + "-build", ["./mach", "build", "binaries"])
            assert state[kind + "_build_exit"] == 0
        state["status"] = "testing " + kind
        save("STATE.json", state)
        observed = command(kind + "-probe-driver", ["python3", "-I", "-S", "-B", str(HERE / "run_browser.py"), kind + "-probe", "", "56"])
        assert observed == 0
        state["variants"][kind] = test_run(kind)
        run = json.loads((HERE / kind / "RUN.json").read_text())
        new_id = "/" + str(NEW_TEST.relative_to(ROOT / "testing/web-platform/tests"))
        assert len([r for r in run["rows"] if r["test"] == new_id]) == 28
        save("STATE.json", state)
finally:
    state["status"] = "restoring"
    save("STATE.json", state)
    for n, content in before.items():
        if (ROOT / n).read_bytes() != content:
            (ROOT / n).write_bytes(content)
    NEW_TEST.unlink(missing_ok=True)
    if changed:
        state["restore_build_exit"] = command("restore-build", ["./mach", "build", "binaries"])
    state["source_restored"] = all((ROOT / n).read_bytes() == content for n, content in before.items()) and not NEW_TEST.exists()
    state["head_unchanged"] = git("rev-parse", "HEAD") == head
    state["index_unchanged"] = git("diff", "--cached", "--binary") == index
    state["status"] = "terminal"
    save("STATE.json", state)
    save("RESTORED.json", {n: sha(ROOT / n) for n in restored})
    print(json.dumps(state, indent=2))
    assert not changed or state["restore_build_exit"] == 0
    assert all(state[k] for k in ["source_restored", "head_unchanged", "index_unchanged"])
