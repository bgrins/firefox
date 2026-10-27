import ast
import difflib
import hashlib
import json
from pathlib import Path
import re
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


for name, expected in json.loads((HERE / "REFERENCES.json").read_text()).items():
    assert digest(ROOT / name) == expected, name
source = json.loads((HERE / "SOURCE.json").read_text())
original = (HERE / "original/dom/base/Element.h").read_text()
candidate = (HERE / "candidate/dom/base/Element.h").read_text()
for role in ["original", "candidate"]:
    assert digest(HERE / role / "dom/base/Element.h") == source["files"]["dom/base/Element.h"][role]
helper = (HERE / "conversion.inc").read_text()
assert candidate.count(helper) == 1
insertion = "  // Client metrics round half ties toward positive infinity.\n" + helper + "\n"
assert candidate.count(insertion) == 1
assert candidate.rfind(" private:", 0, candidate.index(insertion)) > candidate.rfind(" public:", 0, candidate.index(insertion))
reverted = candidate.replace(insertion, "")
for field in ["x", "y", "Width()", "Height()"]:
    new = f"AppUnitsToClientCSSPixels(GetClientAreaRect().{field})"
    old = f"CSSPixel::FromAppUnits(GetClientAreaRect().{field}).Rounded()"
    assert reverted.count(new) == 1
    reverted = reverted.replace(new, old)
assert reverted == original
assert candidate.count("AppUnitsToClientCSSPixels(") == 5
patch = "".join(difflib.unified_diff(original.splitlines(True), candidate.splitlines(True), fromfile="a/dom/base/Element.h", tofile="b/dom/base/Element.h"))
assert (HERE / "native.patch").read_text() == patch
test_path = "testing/web-platform/tests/css/cssom-view/client-size-integer-precision.html"
wpt_patch = "".join(difflib.unified_diff([], (HERE / "client-size-integer-precision.html").read_text().splitlines(True), fromfile="/dev/null", tofile="b/" + test_path))
assert (HERE / "gecko-wpt.patch").read_text() == patch + wpt_patch
accepted112 = (ROOT / "artifacts/css-cssom-offset-scroll-acceptance-v1/gecko-wpt.patch").read_bytes()
combined = (HERE / "combined-112-client-gecko-wpt.patch").read_bytes()
assert combined == accepted112 + (patch + wpt_patch).encode()
assert sorted(re.findall(rb"^\+\+\+ b/(.*)$", combined, re.M)) == sorted([
    b"dom/base/Element.cpp", b"dom/base/Element.h",
    b"testing/web-platform/tests/css/cssom-view/offset-scroll-integer-precision.html",
    test_path.encode()])
assert "#include \"Units.h\"" in original and "#include <cstdint>" in original
assert not (HERE / "candidate/dom/base/Element.cpp").exists()
javascript = "\n".join(re.findall(r"<script(?: [^>]*)?>(.*?)</script>", (HERE / "client-size-integer-precision.html").read_text(), re.S))
assert not any(name in javascript for name in ["offsetWidth", "offsetHeight", "scrollWidth", "scrollHeight", "getBoundingClientRect", "clientLeft", "clientTop"])
syntax = subprocess.run(["node", "--check"], input=javascript, text=True, capture_output=True)
assert syntax.returncode == 0, syntax.stderr
registration = "const names=[];function test(body,name){names.push(name);}\n" + javascript + "\nprocess.stdout.write(JSON.stringify(names));"
registered = subprocess.run(["node", "-"], input=registration, text=True, capture_output=True)
assert registered.returncode == 0, registered.stderr
names = json.loads(registered.stdout)
expected = [f"{observer}-{base}-{extra}" for observer in ["clientWidth", "clientHeight"] for base in [16, 16777200] for extra in [0, 17]]
assert names == expected and len(set(names)) == 8
(HERE / "ROSTER.json").write_text(json.dumps(names, indent=2) + "\n")
model = (ROOT / "artifacts/css-cssom-client-rounding-model-v1/ClientRounding.lean").read_text()
assert "def biased (a : Int) : Int := a + if a ≥ 0 then 30 else -29" in model
assert len(re.findall(r"^theorem ", model, re.M)) == 14
assert "const int64_t bias = aCoord >= 0 ? scale / 2 : 1 - scale / 2;" in helper
assert "int64_t(aCoord) + bias" in helper
# Check textual applicability to the retained upstream header without a Git index.
upstream = "976279105b2e"
upstream_header = subprocess.check_output(["git", "--no-optional-locks", "show", upstream + ":dom/base/Element.h"], cwd=ROOT).decode()
updated = upstream_header
for field in ["x", "y", "Width()", "Height()"]:
    old = f"CSSPixel::FromAppUnits(GetClientAreaRect().{field}).Rounded()"
    assert updated.count(old) == 1
    updated = updated.replace(old, f"AppUnitsToClientCSSPixels(GetClientAreaRect().{field})")
anchor = "  /**\n   * Get this element's client area rect in app units."
assert updated.count(anchor) == 1
updated = updated.replace(anchor, insertion + anchor)
assert updated.replace(insertion, "").replace("AppUnitsToClientCSSPixels(GetClientAreaRect().x)", "CSSPixel::FromAppUnits(GetClientAreaRect().x).Rounded()").replace("AppUnitsToClientCSSPixels(GetClientAreaRect().y)", "CSSPixel::FromAppUnits(GetClientAreaRect().y).Rounded()").replace("AppUnitsToClientCSSPixels(GetClientAreaRect().Width())", "CSSPixel::FromAppUnits(GetClientAreaRect().Width()).Rounded()").replace("AppUnitsToClientCSSPixels(GetClientAreaRect().Height())", "CSSPixel::FromAppUnits(GetClientAreaRect().Height()).Rounded()") == upstream_header
result = {
    "status": "PASS_ARTIFACT_ONLY",
    "native_reconstruction_exact": True,
    "private_helper": True,
    "inline_getter_and_script_annotations_preserved": True,
    "client_getters_changed": 4,
    "observed_large_getters": ["ClientWidth", "ClientHeight"],
    "existing_lean_theorems_reused": 14,
    "new_lean_theorems": 0,
    "standalone_patch_native_and_own_wpt_only": True,
    "composed_patch_exact_accepted112_prefix_plus_client": True,
    "wpt_registered_names": names,
    "javascript_syntax_exit": syntax.returncode,
    "inert_registration_exit": registered.returncode,
    "upstream_revision": subprocess.check_output(["git", "--no-optional-locks", "rev-parse", upstream], cwd=ROOT).decode().strip(),
    "upstream_original_sha256": hashlib.sha256(upstream_header.encode()).hexdigest(),
    "upstream_candidate_sha256": hashlib.sha256(updated.encode()).hexdigest(),
    "upstream_unique_textual_applicability_and_reversal": True,
    "native_compiled": False,
    "browser_executed": False,
    "main_index_mutation": False,
}
(HERE / "CHECK.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result))
