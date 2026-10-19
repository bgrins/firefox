#!/usr/bin/env python3
"""Check frozen source proposal and historical evidence without a native build."""
import argparse
from collections import Counter
import difflib
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parent
FILES = [
    "servo/components/style/properties_and_values/value.rs",
    "servo/ports/geckolib/glue.rs",
    "dom/animation/KeyframeEffect.cpp",
]
MAP = "servo/components/style/custom_properties_map.rs"
TEST = "testing/web-platform/tests/css/css-values/animation-csswide-equal-payload-taint.html"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def delta(original, candidate, name):
    return "".join(difflib.unified_diff(original.splitlines(True), candidate.splitlines(True),
                                     fromfile="a/" + name, tofile="b/" + name))


def run(args, **kw):
    result = subprocess.run(args, text=True, capture_output=True, **kw)
    assert result.returncode == 0, (args, result.stdout, result.stderr)
    return result.stdout


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--checks", action="store_true")
    args = parser.parse_args()
    freeze = json.loads((ROOT / "FREEZE.json").read_text())
    assert sha(ROOT / "MANIFEST.json") == freeze["manifest_sha256"]
    manifest = json.loads((ROOT / "MANIFEST.json").read_text())
    actual = {str(p.relative_to(ROOT)) for p in ROOT.rglob("*") if p.is_file()}
    assert actual == set(manifest) | {"MANIFEST.json", "FREEZE.json"}
    for name, digest in manifest.items():
        path = Path(name)
        assert not path.is_absolute() and ".." not in path.parts
        assert sha(ROOT / path) == digest, name
    expected = "".join(delta((ROOT / "source/original" / f).read_text(),
                             (ROOT / "source/candidate" / f).read_text(), f) for f in FILES)
    assert expected == (ROOT / "native.patch").read_text()
    source = (ROOT / "source/upstream" / MAP).read_text()
    old = "        if self.get(name) == value.as_ref() {"
    new = "        if can_deduplicate_values(self.get(name), value.as_ref()) {"
    assert source.count(old) == 1
    support = delta(source, source.replace(old, new), MAP)
    assert support == (ROOT / "prerequisite-map-support.patch").read_text()
    assert expected + support == (ROOT / "standalone-native.patch").read_text()
    test = (ROOT / "csswide-endpoint-taint.html").read_text()
    test_delta = "".join(difflib.unified_diff([], test.splitlines(True),
                                              fromfile="/dev/null", tofile="b/" + TEST))
    assert expected + test_delta == (ROOT / "stack-with-test.patch").read_text()
    assert expected + support + test_delta == (ROOT / "standalone-with-test.patch").read_text()
    raw = [json.loads(line) for line in (ROOT / "evidence/original-six-raw.json").read_text().splitlines() if line.strip()]
    rows = [row for row in raw if row.get("action") == "test_status"]
    assert Counter(row["status"] for row in rows) == {"FAIL": 2, "PASS": 4}
    assert len({(row["test"], row["subtest"]) for row in rows}) == 6
    for row in rows:
        if row["status"] == "FAIL":
            assert "same payload" in row["subtest"]
            assert "Updated effect URL taint" in row["message"]
    ends = [row for row in raw if row.get("action") == "test_end"]
    assert len(ends) == 1 and ends[0]["status"] == "OK"
    receipt = json.loads((ROOT / "evidence/original-six-RUN.json").read_text())
    assert receipt["stable_after"] and receipt["rows"] == rows
    applications = []
    if args.checks:
        for name in ["csswide-endpoint-taint.html", "typed-endpoint-taint.html"]:
            script = (ROOT / name).read_text().split("<script>")[1].split("</script>")[0]
            run(["node", "--check", "--input-type=commonjs"], input=script)
        for variant, patch, names, target in [
            ("original", "native.patch", FILES, "candidate"),
            ("upstream", "native.patch", FILES, None),
            ("upstream", "standalone-with-test.patch", FILES + [MAP], "standalone"),
        ]:
            with tempfile.TemporaryDirectory(prefix="animation-taint-source-") as temporary:
                directory = Path(temporary)
                for name in names:
                    dest = directory / name
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(ROOT / "source" / variant / name, dest)
                command = ["patch", "--batch", "--fuzz=0", "-p1", "-i", str(ROOT / patch)]
                forward = run(command, cwd=directory)
                if target:
                    for name in names:
                        assert (directory / name).read_bytes() == (ROOT / "source" / target / name).read_bytes()
                if patch == "standalone-with-test.patch":
                    assert (directory / TEST).read_text() == test
                backward = run(command + ["-R"], cwd=directory)
                for name in names:
                    assert (directory / name).read_bytes() == (ROOT / "source" / variant / name).read_bytes()
                if patch == "standalone-with-test.patch":
                    assert not (directory / TEST).exists()
                applications.append({"variant": variant, "patch": patch,
                                     "apply": forward, "reverse": backward})
    print(json.dumps({"status": "PASS", "inputs": len(manifest), "applications": applications,
                      "historical_browser": "2 FAIL / 4 PASS; harness OK",
                      "candidate_compile": "NOT_RUN", "candidate_browser": "NOT_RUN"}, indent=2))


if __name__ == "__main__":
    main()
