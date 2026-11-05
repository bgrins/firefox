from pathlib import Path
import ast
import hashlib
import json
import subprocess
import sys
import tempfile

artifact = Path(__file__).resolve().parent
root = artifact.parent.parent
source = json.loads((artifact / "SOURCE.json").read_text())
base = (root / source["base_path"]).read_bytes()
assert hashlib.sha256(base).hexdigest() == source["base_sha256"]
assert hashlib.sha256((root / source["old_diagnostic_path"]).read_bytes()).hexdigest() == source["old_diagnostic_sha256"]
path = "servo/components/style/properties/cascade.rs"
candidate = (artifact / "candidate" / path).read_bytes()
text = candidate.decode()
start = text.index("impl<'a> DeclarationSources<'a> {")
end = text.index("struct DeclarationSourceIndex", start)
without = (text[:start] + text[end:]).replace("        sources.trace_occurrences();\n", "")
assert without.encode() == base
assert text.count("        sources.trace_occurrences();\n") == 1
assert "sources.trace_occurrences();" in text[text.index("impl<'a> RuleExclusions<'a>"):]
subprocess.run([
    "rustfmt", "--check", "--config-path", str(root / "servo/rustfmt.toml"),
    str(artifact / "candidate" / path),
], check=True)
for name in ["analyze.py", "check_parser.py", "check_preparation.py"]:
    ast.parse((artifact / name).read_text(), filename=name)
subprocess.run([sys.executable, "-B", str(artifact / "check_parser.py")], check=True)
with tempfile.TemporaryDirectory(prefix="css-incremental-occurrence-", dir="/private/tmp") as scratch:
    copied = Path(scratch) / path
    copied.parent.mkdir(parents=True)
    copied.write_bytes(base)
    for reverse, wanted in [(False, candidate), (True, base)]:
        command = ["patch", "--batch", "--fuzz=0", "-p1", "-i", str(artifact / "native.patch")]
        if reverse:
            command.append("-R")
        subprocess.run(command, cwd=scratch, check=True, capture_output=True)
        assert copied.read_bytes() == wanted
print(json.dumps({"prepared": True, "preimage_unchanged": True, "prior_artifact_unchanged": True,
                  "owner_and_exclusion_code_unchanged_except_trace_call": True,
                  "rustfmt_check": True, "patch_forward_reverse_byte_exact": True,
                  "python_syntax": True, "scratch_removed": True,
                  "native_typecheck": False, "native_execution": False}, indent=2))
