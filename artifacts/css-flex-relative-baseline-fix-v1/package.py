import difflib
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
GIT = ["git", "-c", "core.fsmonitor=false"]
CPP = "layout/generic/nsFlexContainerFrame.cpp"
WPT = "testing/web-platform/tests/css/css-flexbox/flexbox-relative-item-exported-baseline.html"


def get(*args):
    return subprocess.check_output(GIT + list(args), cwd=ROOT)


def sha(data):
    return hashlib.sha256(data).hexdigest()


head = get("rev-parse", "HEAD").decode().strip()
index = Path(get("rev-parse", "--git-path", "index").decode().strip())
if not index.is_absolute():
    index = ROOT / index
index_pin = sha(index.read_bytes())
candidate = (HERE / "candidate.cpp").read_bytes()
assert (ROOT / CPP).read_bytes() == candidate
test = (ROOT / WPT).read_bytes()
patch_path = HERE / "fix-candidate-v1.patch"
patch = patch_path.read_text()
checks = []
for base in [head, "976279105b2e78b8666a959eb3f25c9176cefaf8"]:
    original = get("show", base + ":" + CPP)
    with tempfile.TemporaryDirectory(prefix="flex-relative-baseline-package-") as temporary:
        work = Path(temporary)
        source = work / CPP
        source.parent.mkdir(parents=True)
        source.write_bytes(original)
        for args in [["--check"], []]:
            subprocess.run(GIT + ["apply", *args, str(patch_path)], cwd=work, check=True)
        assert (work / WPT).read_bytes() == test
        paths = sorted(str(p.relative_to(work)) for p in work.rglob("*") if p.is_file())
        assert paths == sorted([CPP, WPT])
        after = source.read_bytes()
        (HERE / ("standalone-" + base[:12] + ".cpp")).write_bytes(after)
        subprocess.run(GIT + ["apply", "--reverse", str(patch_path)], cwd=work, check=True)
        assert source.read_bytes() == original and not (work / WPT).exists()
        checks.append({"base": base, "before_sha256": sha(original),
                       "after_sha256": sha(after), "apply_reverse": True, "paths": paths})
assert get("rev-parse", "HEAD").decode().strip() == head
assert sha(index.read_bytes()) == index_pin
assert (ROOT / CPP).read_bytes() == candidate and (ROOT / WPT).read_bytes() == test
record = {"patch_sha256": sha(patch.encode()), "candidate_sha256": sha(candidate),
          "wpt_sha256": sha(test), "checks": checks,
          "head_index_worktree_preserved": True,
          "scope": "Relative-position baseline repair and WPT apply independently to both retained bases. The standalone patch changes two preexisting consumers; shared testing also changes the new natural-donor helper, which will be packaged in the independent natural-donor fix. No isolated upstream build or full baseline/provider correctness theorem is claimed."}
(HERE / "PACKAGING.json").write_text(json.dumps(record, indent=2) + "\n")
print(json.dumps(record, indent=2))
