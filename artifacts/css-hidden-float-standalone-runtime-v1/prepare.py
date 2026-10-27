import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit("Require python3 -I -S without optimization")
sys.dont_write_bytecode = True
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import stat

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
def load(name):
    spec = importlib.util.spec_from_file_location(name, HERE / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def need(ok, why):
    if not ok:
        raise RuntimeError(why)

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
parser = argparse.ArgumentParser()
parser.add_argument("--draft-sha", required=True)
parser.add_argument("--expected-head", required=True)
args = parser.parse_args()
need(not any((HERE / name).exists() for name in ["INPUTS.json", "prepared", "BEFORE.json"]),
     "already prepared or run")
need(sha(HERE / "DRAFT-FILES.json") == args.draft_sha, "draft manifest pin")
draft = json.loads((HERE / "DRAFT-FILES.json").read_text())
for name, digest in draft.items():
    need(not Path(name).is_absolute() and ".." not in Path(name).parts, "unsafe draft path")
    need(stat.S_ISREG((HERE / name).lstat().st_mode) and sha(HERE / name) == digest,
         "draft payload " + name)
bindings = load("bindings")
wpt = load("run_wpt")
c = wpt.CONFIG
need(c.get("ready_for_preparation") is True, "draft not ready for preparation")
bindings.prerequisites()
index = bindings.index_state(wpt)
binary_pins = bindings.restored_epoch(wpt)
bindings.existing_tests(wpt)
before = wpt.snapshot()
need(before["head"] == args.expected_head == c["expected_head"] == index["head"],
     "HEAD differs from the reviewed unsigned baseline")
need(len(c["sources"]) == len(set(c["sources"])) == 24
     and len(c["guard_sources"]) == len(set(c["guard_sources"])) == 29,
     "source roster")
need(before["sources"] == c["original_source_pins"], "installed working source roles changed")
need(all(before[k] == index[k] for k in ["head", "index_diff_sha256", "index_entries_sha256"]),
     "prepared index epoch differs")
need(len(c["install"]) == 2 and len(c["existing_tests"]) == 9
     and set(c["install"]).isdisjoint(c["existing_tests"])
     and set(c["tests"]) == set(c["install"]) | set(c["existing_tests"]),
     "test ownership partition")
need(sum(map(len, c["expected_subtests"].values())) == c["expected_total_subtests"] == 12
     and set(c["run_tests"]) == set(c["install"])
     and len(c["run_tests"]) == len(c["expected_subtests"]) == 2, "exact 12-case roster")
need(all(not (ROOT / n).exists() and not (ROOT / n).is_symlink() for n in c["must_be_absent"]),
     "old or new temporary test exists")
need(set(c["head_sources"]) == set(c["baseline_sources"]) == set(c["sources"]),
     "source role maps differ")
changed = []
for name in c["sources"]:
    head = wpt.git("show", "HEAD:" + name)
    need(head == (HERE / c["head_sources"][name]).read_bytes(), "reviewed HEAD body differs " + name)
    if head != (HERE / c["baseline_sources"][name]).read_bytes():
        changed.append(name)
need(not changed, "standalone baseline must equal HEAD for all24 normalized sources")
for name in c["guard_sources"]:
    need(sha(HERE / "selected/head" / name) == c["baseline_guard_pins"][name]
         and wpt.git("show", "HEAD:" + name) == (HERE / "selected/head" / name).read_bytes(),
         "HEAD guard role differs " + name)
for name in set(c["guard_sources"]) - set(c["sources"]):
    need(wpt.git("show", "HEAD:" + name) == (ROOT / name).read_bytes()
         == (HERE / "selected/head" / name).read_bytes(), "unwritten guard differs " + name)
resources = wpt.resource_paths(c["tests"], virtual=True)
resource_pins = wpt.pins(resources, virtual=True)
installed_resources = json.loads((ROOT / "artifacts/css-hidden-query-installed-v1/RESOURCES.json").read_text())
float_resources = json.loads((ROOT / "artifacts/css-hidden-float-fixture-check-v1/INPUTS.json").read_text())["resources"]
need(all(installed_resources[n] == float_resources[n]
         for n in set(installed_resources) & set(float_resources)), "historical resource overlap differs")
historical = installed_resources | float_resources
proposal = ROOT / "artifacts/css-hidden-float-landing-proposal-v2"
for name, payload in c["install"].items():
    need((HERE / payload).read_bytes() == (proposal / Path(name).name).read_bytes(),
         "final proposed WPT differs " + name)
    historical[name] = sha(HERE / payload)
need(resource_pins == historical
     == json.loads((HERE / "RESOURCE-EXPECTATIONS.json").read_text()),
     "test/support/metadata differs from historical union plus exact final WPTs")
need(all(resource_pins[n] is not None for n in c["tests"] + c["support_paths"]),
     "missing test/support")
prepared = HERE / "prepared"
prepared.mkdir()
for name in c["sources"]:
    for role, data in [("original", (ROOT / name).read_bytes()), ("head", wpt.git("show", "HEAD:" + name))]:
        target = prepared / role / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
need(wpt.snapshot() == before and bindings.restored_epoch(wpt) == binary_pins,
     "source/HEAD/index/binary changed during preparation")
bindings.existing_tests(wpt)
need(wpt.pins(wpt.resource_paths(c["tests"], virtual=True), virtual=True) == resource_pins,
     "resources changed during preparation")
payloads = dict(draft)
for f in prepared.rglob("*"):
    if f.is_file():
        payloads[str(f.relative_to(HERE))] = sha(f)
inputs = {"before": before, "binary_pins": binary_pins, "source_pins": before["sources"], "resource_pins": resource_pins,
          "temporary_test_state": {n: None for n in c["install"]},
          "expected_staged_paths": 925, "draft_sha256": args.draft_sha,
          "payload_pins": payloads, "external_pins": json.loads((HERE / "REFERENCES.json").read_text())}
(HERE / "INPUTS.json").write_text(json.dumps(inputs, indent=2) + "\n")
print(json.dumps({"status": "PREPARED_NOT_RUN", "head": before["head"],
                  "INPUTS_sha256": sha(HERE / "INPUTS.json"), "sources_to_restore": 24,
                  "source_guards": 29, "read_only_tests": 9, "temporary_tests": 2,
                  "subtests": 12, "staged_research_paths": 925}, indent=2))
