from pathlib import Path
import hashlib
import json

capsule = Path(__file__).resolve().parent


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


manifest = json.loads((capsule / "FILES.json").read_text())
actual = {str(path.relative_to(capsule)) for path in capsule.rglob("*")
          if path.is_file() and path.name not in {"FILES.json", "VERIFY.json"}}
assert actual == set(manifest)
for path, expected in manifest.items():
    assert digest(capsule / path) == expected, path
provenance = json.loads((capsule / "PROVENANCE.json").read_text())
for record in provenance["inputs"]:
    assert digest(capsule / record["copy"]) == record["sha256"]
assert digest(capsule / "animated-custom-property-style-queries.html") == provenance["final_fixture_sha256"]
result = json.loads((capsule / "check1/RESULT.json").read_text())
assert result["callbacks"] == 13 and not result["browser_execution"]
assert result["genuine_wpt_lint_and_manifest"] and result["node_syntax_and_inert_registration"]
assert result["scratch_removed"]
for path, expected in result["source_hashes"].items():
    assert digest(capsule / path) == expected, path
print(json.dumps({"status": "PASS", "files": len(manifest), "callbacks": 13,
                  "browser_execution": False}, indent=2))
