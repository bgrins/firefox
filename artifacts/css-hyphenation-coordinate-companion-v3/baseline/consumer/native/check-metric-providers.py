import hashlib
import json
import subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"development-build/full"
TARGET=OUT/"metric-providers"
records=[]
for name,binary,inputs,expected in [
    ("existing-consumer-matrix","hyphen-consumer","hyphen-consumer-matrix-input.txt","hyphen-consumer-matrix-output.txt"),
    ("existing-coordinate-witness","measurement","measurement-coordinate-input.txt","measurement-coordinate-output.txt")]:
    raw=(OUT/inputs).read_bytes()
    result=subprocess.run([str(TARGET/binary)],input=raw,capture_output=True,timeout=180)
    (TARGET/(name+"-output.txt")).write_bytes(result.stdout)
    (TARGET/(name+"-stderr.txt")).write_bytes(result.stderr)
    assert result.returncode==0,(name,result.returncode,result.stderr)
    prior=(OUT/expected).read_bytes()
    differences=[{"line":i,"prior":a.decode(),"actual":b.decode()}for i,(a,b)in enumerate(zip(prior.splitlines(),result.stdout.splitlines()))if a!=b]
    assert len(prior.splitlines())==len(result.stdout.splitlines())
    records.append({"name":name,"cases":len(raw.splitlines()),"input_sha256":hashlib.sha256(raw).hexdigest(),
        "prior_sha256":hashlib.sha256(prior).hexdigest(),"output_sha256":hashlib.sha256(result.stdout).hexdigest(),
        "binary_sha256":hashlib.sha256((TARGET/binary).read_bytes()).hexdigest(),"differences":differences})
(TARGET/"REPLAY.json").write_text(json.dumps({"fixed_inputs":True,"records":records,"status":"Existing fixture provider compatibility gate; not a universal font/shaping oracle. Existing coordinate baseline failure is intentionally retained."},indent=2)+"\n")
print([(r["name"],r["cases"],len(r["differences"]))for r in records])
assert all(not r["differences"]for r in records)
