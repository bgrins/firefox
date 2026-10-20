import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parent
records = json.loads((root / "FILES.json").read_text())
for name, expected in records.items():
    path = root / name
    assert path.is_file() and not path.is_symlink(), name
    assert hashlib.sha256(path.read_bytes()).hexdigest() == expected, name
for index in ("spec/INDEX.json", "prior/INDEX.json"):
    records = json.loads((root / index).read_text())
    for record in records:
        path = root / Path(index).parent / record["file"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == record["sha256"], str(path)
fixture = json.loads((root / "FIXTURE-CHECK.json").read_text())
assert len(fixture["names"]) == len(set(fixture["names"])) == 40
print("Integrity and recorded fixture roster checked; no browser execution")
