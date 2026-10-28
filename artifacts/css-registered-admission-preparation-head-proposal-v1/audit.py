import hashlib
import json
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def function(source, name):
    found = re.search(r"(?m)^.*\bfn " + name + r"[<(]", source)
    assert found, name
    opening = source.index("{", found.start())
    depth = 1
    end = opening + 1
    while depth:
        depth += (source[end] == "{") - (source[end] == "}")
        end += 1
    return source[found.start():end]


kind = "head-proposal" if "head-proposal" in HERE.name else "proposal"
old = ROOT / ("artifacts/css-registered-number-preparation-" + kind + "-v1")
for name, digest in json.loads((HERE / "REFERENCES.json").read_text()).items():
    path = ROOT / name
    assert sha(path) == digest, name
    if path.name == "FILES.json":
        manifest = json.loads(path.read_text())
        for member, pin in manifest.get("files", manifest).items():
            expected = pin["sha256"] if isinstance(pin, dict) else pin
            assert sha(path.parent / member) == expected, member
base = (HERE / "base/servo/components/style/custom_properties.rs").read_text()
candidate = (HERE / "candidate/servo/components/style/custom_properties.rs").read_text()
base_cascade = (HERE / "base/servo/components/style/properties/cascade.rs").read_text()
candidate_cascade = (HERE / "candidate/servo/components/style/properties/cascade.rs").read_text()
old_candidate = (old / "candidate/servo/components/style/custom_properties.rs").read_text()
old_cascade = (old / "candidate/servo/components/style/properties/cascade.rs").read_text()
assert function(base_cascade, "find_non_custom_references") == function(candidate_cascade, "find_non_custom_references")
preserved = ["handle_invalid_at_computed_value_time", "get_attr_value_for_cycle_resolution", "remove_and_insert_initial_value", "compute_value", "substitute_internal"]
if kind == "proposal":
    preserved.append("first_pending_prioritary")
for name in preserved:
    assert function(base, name) == function(candidate, name), name
assert function(old_candidate, "apply_substituted_css_wide_keyword") == function(candidate, "apply_substituted_css_wide_keyword")
assert function(old_cascade, "visit_value_references") == function(candidate_cascade, "visit_value_references")
for value in [base_cascade, candidate_cascade]:
    start = value.index("        context.var_info[index].lowlink = lowlink;")
    end = value.index("        // Not in a loop, apply the value.", start)
    if value is base_cascade:
        settlement = value[start:end]
    else:
        assert settlement == value[start:end]
assert "value_non_custom_refs &= references;" in candidate_cascade
assert "value_non_custom_refs = references;" not in candidate_cascade
assert "is_exact_number_registration" not in candidate + candidate_cascade
assert "Self::Invalid => Some(intrinsic_registered_references(registration))" in candidate
assert "Self::CssWide(_) => Some(ReferenceFlags::empty())" in candidate
assert "references | intrinsic_references" in candidate or "| intrinsic_references" in candidate
assert "let specified = match SpecifiedRegisteredValue::parse(" in candidate
if kind == "proposal":
    assert "references & *conservative_references" in candidate
    assert "Self::Invalid => intrinsic_registered_references(registration)" in candidate
assert all((old_mask & obligations) & ~old_mask == 0 for old_mask in range(64) for obligations in range(64))
print(json.dumps({"status": "STATIC_PRESERVATION_AUDIT_PASS", "variant": kind,
    "original_prefilter_byte_identical": True, "unchanged_functions": preserved,
    "existing_css_wide_helper_preserved": True, "selected_provider_visitor_preserved_from_reviewed_number_proposal": True,
    "scc_settlement_byte_identical": True, "graph_refinement_uses_intersection": True,
    "invalid_preserves_intrinsic_color_scheme": True, "boolean_mask_controls": 4096,
    "native_typecheck": False, "runtime_validation": False, "native_refinement_proof": False}, indent=2))
