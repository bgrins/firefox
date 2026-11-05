from pathlib import Path
import hashlib
import json
import subprocess

artifact = Path(__file__).resolve().parent
root = artifact.parent.parent
source = json.loads((artifact / "SOURCE.json").read_text())
for entry in source["files"]:
    data = subprocess.check_output(
        ["git", "show", source["authority_revision"] + ":" + entry["path"]],
        cwd=root,
    )
    assert hashlib.sha256(data).hexdigest() == entry["sha256"]
    text = data.decode()
    for excerpt in entry["excerpts"]:
        offset = excerpt["offset"]
        assert text[offset:offset + len(excerpt["text"])] == excerpt["text"]
        assert excerpt["text"].startswith(excerpt["needle"])
for entry in [source["frozen_candidate"], *source["prior_evidence"]]:
    assert hashlib.sha256((root / entry["path"]).read_bytes()).hexdigest() == entry["sha256"]
print(json.dumps({
    "result": "PASS",
    "authority_revision": source["authority_revision"],
    "git_source_files": len(source["files"]),
    "exact_excerpts": sum(len(e["excerpts"]) for e in source["files"]),
    "meaning": "Source provenance only; not semantic or browser validation",
}, indent=2))
