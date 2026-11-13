import hashlib
import json
import re
from pathlib import Path

root = Path(__file__).resolve().parent
repo = root.parent.parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


inputs = json.loads((root / "SOURCE-REVIEW-INPUTS.json").read_text())
for name, expected in inputs["files"].items():
    path = root / "source-review" / name
    assert sha(path) == expected["sha256"]
    assert path.stat().st_size == expected["bytes"]
for name, expected in inputs["indexed_mapping"].items():
    local = (root / "source-review" / expected["source"]).read_text()
    excerpts = []
    for chunk in re.split(r"(?=^>>> )", (root / name).read_text(), flags=re.M):
        lines = []
        for line in chunk.splitlines():
            match = re.match(r"^(?:>>>|\s+)\s*\d+: ?(.*)$", line)
            if match:
                lines.append(match.group(1))
        if lines:
            excerpts.append("\n".join(lines).strip())
    assert len(excerpts) == expected["independent_excerpt_count"]
    assert excerpts and all(excerpt in local for excerpt in excerpts)
for name, expected in json.loads((root / "PREDECESSORS.json").read_text()).items():
    assert sha(repo / name) == expected["sha256"]
for name, expected in json.loads((root / "ORIGINALS.json").read_text()).items():
    assert sha(root / "original" / name) == expected["sha256"]
    assert sha(repo / expected["source"]) == expected["sha256"]
print("PASS source-review snapshots, six exact indexed excerpts, predecessor manifests, original source pins")
