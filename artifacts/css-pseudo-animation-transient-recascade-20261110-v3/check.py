#!/usr/bin/env python3
import hashlib, json, re, shutil, subprocess, sys, tempfile, tomllib
from pathlib import Path
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
OUT = HERE / "verification"
OUT.mkdir(exist_ok=True)
def sha(data): return hashlib.sha256(data).hexdigest()
def run(args, **kw):
    r = subprocess.run(args, capture_output=True, **kw)
    if r.returncode: raise RuntimeError((args, r.returncode, r.stdout, r.stderr))
    return r
pins = json.loads((HERE / "SOURCES.json").read_text())
for name, digest in pins["files"].items():
    data = run(["git", "-c", "core.fsmonitor=false", "show", pins["revision"] + ":" + name], cwd=ROOT).stdout
    assert sha(data) == digest and data == (HERE / "source" / name).read_bytes()
previous = json.loads((HERE / "PREREQUISITE.json").read_text())
for name, digest in previous["candidate_files"].items():
    data = (ROOT / previous["capsule"] / "candidate" / name).read_bytes()
    assert sha(data) == digest and data == (HERE / "prerequisite" / name).read_bytes()
for name in ("layout/style/ServoStyleSet.cpp", "layout/style/ServoStyleSet.h", "servo/ports/geckolib/glue.rs"):
    assert (HERE / "prerequisite" / name).read_bytes() == (HERE / "source" / name).read_bytes()
roles = json.loads((HERE / "ROLES.json").read_text())
for row in roles:
    assert sha((HERE / "candidate" / row["path"]).read_bytes()) == row["after_sha256"]
    old = HERE / "prerequisite" / row["path"]
    assert (sha(old.read_bytes()) if old.exists() else None) == row["before_sha256"]
with tempfile.TemporaryDirectory(prefix="recascade-source-check-") as temporary:
    tree = Path(temporary)
    shutil.copytree(HERE / "prerequisite", tree, dirs_exist_ok=True)
    run(["patch", "-p1", "--batch", "--forward", "-i", str(HERE / "extension.patch")], cwd=tree)
    for file in (HERE / "candidate").rglob("*"):
        if file.is_file(): assert file.read_bytes() == (tree / file.relative_to(HERE / "candidate")).read_bytes()
    run(["patch", "-R", "-p1", "--batch", "-i", str(HERE / "extension.patch")], cwd=tree)
    for file in (HERE / "prerequisite").rglob("*"):
        if file.is_file(): assert file.read_bytes() == (tree / file.relative_to(HERE / "prerequisite")).read_bytes()
    run(["patch", "-p1", "--batch", "--forward", "-i", str(HERE / "native.patch")], cwd=tree)
    for file in (HERE / "native").rglob("*"):
        if file.is_file(): assert file.read_bytes() == (tree / file.relative_to(HERE / "native")).read_bytes()
    run(["patch", "-p1", "--batch", "--forward", "-i", str(HERE / "driver.patch")], cwd=tree)
    for file in (HERE / "candidate").rglob("*"):
        if file.is_file(): assert file.read_bytes() == (tree / file.relative_to(HERE / "candidate")).read_bytes()
sys.path[:0] = [str(ROOT / "xpcom/idl-parser"), str(ROOT / "third_party/python/ply")]
from xpidl import xpidl
idl = HERE / "candidate/dom/interfaces/base/nsIDOMWindowUtils.idl"
parsed = xpidl.IDLParser().parse(idl.read_text(), filename=str(idl))
interface = next(x for x in parsed.productions if getattr(x, "name", None) == "nsIDOMWindowUtils")
method = [m for m in interface.members if getattr(m, "name", None) == "getMissingPseudoRecascadeForTesting"]
assert len(method) == 1 and len(method[0].params) == 8
manifest = tomllib.loads((HERE / "candidate/dom/base/test/mochitest.toml").read_text())
assert manifest["test_missing_pseudo_animation_recascade.html"] == {}
assert manifest["test_missing_pseudo_animation_query.html"] == {}
html = (HERE / "test_missing_pseudo_animation_recascade.html").read_text()
assert html == (HERE / "candidate/dom/base/test/test_missing_pseudo_animation_recascade.html").read_text()
inventory = run(["node", str(HERE / "inventory.cjs")], text=True, cwd=ROOT).stdout
assert inventory == (HERE / "ASSERTIONS.json").read_text()
assert json.loads(inventory)["assertion_count"] == 100
run(["node", "--check"], input=html.split("<script>")[1].split("</script>")[0], text=True)
for label, args in [
    ("eslint", [str(ROOT / "node_modules/.bin/eslint"), "--stdin", "--stdin-filename", "dom/base/test/test_missing_pseudo_animation_recascade.html", "--rule", "mozilla/import-globals: off"]),
    ("prettier", [str(ROOT / "node_modules/.bin/prettier"), "--stdin-filepath", "dom/base/test/test_missing_pseudo_animation_recascade.html"]),
]:
    r = run(args, input=html, text=True, cwd=ROOT)
    (OUT / (label + ".stdout")).write_text(r.stdout)
    (OUT / (label + ".stderr")).write_text(r.stderr)
    if label == "prettier": assert r.stdout == html
native = (HERE / "recascade.rs").read_text()
for forbidden in ["borrow_data_mut", "process_animations", "resolve_primary_style", "match_primary", "set_primary", "update_animations"]:
    assert forbidden not in native
assert native.count("CascadeOrigin::Animations") == native.count("CascadeOrigin::Transitions") == 1
assert "&mut inputs.visited_rules" in native and "CascadeInputs::new_from_style(base)" in native
assert "cascade_style_and_visited_for_pseudo_with_default_parents" in native
assert native.index("if matches!(pseudo, PseudoElement::Marker)") < native.index("StyleResolverForElement::new(")
assert "compute_pseudo_element_style_with_inputs" in native
amendment = json.loads((HERE / "MARKER-AMENDMENT.json").read_text())
previous_source = ROOT / amendment["previous_capsule"]
assert sha((previous_source / "SOURCE-ONLY.json").read_bytes()) == amendment["previous_source_manifest_sha256"]
for role in roles:
    if role["before_sha256"] is None: continue
    expected = (previous_source / "candidate" / role["path"]).read_text()
    if role["path"] == amendment["path"]:
        assert expected.count(amendment["insertion_before"]) == 1
        expected = expected.replace(amendment["insertion_before"], amendment["insertion"] + amendment["insertion_before"])
    assert expected == (HERE / "candidate" / role["path"]).read_text()
assert (HERE / "test_missing_pseudo_animation_recascade.html").read_bytes() == (previous_source / "test_missing_pseudo_animation_recascade.html").read_bytes()
result = {
    "status": "PASS", "git_source_pins": len(pins["files"]), "prerequisite_files": len(previous["candidate_files"]),
    "changed_or_new_files": len(roles), "patch_forward_reverse_and_split_composition": True,
    "xpidl_syntax_parsed": True, "xpidl_types_resolved": False,
    "manifest_parsed": True, "tasks": 6, "assertions": 100,
    "inert_js_syntax": True, "scoped_eslint": True, "eslint_import_globals_disabled": True,
    "prettier_idempotent": True, "native_build": False, "browser_execution": False,
    "extension_sha256": sha((HERE / "extension.patch").read_bytes()),
    "native_sha256": sha((HERE / "native.patch").read_bytes()),
    "driver_sha256": sha((HERE / "driver.patch").read_bytes()),
}
(OUT / "REPORT.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))
