import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / "css-document-library-integration-20261110-v1"
CANONICAL = HERE.parent / "css-spec-lean"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    final = json.loads((SOURCE / "ROOT-FINAL-FILES.json").read_text())
    overlay = {str(p.relative_to(SOURCE / "overlay")): p.read_bytes()
               for p in (SOURCE / "overlay").rglob("*") if p.is_file()}
    assert set(final) == set(overlay)
    name = "research/derivation/README.md"
    expected = overlay[name].replace(b"## Boundaries\n", b"## Original codec boundaries\n\n"
        b"The generic document extensions below have their own [proof boundaries](document/README.md).\n")
    assert expected != overlay[name] and overlay[name].count(b"## Boundaries\n") == 1
    actual = {}
    for path, source in overlay.items():
        data = (CANONICAL / path).read_bytes()
        assert sha(data) == final[path]
        assert data == (expected if path == name else source), path
        actual[path] = sha(data)
    with tempfile.TemporaryDirectory(prefix="document-review-root-delta-") as directory:
        work = Path(directory)
        target = work / name
        target.parent.mkdir(parents=True)
        target.write_bytes(overlay[name])
        patch = SOURCE / "ROOT-DOC-CLARIFICATION.patch"
        result = subprocess.run(["git", "apply", str(patch.resolve())], cwd=work, capture_output=True)
        assert result.returncode == 0, result.stderr
        assert target.read_bytes() == expected
    result = {"status": "pass", "root_patch_sha256": sha(patch.read_bytes()),
              "root_final_manifest_sha256": sha((SOURCE / "ROOT-FINAL-FILES.json").read_bytes()),
              "canonical_overlay_files_verified": len(actual), "canonical_overlay_sha256": actual,
              "only_delta_from_frozen_overlay": name,
              "lean_and_checker_changes": False, "native_or_canonical_mutations_by_reviewer": False}
    (HERE / "ROOT-DOC-CHECK.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: result[k] for k in ["status", "root_patch_sha256", "canonical_overlay_files_verified"]}))


if __name__ == "__main__":
    main()
