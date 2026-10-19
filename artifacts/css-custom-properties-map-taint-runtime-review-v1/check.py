import hashlib,json,runpy
from pathlib import Path
r=Path(__file__).resolve().parent
for name,digest in json.loads((r/"MANIFEST.json").read_text())["files"].items():
    assert hashlib.sha256((r/name).read_bytes()).hexdigest()==digest,name
runpy.run_path(str(r/"checks.py"),run_name="__main__")
