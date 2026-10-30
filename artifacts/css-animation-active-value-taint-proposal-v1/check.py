import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
roles = json.loads((HERE / "SOURCE-ROLES.json").read_text())
clean = json.loads((HERE / "CLEAN-PROVIDER.json").read_text())
edits = json.loads((HERE / "EDITS.json").read_text())
for name, role in roles.items():
    assert sha(ROOT / role["base_capture"]) == role["base_sha256"]
    assert sha(ROOT / role["candidate_capture"]) == role["candidate_sha256"]
    text = (ROOT / role["base_capture"]).read_text()
    for edit in edits:
        if edit["path"] != name:
            continue
        assert text.count(edit["old"]) == edit["count"]
        text = text.replace(edit["old"], edit["new"])
    assert text == (ROOT / role["candidate_capture"]).read_text()
for use_clean in [False, True]:
    inputs = {name: (clean if use_clean and name.endswith("/custom_properties.rs") else role)
              for name, role in roles.items()}
    with tempfile.TemporaryDirectory(prefix="css-active-value-taint-patch-") as tmp:
        scratch = Path(tmp)
        for name, role in inputs.items():
            dest = scratch / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / role["base_capture"], dest)
        for reverse in [False, True]:
            patch = HERE / ("native-clean-provider.patch" if use_clean else "native.patch")
            args = ["patch", "--batch", "-p1", "-i", str(patch)]
            if reverse:
                args.append("-R")
            result = subprocess.run(args, cwd=scratch, capture_output=True, text=True)
            assert result.returncode == 0, result.stdout + result.stderr
            for name, role in inputs.items():
                assert sha(scratch / name) == role["base_sha256" if reverse else "candidate_sha256"]
    assert not scratch.exists()
assert (HERE / "AliasGuard.lean").read_bytes() == (HERE / "lean-run1/AliasGuard.lean").read_bytes()
lean = json.loads((HERE / "lean-run1/CHECK.json").read_text())
assert lean["success"] and lean["false_controls_rejected"] == 3 and lean["scratch_removed"]
print(json.dumps({"source_files": len(roles), "exact_replacements": len(edits),
                  "held_and_clean_provider_patch_forward_reverse": True,
                  "scratch_removed": True, "native_compiled": False,
                  "browser_executed": False, "lean_audits": len(lean["audited_theorems"])}))
