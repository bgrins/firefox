import hashlib,json
from pathlib import Path
r=Path(__file__).resolve().parent
for f,h in json.loads((r/"MANIFEST.json").read_text())["files"].items():
 assert hashlib.sha256((r/f).read_bytes()).hexdigest()==h,f
rows=json.loads((r/"SPAN-TRACE.json").read_text())["rows"]
assert rows[0]["url_span"][1]==rows[0]["taint_span"][0]
assert rows[0]["native_overlap"] and not rows[0]["half_open_overlap"]
assert not rows[1]["native_overlap"]
assert all(x["all_ascii"] for x in rows)
print("Authenticated source/probe and derived touching-span witness; browser NOT_RUN")
