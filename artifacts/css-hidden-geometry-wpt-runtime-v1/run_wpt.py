import hashlib
import json
import os
from html.parser import HTMLParser
from pathlib import Path
import subprocess
from urllib.parse import unquote, urlsplit

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CONFIG = json.loads((HERE / "CONFIG.json").read_text())
TESTS = CONFIG["tests"]
INSTALL = CONFIG["install"]
SOURCES = CONFIG["sources"]
SOURCE = ROOT / "layout/generic/nsFlexContainerFrame.cpp"
ENV = dict(os.environ, MOZ_SKIP_PATH_PERFORMANCE_CHECK="1", GIT_OPTIONAL_LOCKS="0",
           GIT_CONFIG_COUNT="1", GIT_CONFIG_KEY_0="core.fsmonitor", GIT_CONFIG_VALUE_0="false")
ENV.pop("MOZ_LOG", None)
GIT = ["git", "-c", "core.fsmonitor=false"]

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

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
    paths = set(TESTS + CONFIG["guard_sources"] + CONFIG["support_paths"] + list(INSTALL) + ["dom/base/DOMRect.cpp", str(SOURCE.relative_to(ROOT)),
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
    complete = (code in (0, 1) and len(ends) == len(TESTS) and {r["test"] for r in ends} == expected
                and len({(r["test"], r["subtest"]) for r in rows}) == len(rows)
                and all(r["test"] in expected and r["status"] in ("PASS", "FAIL") for r in rows)
                and all(r["status"] in ("OK", "PASS", "FAIL") for r in ends)
                and sum(r.get("action") == "suite_end" for r in events) == 1)
    result = {"exit": code, "complete": complete, "before": before, "after": pins(),
              "rows": rows, "ends": ends}
    (directory / "RUN.json").write_text(json.dumps(result, indent=2) + "\n")
    assert complete and before == result["after"]
    return {"exit": code, "complete": complete, "subtests": len(rows), "files": len(ends)}


