import hashlib
import json
import os
from html.parser import HTMLParser
from pathlib import Path
import subprocess
from urllib.parse import unquote, urlsplit

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = ROOT / "layout/generic/nsContainerFrame.cpp"
TESTS = json.loads((HERE / "TESTS.json").read_text())
NEW_TEST = ROOT / TESTS[-1]
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
    paths = set(TESTS + [str(SOURCE.relative_to(ROOT)),
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
before = SOURCE.read_bytes()
head = git("rev-parse", "HEAD")
index = git("diff", "--cached", "--binary")
(HERE / "before.cpp").write_bytes(before)
save("BEFORE.json", {"head": head.decode().strip(), "source_sha256": sha(SOURCE),
                     "index_diff_sha256": hashlib.sha256(index).hexdigest()})
state = {"status": "baseline", "accepted": False}
save("STATE.json", state)
try:
    NEW_TEST.write_bytes((HERE / NEW_TEST.name).read_bytes())
    state["baseline"] = test_run("baseline")
    patch = HERE / "native-only.patch"
    git("apply", "--check", str(patch))
    git("apply", str(patch))
    (HERE / "candidate.cpp").write_bytes(SOURCE.read_bytes())
    state["status"] = "building candidate"
    save("STATE.json", state)
    state["candidate_build_exit"] = command("candidate-build", ["./mach", "build", "binaries"])
    if state["candidate_build_exit"] == 0:
        state["status"] = "candidate tests"
        save("STATE.json", state)
        state["candidate"] = test_run("candidate")
finally:
    state["status"] = "restoring"
    save("STATE.json", state)
    if SOURCE.read_bytes() != before:
        SOURCE.write_bytes(before)
    NEW_TEST.unlink(missing_ok=True)
    state["restore_build_exit"] = command("restore-build", ["./mach", "build", "binaries"])
    state["source_restored"] = SOURCE.read_bytes() == before and not NEW_TEST.exists()
    state["head_unchanged"] = git("rev-parse", "HEAD") == head
    state["index_unchanged"] = git("diff", "--cached", "--binary") == index
    state["status"] = "terminal"
    save("STATE.json", state)
    print(json.dumps(state, indent=2))
    assert state["restore_build_exit"] == 0
    assert all(state[k] for k in ["source_restored", "head_unchanged", "index_unchanged"])
