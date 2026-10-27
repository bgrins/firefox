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
assert set(pre) == set(post) and len(pre) == 5
for name, digest in pre.items():
    assert sha(HERE / "original" / name) == digest, name
for name, digest in post.items():
    assert sha(HERE / "candidate" / name) == digest, name
builder = (HERE / "candidate/servo/components/style/properties/properties.mako.rs").read_text()
assert "Self::Owned(UniqueArc::new((**value).clone()))" in builder
assert "Self::Vacated => return None" in builder
assert "${style_struct.ident}: self.${style_struct.ident}.fork()?" in builder
endpoint = (HERE / "candidate/servo/components/style/keyframe_endpoint.rs").read_text()
a = endpoint.index("    pub fn resolve_from_cascade(")
b = endpoint.index("impl MallocSizeOf", a)
attempt = endpoint[a:b]
assert "builder.build(" not in attempt
assert "self.resolve_pending_in_context(" in attempt
assert ".ok_or(EndpointDemand::ContextPreparation)?" in attempt
assert "attributes: tracker.finalize()" in attempt
assert "attempt.builder.flags()" in attempt
assert "cache_conditions," in attempt
glue = (HERE / "candidate/servo/ports/geckolib/glue.rs").read_text()
assert 'pub extern "C" fn Servo_KeyframeEndpoint_ResolveIsolatedForTesting' in glue
assert "endpoint.resolve_from_cascade(" in glue
assert "context.builder.take_font()" in glue
assert "context.builder.put_font(font)" in glue
cpp = (HERE / "candidate/layout/style/test/gtest/TestKeyframePresentation.cpp").read_text()
for assertion in ["EXPECT_TRUE(parentUnchanged)", "EXPECT_TRUE(ownedStructIsolated)", "EXPECT_TRUE(vacatedRejected)", "EXPECT_EQ(test.status, isolatedStatus)", "EXPECT_FALSE(isolatedAttributes)"]:
    assert assertion in cpp
validation = HERE / "validation"
validation.mkdir(exist_ok=False)
results = []
with tempfile.TemporaryDirectory(prefix="css-joint-context-", dir="/private/tmp") as tmp:
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
        results.append({"phase": phase, "exit": result.returncode, "five_bodies_exact": True})
assert not root.exists()
result = {
    "status": "JOINT_CONTEXT_SOURCE_TRANSPORT_PASS",
    "paths": 5,
    "patch_transport": results,
    "scratch_removed": True,
    "source_assertions_only": True,
    "native_compiled": False,
    "native_tests_executed": False,
    "browser_tested": False,
    "pending_rule_iterator_connected": False,
    "joint_native_completion_implemented": False,
    "host_harness_bridge_authored_not_built": True,
    "normal_pending_producer_activated": False,
    "collection_interface_blocker_closed": False,
}
(validation / "CHECK.json").write_text(json.dumps(result, indent=2) + "\n")
print(result["status"])
