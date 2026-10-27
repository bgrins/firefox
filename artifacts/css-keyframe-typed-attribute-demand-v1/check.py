import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

parser = argparse.ArgumentParser()
parser.add_argument("--output", type=Path, required=True)
args = parser.parse_args()
assert args.output.is_absolute() and not args.output.exists()
here = Path(__file__).resolve().parent
root = here.parents[1]
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
pre = json.loads((here / "PREIMAGES.json").read_text())
post = json.loads((here / "POSTIMAGES.json").read_text())
assert pre.keys() == post.keys() and len(pre) == 5
for side, pins in [("original", pre), ("candidate", post)]:
    assert {name: sha(here / side / name) for name in pins} == pins
for name, digest in json.loads((here / "REFERENCES.json").read_text()).items():
    assert sha(root / name) == digest, name

def body(side, name):
    return (here / side / name).read_text()

custom_name = "servo/components/style/custom_properties.rs"
custom = body("candidate", custom_name)
assert "SubstitutionDemand::AttributePreparation" not in custom
assert "!substitution_functions.contains_attr(&reference.name, namespace)" in custom
assert "SubstitutionDemand::Attribute {" in custom
assert "namespace: Option<&Namespace>" in custom
assert custom.index("first_pending_prioritary(reference.to_prioritary_id(), pending_prioritary)") < custom.index("let value = match substitution.into_value(")
cascade_name = "servo/components/style/properties/cascade.rs"
cascade = body("candidate", cascade_name)
traverse = cascade[cascade.index("    fn traverse<"):]
assert traverse.index("names.contains(name)") < traverse.index("map.get_var(") if "map.get_var(" in traverse else traverse.index("names.contains(name)") < traverse.index(".get_var(")
assert "if !primary_valid && let Some(ref fallback) = next.fallback" in cascade
assert "if demand.is_err()" in cascade and "demand?;" in cascade
assert "Some(context.pending_prioritary)" in cascade
endpoint_name = "servo/components/style/keyframe_endpoint.rs"
old_endpoint = body("original", endpoint_name)
endpoint = body("candidate", endpoint_name)
old_resolver = old_endpoint[old_endpoint.index("impl KeyframeEndpoint {\n    /// Resolve"):old_endpoint.index("pub enum EndpointDemand")]
assert old_resolver in endpoint
assert "resolve_requested_attribute" in endpoint and "Some(pending_prioritary)" in endpoint
assert endpoint.index("substitution_functions.attributes.clear()") < endpoint.index("let external_demand")
cpp_name = "layout/style/test/gtest/TestKeyframePresentation.cpp"
old_cpp = body("original", cpp_name)
cpp = body("candidate", cpp_name)
anchor = "TEST_F(KeyframePresentation, RetainedEndpointProviderDemand)"
assert cpp[:cpp.index(anchor)] == old_cpp[:old_cpp.index(anchor)]
new_test = cpp[cpp.index(anchor):]
assert new_test.index("ASSERT_TRUE(endpoint);") < new_test.index("NS_ConvertUTF8toUTF16(test.attribute)")
assert "Status::Prioritary" in new_test
assert "var(--ready, attr(data type(<number>)))" in new_test
assert "var(--missing, attr(data type(<number>)))" in new_test
args.output.mkdir()
receipts = []
with tempfile.TemporaryDirectory(prefix="typed-attribute-demand-", dir="/private/tmp") as temporary:
    temp = Path(temporary)
    for kind in ["incremental", "stack"]:
        tree = temp / kind
        shutil.copytree(here / "original", tree)
        if kind == "stack":
            earlier = root / "artifacts/css-keyframe-demand-substitution-v1/original"
            for name in pre:
                if (earlier / name).exists():
                    shutil.copyfile(earlier / name, tree / name)
        before = {name: sha(tree / name) for name in pre}
        patch = here / ("native.patch" if kind == "incremental" else "stack-native.patch")
        for reverse, expected in [(False, post), (True, before)]:
            command = ["patch", "--batch", "-p1"] + (["-R"] if reverse else [])
            run = subprocess.run(command, cwd=tree, input=patch.read_bytes(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            label = kind + ("-reverse" if reverse else "-forward")
            (args.output / (label + ".log")).write_bytes(run.stdout)
            assert run.returncode == 0
            assert {name: sha(tree / name) for name in pre} == expected
            receipts.append({"phase": label, "exit": run.returncode})
    tree = temp / "supplement"
    shutil.copytree(here / "original", tree)
    original = (tree / cpp_name).read_bytes()
    patch = here / "v1-fallback-test-supplement.patch"
    for reverse in [False, True]:
        run = subprocess.run(["patch", "--batch", "-p1"] + (["-R"] if reverse else []), cwd=tree, input=patch.read_bytes(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        assert run.returncode == 0
        if not reverse:
            supplement = (tree / cpp_name).read_text()
            assert "var(--ready, attr(data type(<number>)))" in supplement
            assert "var(--missing, attr(data type(<number>)))" in supplement
        else:
            assert (tree / cpp_name).read_bytes() == original
assert not Path(temporary).exists()
result = {
    "status": "TYPED_ATTRIBUTE_DEMAND_SOURCE_TRANSPORT_PASS",
    "native_compiled": False,
    "native_tests_executed": False,
    "browser_tested": False,
    "ordinary_resolver_and_existing_tests_preserved": True,
    "ordinary_scc_result_plumbing_changed": True,
    "scc_primary_first_fallback_rule_retained": True,
    "patch_transport": receipts,
    "v1_test_supplement_transport": True,
    "scratch_removed": True,
}
(args.output / "CHECK.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result))
