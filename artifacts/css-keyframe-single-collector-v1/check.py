import hashlib
import json
import os
import subprocess
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
pre = json.loads((HERE / "PREIMAGES.json").read_text())
post = json.loads((HERE / "POSTIMAGES.json").read_text())
assert set(pre) == set(post) and len(pre) == 3
for name, digest in pre.items():
    assert sha(HERE / "original" / name) == digest, name
for name, digest in post.items():
    assert sha(HERE / "candidate" / name) == digest, name
cascade = (HERE / "candidate/servo/components/style/properties/cascade.rs").read_text()
assert "match property {}" in cascade
assert "let collected = CollectedDeclarations::collect(" in " ".join(cascade.split())
assert "collected.resolve_concrete(" in " ".join(cascade.split())
assert "fn into_pending_owner<C>" in cascade
assert "AdmittedCustomProperty::Ordinary(declaration.clone())" in cascade
assert "CollectedCustomProperty::Pending { name, property }" in cascade
start = cascade.index("fn admit_custom_property(")
end = cascade.index("/// Cascade a given custom property declaration.", start)
admission = cascade[start:end]
assert "value_may_affect_style" not in admission
assert admission.index("reverted.allows") < admission.index("included_cascade_flags")
assert admission.index("included_cascade_flags") < admission.index("self.seen.custom.var.entry(name)")
assert admission.index("keyword.revert_kind()") < admission.index("entry.insert(false)")
assert cascade.count("fn iter_declarations<") == 1
stylist = (HERE / "candidate/servo/components/style/stylist.rs").read_text()
assert "crate::properties::CascadeDeclaration::Concrete(declaration)" in stylist
adapter = (HERE / "candidate/servo/components/style/native_provider_completion.rs").read_text()
assert "Winner::Pending(winner)" in adapter
validation = HERE / "validation"
validation.mkdir(exist_ok=False)
results = []
with tempfile.TemporaryDirectory(prefix="css-single-collector-", dir="/private/tmp") as tmp:
    root = Path(tmp)
    for name in pre:
        dest = root / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes((HERE / "original" / name).read_bytes())
    for phase, args, pins in [
        ("forward", ["apply", str(HERE / "native.patch")], post),
        ("reverse", ["apply", "--reverse", str(HERE / "native.patch")], pre),
    ]:
        result = subprocess.run(
            ["git", "--no-optional-locks", "-c", "core.fsmonitor=false", *args],
            cwd=root, capture_output=True, text=True,
            env=dict(os.environ, GIT_OPTIONAL_LOCKS="0"),
        )
        (validation / (phase + ".log")).write_text(result.stdout + result.stderr)
        assert result.returncode == 0, (phase, result.stderr)
        assert {name: sha(root / name) for name in pins} == pins
        results.append({"phase": phase, "exit": result.returncode, "three_bodies_exact": True})
assert not root.exists()
result = {
    "status": "SINGLE_COLLECTOR_SOURCE_TRANSPORT_PASS",
    "paths": 3,
    "patch_transport": results,
    "scratch_removed": True,
    "source_assertions_only": True,
    "native_compiled": False,
    "native_tests_executed": False,
    "browser_tested": False,
    "pending_rule_iterator_connected": False,
    "joint_native_completion_implemented": False,
    "host_harness_bridge_available": False,
    "normal_pending_producer_activated": False,
    "collection_interface_blocker_closed": False,
}
(validation / "CHECK.json").write_text(json.dumps(result, indent=2) + "\n")
print(result["status"])
