import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit("Require python3 -I -S without optimization")
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RUNTIME = ROOT / "artifacts/css-hidden-query-landing-runtime-v1"
OVERLAY = ROOT / "artifacts/css-hidden-query-worktree-overlay-v1"
ACCEPTANCE = ROOT / "artifacts/css-hidden-query-landing-acceptance-v1/ACCEPTANCE.json"

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def need(ok, why):
    if not ok:
        raise RuntimeError(why)

need(not (HERE / "INSTALLATION.json").exists(), "already installed")
a = json.loads(ACCEPTANCE.read_text())
need(a["status"] == "ACCEPTED_BOUNDED_NATIVE_REPAIRS", "acceptance required")
need(sha(RUNTIME / "FILES.json") == a["runtime_files_sha256"], "runtime manifest changed")
need(sha(OVERLAY / "FILES.json") == "88291d7b720f4086bddc4c2789020767ea3913cf9ae9dd4d04c7e69abeb81fc1", "overlay seal")
for name, digest in json.loads((OVERLAY / "FILES.json").read_text()).items():
    need(sha(OVERLAY / name) == digest, "overlay payload " + name)
spec = importlib.util.spec_from_file_location("wpt", RUNTIME / "run_wpt.py")
wpt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wpt)
c = wpt.CONFIG
before = json.loads((RUNTIME / "FINAL.json").read_text())
state = json.loads((RUNTIME / "STATE.json").read_text())
need(state["status"] == "terminal" and state["restored"] and state["restore_build_exit"] == 0 and not state["recovery_errors"] and "failure" not in state, "restoration gate")
need(wpt.snapshot() == before, "live sources/index/HEAD differ from restored state")
need(not wpt.git("diff", "--cached", "--name-only"), "index not empty")
need(all(not (ROOT / name).exists() and not (ROOT / name).is_symlink() for name in c["install"]), "test target exists")
recipes = json.loads((OVERLAY / "BINDINGS.json").read_text())["recipes"]
originals = {r["path"]: (ROOT / r["path"]).read_bytes() for r in recipes}
for r in recipes:
    need(sha(ROOT / r["path"]) == r["original_sha256"], "original source changed")
    need(hashlib.sha256(wpt.git("show", "HEAD:" + r["path"])).hexdigest() == r["head_before_sha256"], "HEAD source changed")
    subprocess.run(wpt.GIT + ["apply", "--check", str(OVERLAY / r["overlay_patch"])], cwd=ROOT, env=wpt.ENV, check=True)
installed = []
try:
    for r in recipes:
        subprocess.run(wpt.GIT + ["apply", str(OVERLAY / r["overlay_patch"])], cwd=ROOT, env=wpt.ENV, check=True)
    for name, source in c["install"].items():
        with (ROOT / name).open("xb") as stream:
            installed.append(name)
            stream.write((RUNTIME / source).read_bytes())
    after = wpt.snapshot()
    expected = dict(before["sources"])
    expected.update({r["path"]: r["overlay_sha256"] for r in recipes})
    need(after["sources"] == expected, "source preservation failed")
    need(all(after[k] == before[k] for k in ["head", "index_diff_sha256", "index_entries_sha256"]), "HEAD/index changed")
    resources = json.loads((RUNTIME / "INPUTS.json").read_text())["resource_pins"]
    need(wpt.pins(list(resources)) == resources, "installed tests/resources differ")
except BaseException:
    for name, data in originals.items():
        (ROOT / name).write_bytes(data)
    for name in installed:
        (ROOT / name).unlink()
    raise
(HERE / "INSTALLATION.json").write_text(json.dumps({"before": before, "after": after, "installed_tests": installed, "acceptance_sha256": sha(ACCEPTANCE), "preserved_other_source_bytes": True}, indent=2) + "\n")
print("Installed exact three native overlays and four WPT files; index unchanged")
