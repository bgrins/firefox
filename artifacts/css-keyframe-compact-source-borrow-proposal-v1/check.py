from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
sha = lambda data: hashlib.sha256(data).hexdigest()
pre = json.loads((HERE / "PREIMAGES.json").read_text())
post = json.loads((HERE / "POSTIMAGES.json").read_text())
assert len(pre) == 4 and pre.keys() == post.keys()
for name in pre:
    assert sha((HERE / "original" / name).read_bytes()) == pre[name]
    assert sha((HERE / "candidate" / name).read_bytes()) == post[name]
arc = "servo/components/servo_arc/lib.rs"
original = (HERE / "original" / arc).read_text()
candidate = (HERE / "candidate" / arc).read_text()
start = candidate.index("/// A pointer-sized, non-owning borrow")
end = candidate.index("impl<A, B> ArcUnion<A, B> {", start)
without_new_type = candidate[:start] + candidate[end:]
without_new_type = without_new_type[:without_new_type.index("\n#[cfg(test)]\nmod compact_borrow_tests")]
assert without_new_type == original
assert candidate.count("```compile_fail") == original.count("```compile_fail") + 3
assert candidate[candidate.index("mod compact_borrow_tests"):].count("#[test]") == 5
source = (HERE / "candidate/servo/components/style/rule_tree/source.rs").read_text()
assert "pub enum StyleSourceBorrow" not in source
assert "StyleSourceBorrow(ArcUnionBorrowPtr::from_union(&self.0))" in source
assert "#![deny(unsafe_code)]" in source
block = "servo/components/style/properties/declaration_block.rs"
assert (HERE / "candidate" / block).read_text() == (HERE / "original" / block).read_text().replace("use crate::shared_lock::Locked;\n", "")
host = (HERE / "candidate/layout/style/test/gtest/rust/owner_cases.rs").read_text()
assert '#[cfg(target_pointer_width = "64")]\n    assert_eq!(\n        size_of::<style::applicable_declarations::ApplicableDeclarationBlock' in host
with tempfile.TemporaryDirectory(prefix="compact-arc-borrow-") as directory:
    root = Path(directory)
    for name in pre:
        dst = root / name
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(HERE / "original" / name, dst)
    for arguments in [["--check"], [], ["--reverse", "--check"], ["--reverse"]]:
        subprocess.run(["git", "apply", *arguments, str(HERE / "native.patch")], cwd=root, check=True, capture_output=True)
        if not arguments:
            assert all(sha((root / name).read_bytes()) == digest for name, digest in post.items())
    assert all(sha((root / name).read_bytes()) == digest for name, digest in pre.items())
assert not root.exists()
print(json.dumps({"status": "COMPACT_BORROW_SOURCE_TRANSPORT_PASS", "paths": 4, "backward_compatible_arc_bodies": True, "drafted_unit_tests": 5, "drafted_compile_fail_controls": 3, "scratch_removed": True, "compiled": False, "tests_executed": False}))
