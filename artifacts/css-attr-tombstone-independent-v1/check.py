#!/usr/bin/env python3
import argparse
import difflib
import hashlib
import json
from pathlib import Path
import re

parser = argparse.ArgumentParser()
parser.add_argument("--manifest-sha", required=True)
a = parser.parse_args()
root = Path(__file__).resolve().parent
sha = lambda b: hashlib.sha256(b).hexdigest()
raw = (root / "MANIFEST.json").read_bytes()
assert sha(raw) == a.manifest_sha
m = json.loads(raw)
for name,digest in m["files"].items():
    p = root/name
    assert not p.is_symlink() and p.resolve().is_relative_to(root)
    assert sha(p.read_bytes()) == digest, "input mismatch: " + name
admission = json.loads((root/"FINAL-ADMISSION.json").read_text())
assert sha((root/"producer-seal/FREEZE.json").read_bytes()) == admission["producer_freeze_sha256"] == "75e5b73adaab276c987675cb000248294a8ac5d7008fab1a8aa3040f2eb98d65"
assert sha((root/"producer-seal/INPUTS.json").read_bytes()) == admission["producer_inputs_sha256"]
assert sha((root/"final-input/native.patch").read_bytes()) == admission["root_communicated_native_patch_sha256"]
assert sha((root/"final-input/attr-repeated-invalid-value.html").read_bytes()) == admission["root_communicated_wpt_sha256"]
base = json.loads((root/"candidate-input/BASE.json").read_text())
for name,digest in base["pins"].items():
    assert sha((root/"candidate-input/original"/name).read_bytes()) == digest
custom_old = (root/"candidate-input/original/custom_properties.rs").read_text()
custom_new = (root/"final-input/candidate/custom_properties.rs").read_text()
helper = """    #[inline(always)]
    pub(crate) fn contains_attr(&self, name: &Name, namespace: &Namespace) -> bool {
        self.attributes
            .get(namespace)
            .is_some_and(|attributes| attributes.contains_key(name))
    }

"""
assert custom_new.count(helper) == 1
assert custom_new.replace(helper, "") == custom_old
cascade_old = (root/"candidate-input/original/properties__cascade.rs").read_text()
cascade_new = (root/"final-input/candidate/properties__cascade.rs").read_text()
old_guard = "context.map().get_attr(&next.name, namespace).is_none()"
new_guard = "!context.map().contains_attr(&next.name, namespace)"
assert cascade_old.count(old_guard) == 1 and cascade_new.count(new_guard) == 1
assert cascade_old.replace(old_guard,new_guard) == cascade_new
patch = ""
for short,path in base["native_paths"].items():
    old = (root/"candidate-input/original"/short).read_text()
    new = (root/"final-input/candidate"/short).read_text()
    assert new == (root/"candidate-input/candidate"/short).read_text()
    patch += "".join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile="a/"+path,tofile="b/"+path))
assert patch == (root/"final-input/native.patch").read_text()
reset = cascade_new.split("fn reset(&mut self)",1)[1].split("fn map(&self)",1)[0]
for text in ["self.index_map.clear()", "self.var_info.clear()", "self.stack.clear()"]:
    assert text in reset
assert "substitution_functions" not in reset
assert cascade_new.count(".remove_attr(name, namespace)") == 1
assert custom_new.count(".remove_attr(name, namespace)") == 1
assert ".insert(name.clone(), None)" in custom_new
for directory,phase in [("baseline","v1"),("baseline-final","v2")]:
    receipt = json.loads((root/directory/("baseline-"+phase+"-receipt.json")).read_text())
    rows = [json.loads(s) for s in (root/directory/("baseline-"+phase+".jsonl")).read_text().splitlines() if s.strip()]
    assert [r for r in rows if r.get("action") in ["test_status","test_end"]] == receipt["statuses"]
    assert receipt["pins_before"] == receipt["pins_after"] and receipt["all_inputs_unchanged"]
    assert sum(r.get("action")=="suite_end" for r in rows)==1
    target = "/css/css-values/attr-"+("cycle-repeated-reference.html" if phase=="v1" else "repeated-invalid-value.html")
    statuses = [r for r in rows if r.get("test")==target and r.get("action")=="test_status"]
    assert sum(r["status"]=="FAIL" for r in statuses)==4
    assert sum(r["status"]=="PASS" for r in statuses)==(7 if phase=="v1" else 6)
    expected_file = root/("baseline/attr-cycle-repeated-reference.html" if phase=="v1" else "final-input/attr-repeated-invalid-value.html")
    assert receipt["pins_before"]["testing/web-platform/tests"+target] == sha(expected_file.read_bytes())
html = (root/"final-input/attr-repeated-invalid-value.html").read_text()
names = re.findall(r'    name: "([^"]+)"',html)
assert len(names)==10 and len(set(names))==10
assert "predictedFailure" not in html and "assert_implements_optional" not in html
assert "computed.marginTop" in html and "computed.marginRight" in html
spec=(root/"candidate-input/evidence/probe-css-values-5.html").read_bytes()
assert sha(spec)==json.loads((root/"candidate-input/evidence/probe-FETCH.json").read_text())["sha256"]
for anchor in ["attr-substitution","substitute-arbitrary-substitution-function","guarded"]:
    assert ('id="'+anchor+'"').encode() in spec
print(json.dumps({"status":"PASS","authenticated_files":len(m["files"]),"native_delta":"helper plus one guard only","final_wpt_cases":10,"historical_baseline":"4 FAIL / 7 PASS / 1 OK","final_baseline":"4 FAIL / 6 PASS / 1 OK","execution":"integrity/static correspondence only; no native/browser execution"},indent=2))
