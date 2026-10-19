import hashlib
import json
import os
from pathlib import Path
import subprocess

root = Path(__file__).resolve().parents[2]
here = Path(__file__).resolve().parent
sources = ["custom_properties.rs", "properties/cascade.rs"]
original = {name: (here / "native-original-v1" / name.replace("/", "__")).read_bytes() for name in sources}
candidate = {name: (here / "native-candidate-v2" / name.replace("/", "__")).read_bytes() for name in sources}
status = {"steps": [], "state": "starting"}
status_path = here / "paired-validation-v1.json"
assert not status_path.exists()

def save():
    status_path.write_text(json.dumps(status, indent=2) + "\n")

def source_pins():
    return {name: hashlib.sha256((root / "servo/components/style" / name).read_bytes()).hexdigest() for name in sources}

def switch(before, after):
    for name in sources:
        assert (root / "servo/components/style" / name).read_bytes() == before[name], name
    for name in sources:
        (root / "servo/components/style" / name).write_bytes(after[name])

def run(label, command, logfile, expected_exit):
    status["state"] = label
    save()
    before = source_pins()
    env = dict(os.environ, MOZCONFIG=str(root / "mozconfig"), MOZ_SKIP_PATH_PERFORMANCE_CHECK="1")
    with logfile.open("w") as log:
        result = subprocess.run(command, cwd=root, env=env, stdout=log, stderr=subprocess.STDOUT)
    after = source_pins()
    status["steps"].append({"label": label, "command": command, "exit_code": result.returncode,
                            "sources_before": before, "sources_after": after, "log": str(logfile.relative_to(root))})
    save()
    assert before == after, label
    assert result.returncode == expected_exit, (label, result.returncode)

def wpt(phase, expected_counts, expected_exit):
    run(phase, ["python3", str(here / "run_wpt_v3.py"), phase], here / (phase + "-driver.log"), expected_exit)
    receipt = json.loads((here / (phase + "-receipt.json")).read_text())
    assert receipt["all_inputs_unchanged"] and receipt["suite_end_count"] == 1, phase
    assert receipt["absent_before"] == receipt["absent_after"], phase
    assert receipt["counts"]["/css/css-values/attr-namespace-cache.html"] == expected_counts, receipt["counts"]
    assert receipt["counts"]["/css/css-values/attr-cycle.html"] == {"PASS": 37, "OK": 1}
    for name in ["attr-namespace-valid.xhtml", "attr-namespace-case-sensitivity.xhtml"]:
        assert receipt["counts"]["/css/css-values/" + name] == {"PASS": 1}
    return receipt

try:
    switch(candidate, candidate)
    first = wpt("candidate-v4", {"PASS": 21, "OK": 1}, 0)
    switch(candidate, original)
    run("build-original", ["/Users/bgrins/venvs/firefox/bin/python", "./mach", "build", "binaries"], here / "build-v3.log", 0)
    baseline = wpt("baseline-v4", {"FAIL": 13, "PASS": 8, "OK": 1}, 1)
    switch(original, candidate)
    run("build-candidate", ["/Users/bgrins/venvs/firefox/bin/python", "./mach", "build", "binaries"], here / "build-v4.log", 0)
    final = wpt("candidate-v5", {"PASS": 21, "OK": 1}, 0)
    allowed = {"servo/components/style/custom_properties.rs", "servo/components/style/properties/cascade.rs",
               "objdir-full.noindex/dist/Nightly.app/Contents/MacOS/firefox", "objdir-full.noindex/dist/Nightly.app/Contents/MacOS/XUL"}
    assert baseline["pins_before"].keys() == final["pins_before"].keys()
    changed = {name for name in baseline["pins_before"] if baseline["pins_before"][name] != final["pins_before"][name]}
    assert changed <= allowed, changed
    assert first["pins_before"]["objdir-full.noindex/.mozconfig.json"] == baseline["pins_before"]["objdir-full.noindex/.mozconfig.json"]
    status["changed_pair_inputs"] = sorted(changed)
    status["state"] = "PAIRED_BROWSER_PASS"
except BaseException as error:
    status["state"] = "FAILED"
    status["error"] = repr(error)
    for name in sources:
        path = root / "servo/components/style" / name
        if path.read_bytes() == original[name]:
            path.write_bytes(candidate[name])
    status["candidate_sources_restored"] = all((root / "servo/components/style" / name).read_bytes() == candidate[name] for name in sources)
    save()
    raise
save()
print(json.dumps({"status": status["state"], "steps": len(status["steps"])}))
