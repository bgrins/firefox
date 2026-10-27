import ast
import hashlib
import json
import stat
import sys
from pathlib import Path
assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
read = lambda p: json.loads(p.read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
for name,digest in read(HERE / "REFERENCES.json").items():
    assert not Path(name).is_absolute() and ".." not in Path(name).parts
    assert stat.S_ISREG((ROOT / name).lstat().st_mode) and sha(ROOT / name) == digest
c = read(HERE / "CONFIG.json")
assert c["ready_for_execution"] is False
assert all(c[n] is None for n in ("epoch","epoch_manifest_sha256","root_receipt_sha256","acceptance","acceptance_sha256"))
base = ROOT / "artifacts/css-svg-length-font-browser-v1"
old = read(base / "CONFIG.json")
assert c["names"] == old["names"] and len(c["names"]) == 6
assert c["owned_test"] == old["owned_test"] and c["owned_metadata"] == old["owned_metadata"]
assert (HERE / "fixture.html").read_bytes() == (base / "fixture.html").read_bytes() == (ROOT / c["proposal"] / "probe.html").read_bytes()
script = (HERE / "run.py").read_text()
compile(script,"run.py","exec")
compile((HERE / "check.py").read_text(),"check.py","exec")
previous = (base / "run.py").read_text()
assert script.split("finally:\n    try:\n        if owned_identity",1)[1] == previous.split("finally:\n    try:\n        if owned_identity",1)[1]
assert script.split('    with (ROOT / owned_test).open("xb")',1)[1].split('    need(len(result["rows"]) == 6',1)[0] == previous.split('    with (ROOT / owned_test).open("xb")',1)[1].split('    need(len(result["rows"]) == 6',1)[0]
start = script.index('    need(all(row["status"] == "PASS"')
end = script.index('    wpt.save("SUMMARY.json", summary)',start)
import textwrap
body = compile(textwrap.dedent(script[start:end]),"actual-classifier","exec")
def need(ok,why):
    if not ok: raise RuntimeError(why)
rows = [{"subtest":n,"status":"PASS"} for n in c["names"]]
namespace = {"need":need,"result":{"rows":rows}}
exec(body,namespace)
assert namespace["summary"]["counts"] == {"PASS":6,"FAIL":0}
for i in range(6):
    bad = [dict(row) for row in rows];bad[i]["status"] = "FAIL"
    try:exec(body,{"need":need,"result":{"rows":bad}})
    except RuntimeError:pass
    else:raise AssertionError(i)
source_inputs = read(ROOT / c["proposal"] / "SOURCE-PINS.json")["files"]
repair_inputs = read(ROOT / c["repair_proposal"] / "SOURCE-PINS.json")
assert set(repair_inputs) == {"dom/svg/DOMSVGLength.cpp","dom/svg/DOMSVGLength.h"}
assert source_inputs["dom/svg/DOMSVGLength.cpp"] == repair_inputs["dom/svg/DOMSVGLength.cpp"]["before_sha256"]
assert set(source_inputs) & set(repair_inputs) == {"dom/svg/DOMSVGLength.cpp"}
result = {"disabled":True,"future_installation_and_acceptance_unbound":True,"six_fixture_names_unchanged":True,
          "fixture_byte_identical":True,"only_font_source_override":"dom/svg/DOMSVGLength.cpp",
          "both_accepted_native_pins_required":True,"unchanged_test_creation_execution_and_cleanup":True,
          "all_six_PASS_required":True,"six_single_failures_rejected":True,"syntax":True,
          "native_build_browser_index_actions":False}
(HERE / "CHECK.json").write_text(json.dumps(result,indent=2)+"\n")
print(json.dumps(result,indent=2))
