import difflib, hashlib, json, subprocess, tempfile
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sha = lambda b: hashlib.sha256(b).hexdigest()
def diff(a, b, left, right):
    return "".join(difflib.unified_diff(a.splitlines(True), b.splitlines(True), fromfile=left, tofile=right))
formatter = "/Users/bgrins/.mozbuild/clang/bin/clang-format"
rows = []
patch = ""
format_delta = ""
for file in sorted((HERE / "base").rglob("*")):
    if not file.is_file():
        continue
    relative = str(file.relative_to(HERE / "base"))
    command = [formatter, "--style=file", "--assume-filename=" + str(ROOT / relative)]
    raw = (HERE / "unformatted" / relative).read_bytes()
    candidate = subprocess.run(command, input=raw, capture_output=True, check=True).stdout
    assert subprocess.run(command, input=candidate, capture_output=True, check=True).stdout == candidate
    (HERE / "candidate" / relative).write_bytes(candidate)
    xml = subprocess.run(command + ["--output-replacements-xml"], input=candidate, capture_output=True, check=True).stdout
    assert b"incomplete_format='false'" in xml and b"<replacement " not in xml
    (HERE / (Path(relative).name + ".format.xml")).write_bytes(xml)
    format_delta += diff(raw.decode(), candidate.decode(), "unformatted/" + relative, "candidate/" + relative)
    patch += diff(file.read_text(), candidate.decode(), "a/" + relative, "b/" + relative)
    rows.append(dict(path=relative, base_sha256=sha(file.read_bytes()), candidate_sha256=sha(candidate), unformatted_sha256=sha(raw), format_changed=candidate != raw))
for file in sorted((HERE / "tests").rglob("*.html")):
    patch += diff("", file.read_text(), "/dev/null", "b/testing/web-platform/tests/" + str(file.relative_to(HERE / "tests")))
(HERE / "fix.patch").write_text(patch)
(HERE / "FORMAT-DELTA.patch").write_text(format_delta)
with tempfile.TemporaryDirectory(prefix="hyphenation-patch-") as tmp:
    root = Path(tmp)
    for row in rows:
        target = root / row['path']
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((HERE / "base" / row['path']).read_bytes())
    logs = []
    for reverse in (False, True):
        result = subprocess.run(["patch", "--batch", "--fuzz=0", "-p1"] + (["-R"] if reverse else []), input=patch.encode(), cwd=root, capture_output=True, check=True)
        log = result.stdout.decode() + result.stderr.decode()
        assert "offset" not in log and "fuzz" not in log
        logs.append(log)
        for row in rows:
            assert (root / row['path']).read_bytes() == (HERE / ("base" if reverse else "candidate") / row['path']).read_bytes()
        for file in (HERE / "tests").rglob("*.html"):
            destination = root / "testing/web-platform/tests" / file.relative_to(HERE / "tests")
            assert (not destination.exists()) if reverse else destination.read_bytes() == file.read_bytes()
assert not root.exists()
result = dict(formatter=formatter, version=subprocess.run([formatter,"--version"],capture_output=True,text=True,check=True).stdout.strip(), files=rows, patch_sha256=sha(patch.encode()), format_delta_bytes=len(format_delta.encode()), idempotent=True, incomplete_format=False, forward_reverse_zero_fuzz_zero_offset=True, scratch_removed=True, logs=logs)
(HERE / "FORMAT.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result))
