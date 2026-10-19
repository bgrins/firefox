import hashlib
import json
import subprocess
from pathlib import Path

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[1]


def digest(data):
    return hashlib.sha256(data).hexdigest()


def materialize():
    record = json.loads((BASE / "SOURCE-v1.json").read_text())
    old = subprocess.check_output(["git", "-c", "core.fsmonitor=false", "show",
                                   record["parent"] + ":" + record["paths"]["generic"]], cwd=ROOT)
    animated = subprocess.check_output(["git", "-c", "core.fsmonitor=false", "show",
                                        record["parent"] + ":" + record["paths"]["animated"]], cwd=ROOT)
    text = old.decode()
    if text.count(record["old_arm"]) != 1:
        raise ValueError("Old arm is not unique")
    current = text.replace(record["old_arm"], record["new_arm"], 1).encode()
    sources = {"old-generic.rs": old, "current-generic.rs": current, "animated.rs": animated}
    for name, data in sources.items():
        if digest(data) != record["sha256"][name]:
            raise ValueError("Snapshot hash mismatch: " + name)
        path = BASE / name
        if path.exists() and path.read_bytes() != data:
            raise ValueError("Refusing to overwrite changed snapshot: " + name)
        if not path.exists():
            path.write_bytes(data)
    return record


if __name__ == "__main__":
    materialize()
