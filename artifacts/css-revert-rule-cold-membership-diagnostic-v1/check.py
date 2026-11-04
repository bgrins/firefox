import difflib
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def run(args, cwd=None):
    result = subprocess.run(args, cwd=cwd, capture_output=True)
    assert result.returncode == 0, (args, result.stdout.decode(), result.stderr.decode())
    return result.stdout


def section(source, start, end):
    return source[source.index(start):source.index(end, source.index(start))]


roles = json.loads((HERE / "SOURCE-ROLES.json").read_text())
references = json.loads((HERE / "REFERENCES.json").read_text())
for path, expected in references.items():
    assert sha((ROOT / path).read_bytes()) == expected, path
patch = ""
for path, role in roles.items():
    a, b = HERE / "base" / path, HERE / "candidate" / path
    assert sha(a.read_bytes()) == role["base_sha256"]
    assert sha(b.read_bytes()) == role["candidate_sha256"]
    patch += "".join(difflib.unified_diff(a.read_text().splitlines(True), b.read_text().splitlines(True), fromfile="a/" + path, tofile="b/" + path))
assert patch == (HERE / "native.patch").read_text()
parent = ROOT / "artifacts/css-rollback-cutoff-e86-rebase-v1"
path = "servo/components/style/properties/cascade.rs"
assert (HERE / "base" / path).read_bytes() == (parent / "candidate" / path).read_bytes()
a, b = (HERE / "base" / path).read_text(), (HERE / "candidate" / path).read_text()
for start, end in [("struct Declaration<'a>", "/// The set of property declarations"), ("fn iter_declarations", "/// NOTE: This function expects"), ("    fn apply_one_prioritary_property(", "    /// Some prioritary properties"), ("    fn apply_non_prioritary_properties(", "    #[cold]"), ("    fn cascade_custom_property(", "    fn ")]:
    if start == "    fn cascade_custom_property(":
        # Locate the next function after this signature.
        sa = a.index(start); sb = b.index(start)
        assert a[sa:a.index(end, sa + len(start))] == b[sb:b.index(end, sb + len(start))]
    else:
        assert section(a, start, end) == section(b, start, end), start
assert "sources: None" in section(b, "    fn new_for_custom_properties_only", "    fn substitute_variables_if_needed")
apply = section(b, "    fn apply_one_longhand(", "    #[inline]\n    unsafe fn do_apply_declaration")
order = ["self.seen.longhands.contains", "priority.flags()", "self.reverted.longhands_set.contains", "!reverted.allows", "self.rule_exclusions.iter()", "let original_declaration = declaration", "self.substitute_variables_if_needed", "tweak_when_ignoring_colors", "self.reverted.longhands_set.insert", "containing_block(original_declaration)", "self.seen.longhands.insert"]
positions = [apply.index(x) for x in order]
assert positions == sorted(positions)
assert "excluded.property == longhand_id" in apply
assert "excluded.priority == priority.unimportant()" in apply
assert "block_contains(excluded.block, declaration)" in apply
assert "priority: priority.unimportant()" in apply
assert "std::ptr::eq(entry, declaration)" in b
assert "unsafe" not in section(b, "enum DeclarationSources", "pub(crate) struct Cascade")
assert section(a, "struct RevertState", "#[derive(Default)]\nstruct SeenSubstitutionFunctions") == section(b, "struct RevertState", "#[derive(Default)]\nstruct SeenSubstitutionFunctions")
for path, item in json.loads((HERE / "SOURCE-API.json").read_text()).items():
    assert sha(run(["git", "--no-optional-locks", "show", item["revision"] + ":" + path], ROOT)) == item["sha256"]
path = "servo/components/style/stylist.rs"
for revision in ["e86b64866cdc5e2260ba9be08c45756fd96e21bb", "a6f39620516a4cf76a5dbf5208960adc79068cf1"]:
    assert run(["git", "--no-optional-locks", "show", revision + ":" + path], ROOT) == (HERE / "base" / path).read_bytes()
assert (HERE / "candidate" / path).read_text().replace("            Some(block),\n", "", 1) == (HERE / "base" / path).read_text()
fixtures = json.loads((HERE / "FIXTURES.json").read_text())
for item in fixtures["unchanged"].values():
    assert sha((ROOT / item["path"]).read_bytes()) == item["sha256"]
assert sum(x["callbacks"] for x in fixtures["unchanged"].values()) == 156
scratch = Path(tempfile.mkdtemp(prefix="cold-rule-membership-"))
try:
    tree = scratch / "tree"
    shutil.copytree(HERE / "base", tree)
    run(["patch", "--batch", "--fuzz=0", "-p1", "-i", str(HERE / "native.patch")], tree)
    for path in roles:
        assert (tree / path).read_bytes() == (HERE / "candidate" / path).read_bytes()
    run(["patch", "--batch", "--fuzz=0", "-R", "-p1", "-i", str(HERE / "native.patch")], tree)
    for path in roles:
        assert (tree / path).read_bytes() == (HERE / "base" / path).read_bytes()
        run(["rustfmt", "--edition", "2024", "--emit", "stdout", str(HERE / "candidate" / path)])
finally:
    shutil.rmtree(scratch)
assert not scratch.exists()
print(json.dumps({"references": len(references), "native_roles": len(roles), "roundtrip_operations": 2, "rustfmt_parsed_files": 2, "declaration_layout_source_unchanged": True, "dependency_prepass_and_both_consumers_unchanged": True, "custom_consumer_and_cutoffs_unchanged": True, "guard_order_and_original_reference_checked": True, "fixtures_unchanged_callbacks": 156, "scratch": str(scratch), "scratch_removed": True, "native_typecheck": False, "browser_run": False}))
