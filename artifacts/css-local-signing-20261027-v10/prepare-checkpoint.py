import hashlib, json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
names = ["commit.py", "prepare.py", "prepare-checkpoint.py", "refresh-ledger.py", "CHECKPOINT.md", "PREPARATION.json", "LEDGER-REFRESH.json", "harness-controls.log"]
for ident in ["guard-model", "fallback-harness", "upstream-variant"]:
    for suffix in ["selection.json", "item.json", "receipt.json", "message.txt", "signature.log", "commit.log", "driver.log"]:
        names.append(ident + "-" + suffix)
paths = [HERE / n for n in names] + [ROOT / "artifacts/stylo-bloom-tools/CURRENT-COMMITS.json"]
pins = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
item = {"id": "checkpoint", "message": "No bug - Checkpoint CSS guard research and preserved unfinished work. r?#firefox-style-system-reviewers", "files": sorted(pins), "source_pins": pins}
with (HERE / "checkpoint-selection.json").open("x") as f:
    json.dump(item, f, indent=2, sort_keys=True)
    f.write("\n")
print(len(pins), "checkpoint files prepared")
