import hashlib
import json
from pathlib import Path
import runpy

root = Path(__file__).resolve().parent
manifest = json.loads((root / "MANIFEST.json").read_text())
for name, expected in manifest["files"].items():
    if ".." in Path(name).parts or Path(name).is_absolute():
        raise SystemExit("invalid path")
    path = root / name
    if path.is_symlink() or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
        raise SystemExit("authentication failed: " + name)
parser = runpy.run_path(str(root / "inspect_font.py"))
print(json.dumps({"authenticated_files": len(manifest["files"]),
                  "font": parser["inspect"](root / "probes/Ahem.ttf"),
                  "browser_execution": False}, indent=2))
