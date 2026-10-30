import difflib, hashlib, json, subprocess, tempfile
from pathlib import Path
HERE = Path(__file__).resolve().parent
sha = lambda b: hashlib.sha256(b).hexdigest()
def diff(a, b, left, right):
    return "".join(difflib.unified_diff(a.splitlines(True), b.splitlines(True), fromfile=left, tofile=right))
command = ["/Users/bgrins/.mozbuild/clang/bin/clang-format", "--style=file", "--assume-filename=/Users/bgrins/code/firefox/dom/base/nsLineBreaker.cpp"]
raw = (HERE / "unformatted.cpp").read_bytes()
candidate = subprocess.run(command, input=raw, capture_output=True, check=True).stdout
assert subprocess.run(command, input=candidate, capture_output=True, check=True).stdout == candidate
(HERE / "candidate.cpp").write_bytes(candidate)
(HERE / "INPUT-CORRECTION.patch").write_text(diff((HERE / "reviewed-input.cpp").read_text(), raw.decode(), "reviewed-input.cpp", "unformatted.cpp"))
format_delta = diff(raw.decode(), candidate.decode(), "unformatted.cpp", "candidate.cpp")
(HERE / "FORMAT-DELTA.patch").write_text(format_delta)
(HERE / "FORMAT-REPLACEMENTS.xml").write_bytes(subprocess.run(command + ["--output-replacements-xml"], input=candidate, capture_output=True, check=True).stdout)
patch = diff((HERE / "original.cpp").read_text(), candidate.decode(), "a/dom/base/nsLineBreaker.cpp", "b/dom/base/nsLineBreaker.cpp")
for file in sorted((HERE / "tests").rglob("*.html")):
    patch += diff("", file.read_text(), "/dev/null", "b/testing/web-platform/tests/" + str(file.relative_to(HERE / "tests")))
(HERE / "fix.patch").write_text(patch)
with tempfile.TemporaryDirectory(prefix="language-patch-") as tmp:
    root = Path(tmp)
    target = root / "dom/base/nsLineBreaker.cpp"
    target.parent.mkdir(parents=True)
    target.write_bytes((HERE / "original.cpp").read_bytes())
    logs = []
    for reverse in (False, True):
        result = subprocess.run(["patch", "--batch", "--fuzz=0", "-p1"] + (["-R"] if reverse else []), input=patch.encode(), cwd=root, capture_output=True, check=True)
        log = result.stdout.decode() + result.stderr.decode()
        assert "offset" not in log and "fuzz" not in log
        logs.append(log)
        assert target.read_bytes() == ((HERE / "original.cpp").read_bytes() if reverse else candidate)
        for file in (HERE / "tests").rglob("*.html"):
            destination = root / "testing/web-platform/tests" / file.relative_to(HERE / "tests")
            assert (not destination.exists()) if reverse else destination.read_bytes() == file.read_bytes()
assert not root.exists()
result = json.loads((HERE / "REVIEWED-INPUT-FORMAT.json").read_text())
result.update(unformatted_sha256=sha(raw), candidate_sha256=sha(candidate), patch_sha256=sha(patch.encode()), format_delta_bytes=len(format_delta.encode()), reviewed_input_sha256=sha((HERE / "reviewed-input.cpp").read_bytes()), semantic_correction="Keep failed locale parsing distinct from valid false; clear stale script but do not commit the invalid buffered language atom.")
(HERE / "FORMAT.json").write_text(json.dumps(result, indent=2) + "\n")
(HERE / "PATCH-CHECK.json").write_text(json.dumps(dict(forward_reverse_zero_fuzz=True, logs=logs, scratch_removed=str(root), scratch_absent=True, files=3, candidate_sha256=sha(candidate), patch_sha256=sha(patch.encode())), indent=2) + "\n")
print(json.dumps(result))
