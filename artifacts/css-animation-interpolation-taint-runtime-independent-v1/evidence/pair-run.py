import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
PROPOSAL = ROOT / "artifacts/css-animation-interpolation-taint-proposal-v1"
SOURCE = "servo/components/style/properties_and_values/value.rs"
TEST = "testing/web-platform/tests/css/css-values/registered-number-interpolation-attr-taint.html"

def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream,"sha256").hexdigest()

def read(path):
    return json.loads(path.read_text())

prior = read(ROOT / "artifacts/css-animation-interpolation-taint-root-v1/RUN.json")
pins = prior["pins"].copy()
assert all(sha(ROOT/name)==digest for name,digest in pins.items())
assert sha(PROPOSAL / "source/value.candidate.rs")=="485c097931bcb385bc0ada6679c3429f6f300ffae5f03c75268458feb3316fa0"
assert sha(PROPOSAL / "native.patch")=="f71bde0368680e8cdfd39c9df1fc5e0ab3e302a4b76fe1eea7f46b35b7b562f8"
assert sha(PROPOSAL / Path(TEST).name)==sys.argv[1]
assert not (ROOT/TEST).exists()
(ROOT/TEST).write_bytes((PROPOSAL/Path(TEST).name).read_bytes())
pins[TEST]=sha(ROOT/TEST)
record={"phase":"baseline","complete":False,"pins_before":pins.copy(),
        "scope":"Shared local fix79 tree; only Value::animate metadata changes after focused baseline."}

def save():
    (HERE/"PAIR.json").write_text(json.dumps(record,indent=2)+"\n")

def stable():
    return all(sha(ROOT/name)==digest for name,digest in pins.items())

def run(command,log):
    with log.open("w") as output:
        return subprocess.run(command,cwd=ROOT,stdout=output,stderr=subprocess.STDOUT,
          env={**os.environ,"MOZ_SKIP_PATH_PERFORMANCE_CHECK":"1"}).returncode

def collect(path):
    rows=[json.loads(line) for line in path.read_text().splitlines()]
    assert sum(r.get("action")=="suite_end" for r in rows)==1
    return ([r for r in rows if r.get("action")=="test_status"],
            [r for r in rows if r.get("action")=="test_end"])

save()
baseline=HERE/"baseline";baseline.mkdir(exist_ok=False)
command=["./mach","wpt","--headless","--processes=1",
 "--setpref=layout.css.properties-and-values.enabled=true","--log-raw="+str(baseline/"raw.json"),TEST]
status=run(command,baseline/"wpt.log");rows,ends=collect(baseline/"raw.json")
record["baseline"]={"command":command,"exit":status,"rows":rows,"harness":ends,"stable":stable()};save()
failed=[r for r in rows if r["status"]!="PASS"]
assert len(rows)==24 and len(ends)==1 and ends[0]["status"]=="OK" and stable()
assert [r["subtest"] for r in failed]==["clean-to-tainted, progress 0.25, bundle","clean-to-tainted, progress 0.75, bundle"]
assert all("sampled URL observer" in r.get("message","") for r in failed)
(ROOT/SOURCE).write_bytes((PROPOSAL/"source/value.candidate.rs").read_bytes())
pins[SOURCE]=sha(ROOT/SOURCE)
command=["./mach","format","--path",SOURCE]
record["format"]={"command":command,"exit":run(command,HERE/"format.log")}
assert record["format"]["exit"]==0 and sha(ROOT/SOURCE)==pins[SOURCE]
record.update(phase="building",candidate_source_sha256=pins[SOURCE]);save()
candidate=HERE/"candidate";candidate.mkdir(exist_ok=False)
command=["./mach","build","binaries"]
record["build"]={"command":command,"exit":run(command,candidate/"build.log")}
save();assert record["build"]["exit"]==0
for name in pins:
    if name.startswith("objdir-full.noindex/dist/Nightly.app/Contents/MacOS/"):
        pins[name]=sha(ROOT/name)
assert stable()
record.update(phase="candidate-wpt",pins_after=pins.copy());save()
previous=read(ROOT/"artifacts/css-animation-base-metadata-paired-root-v1/PAIR.json")
tests=[a for a in previous["candidate"]["command"] if a.startswith("testing/")]
tests += [a for a in prior["command"] if a.startswith("testing/")] + [TEST]
command=["./mach","wpt","--headless","--processes=1",
 "--setpref=layout.css.properties-and-values.enabled=true","--log-raw="+str(candidate/"raw.json"),*tests]
status=run(command,candidate/"wpt.log");after,ends=collect(candidate/"raw.json")
key=lambda r:(r["test"],r["subtest"])
before={key(r):r["status"] for r in previous["candidate"]["rows"]+prior["rows"]+rows}
after_map={key(r):r["status"] for r in after}
record["candidate"]={"command":command,"exit":status,"rows":after,"harness":ends}
record["changes"]=[{"identity":list(k),"before":before[k],"after":after_map.get(k)} for k in before if before[k]!=after_map.get(k)]
record["complete"]=(status==0 and len(before)==len(after_map)==len(after)==253 and before.keys()==after_map.keys()
 and all(r["status"]=="PASS" for r in after) and len(ends)==16 and all(r["status"]=="OK" for r in ends) and stable())
record.update(phase="done",stable_after=stable());save();assert record["complete"]
print("253PASS16OK; paired status changes recorded; two boundary diagnostics and historical conditional tests retain limits.")
