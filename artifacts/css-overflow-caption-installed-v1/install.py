import hashlib
import json
import os
from html.parser import HTMLParser
from pathlib import Path
import subprocess
from urllib.parse import unquote, urlsplit

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = ROOT / "layout/generic/nsFlexContainerFrame.cpp"
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



patches = [ROOT / "artifacts/css-overflow-relative-position-format-v1/formatted-proposal.patch", ROOT / "artifacts/css-flex-table-caption-commit-v1/stack.patch"]
paths = ["layout/generic/nsContainerFrame.cpp", "layout/generic/nsFlexContainerFrame.cpp", *TESTS[:2]]
expected = {
 "layout/generic/nsContainerFrame.cpp": "1c89576b44909a4773901aeb00121a04b420e7152e360a21a8b6067ee552ae6a",
 "layout/generic/nsFlexContainerFrame.cpp": "dd8bf5333aca62588f3960c11a0a18763e26b815fcf101c283acecd492436105",
 "testing/web-platform/tests/css/css-break/relative-position-overflow-continuations.html": "f343069aefdd630657da02c84518f538d12773e4a938fc1c3b2c93770e7ce560",
 "testing/web-platform/tests/css/css-flexbox/table-caption-percentage-height-resize.html": "a21a6559b1bda44aa1ae81681213d4f87fd9375479767910f4e2777ec7e6d47b",
}
assert all(not (ROOT/n).exists() for n in TESTS[:2])
head=git("rev-parse","HEAD");index=git("diff","--cached","--binary")
assert hashlib.sha256(index).hexdigest()=="238aa7d1068214361d145013b994072a9cb4cd0a5661688cf554b95d75dcb25f"
before={n:(ROOT/n).read_bytes() if (ROOT/n).exists() else None for n in paths}
for n,data in before.items():
 if data is not None:
  dst=HERE/"before"/n;dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(data)
state={"status":"installing", "installed":False, "head":head.decode().strip(), "index_diff_sha256":hashlib.sha256(index).hexdigest()}
save("STATE.json",state)
try:
 for patch in patches:
  git("apply","--check",str(patch));git("apply",str(patch))
 for n,h in expected.items():assert sha(ROOT/n)==h,n
 state["status"]="building";save("STATE.json",state)
 state["build_exit"]=command("installed-build",["./mach","build","binaries"])
 assert state["build_exit"]==0
 state["status"]="testing";save("STATE.json",state)
 state["wpt"]=test_run("installed")
 assert state["wpt"]["exit"]==0
 state["installed"]=True
except BaseException:
 state["status"]="restoring after failure";save("STATE.json",state)
 for n,data in before.items():
  if data is None:(ROOT/n).unlink(missing_ok=True)
  else:(ROOT/n).write_bytes(data)
 state["restore_build_exit"]=command("restore-build",["./mach","build","binaries"])
 raise
finally:
 state["status"]="terminal"
 state["head_unchanged"]=git("rev-parse","HEAD")==head
 state["index_unchanged"]=git("diff","--cached","--binary")==index
 state["installed_pins"]={n:sha(ROOT/n) if (ROOT/n).exists() else None for n in paths}
 save("STATE.json",state)
print(json.dumps(state,indent=2))
assert state["head_unchanged"] and state["index_unchanged"]
