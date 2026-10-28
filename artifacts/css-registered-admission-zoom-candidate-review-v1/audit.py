import hashlib
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
refs = {}
def read(path):
    data = path.read_bytes()
    refs[str(path.relative_to(ROOT))] = hashlib.sha256(data).hexdigest()
    return json.loads(data)
phases = []
for phase in ["original", "candidate"]:
    directory = ROOT / ("artifacts/css-registered-admission-zoom-runtime-" + phase + "-1")
    result = read(directory / "RESULT.json")
    raw = read(directory / "RAW.json")
    epoch = read(directory / "EPOCH.json")
    assert result["complete"] and result["execution_preserved"] and result["error"] is None and result["preservation_error"] is None
    assert not raw["network_errors"] and len(raw["payloads"]) == 1
    obs = raw["payloads"][0]["observation"]
    rows = {r["id"]:r for r in obs["rows"]}
    assert len(rows) == len(obs["rows"]) == 16
    assert all(r["registrationErrors"] == [] and len(r["snapshots"]) == 2 for r in rows.values())
    assert read(directory / "PRE.json") == read(directory / "POST.json")
    cleanup = read(directory / "CLEANUP.json")
    assert cleanup["owned_group_absent"] and cleanup["profile_removed"] and cleanup["server_thread_stopped"]
    metadata = read(directory / "APPLICATION-METADATA.json")
    assert metadata == read(directory / "APPLICATION-METADATA-POST.json") == result["application_metadata"]
    assert metadata["revision"] == epoch["semantic_index"]["head"]
    assert result["normal_binaries"] == read(directory / "NORMAL-BINARIES.json")
    assert all(epoch["pins"][n] == v for n,v in result["native_sources"].items())
    assert all(epoch["pins"][n] == v for n,v in result["normal_binaries"].items())
    wptdir = ROOT / ("artifacts/css-registered-number-wpt-runtime-" + phase + "-2")
    assessment = read(wptdir / "ASSESSMENT.json")
    assert result["normative_assessment_sha256"] == refs[str((wptdir/"ASSESSMENT.json").relative_to(ROOT))]
    assert metadata == assessment["run_binding"] and result["epoch_sha256"] == assessment["epoch_sha256"]
    phases.append(dict(rows=rows, query_order=obs["queryOrder"], result=result, cleanup=cleanup))
old, new = phases
assert old["rows"].keys() == new["rows"].keys() and old["query_order"] == new["query_order"]
changes = []
for key in old["rows"]:
    before, after = old["rows"][key], new["rows"][key]
    for a,b in zip(before["snapshots"],after["snapshots"]):
        assert {k:v for k,v in a.items() if k != "actual"} == {k:v for k,v in b.items() if k != "actual"}
    if before != after:
        changes.append(dict(id=key, original=before, candidate=after))
expected = {mode+"/"+font for mode in ["ready-unused-em","selected-invalid-em","wrong-ready-unused-em","direct-invalid"] for font in ["fixed-font","self-font"]}
assert {v["id"] for v in changes} == expected
assert len(changes) == new["result"]["comparison"]["changed_cases"] == 8
assert refs["artifacts/css-registered-admission-zoom-runtime-candidate-1/RESULT.json"] == "4e388b2b62cd83024dd9273252ee68260e0769bd407c8c2db8a4c81bf8bc3eb0"
for mode,initial,want in [("ready-unused-em", "5px", "2.5px"), ("selected-invalid-em", "10px", "5px"),("wrong-ready-unused-em", "10px", "5px"),("direct-invalid", "10px", "5px")]:
    a=old["rows"][mode+"/fixed-font"]["snapshots"][1]["actual"]
    b=new["rows"][mode+"/fixed-font"]["snapshots"][1]["actual"]
    assert a["value"] == initial and b["value"] == want
assert old["rows"]["literal/fixed-font"] == new["rows"]["literal/fixed-font"]
for name in ["artifacts/css-registered-admission-zoom-trace-v1/FILES.json", "artifacts/css-registered-zoom-normalization-model-v1/FILES.json", "artifacts/css-registered-zoom-scaling-api-audit-v1/FILES.json"]:
    read(ROOT/name)
check = dict(status="NEW_CSSOM_REGRESSION_CONFIRMED_IN_LOCAL_COMPARISON", acceptance_blocker=True,
             changed_rows=changes, changed_count=8, unchanged_count=8, registrations_succeeded=16,
             candidate_cleanup=new["cleanup"], native_fix_accepted=False, browser_executed_by_review=False)
(HERE/"CHECK.json").write_text(json.dumps(check,indent=2)+"\n")
(HERE/"REFERENCES.json").write_text(json.dumps(refs,indent=2,sort_keys=True)+"\n")
print(json.dumps({k:v for k,v in check.items() if k != "changed_rows"}))
