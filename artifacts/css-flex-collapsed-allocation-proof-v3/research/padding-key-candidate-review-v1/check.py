import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit('require isolated nonoptimized Python without site')
sys.dont_write_bytecode=True
from pathlib import Path
import hashlib,json
root=Path(__file__).resolve().parent
repo=root.parents[3]
for name,value in json.loads((root/'INPUTS.json').read_text()).items():
    if hashlib.sha256((repo/name).read_bytes()).hexdigest()!=value:
        raise SystemExit('input changed: '+name)
print('PASS retained review input hashes; raw recount is recorded separately')
