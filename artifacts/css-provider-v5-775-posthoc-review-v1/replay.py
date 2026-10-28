import ast
from collections import Counter
import hashlib
import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
read = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

inventory = read(HERE / "RUNTIME-INVENTORY.json")
directory = ROOT / inventory["directory"]
files, links = {}, {}
for path in directory.rglob("*"):
    name = str(path.relative_to(directory))
    if path.is_symlink():
        links[name] = str(path.resolve())
    elif path.is_file():
        files[name] = {"sha256": sha(path), "bytes": path.stat().st_size}
assert files == inventory["files"] and links == inventory["links"]
assert not (directory / "RESULT.json").exists()
capsule = ROOT / "artifacts/css-registered-provider-expanded-observation-v5"
for name, pin in read(HERE / "REFERENCES.json").items():
    assert sha(ROOT / name) == pin
run = load("saved_wrapper", capsule / "run.py")
run.authenticate(capsule, read(HERE / "REFERENCES.json")[str(capsule.relative_to(ROOT) / "FILES.json")])
policy = read(capsule / "POLICY.json")
assessment = read(directory / "ASSESSMENT.json")
assert assessment["capsule_manifest_sha256"] == sha(capsule / "FILES.json")
assert assessment["complete"] and assessment["execution_preserved"] and not assessment["errors"]
assert read(directory / "PRE.json") == read(directory / "POST.json")
cleanup = read(directory / "CLEANUP.json")
assert cleanup["owned_group_absent"] and cleanup["temporary_root_removed"]
outer = read(directory / "OUTER.json")
assert outer["exit"] == 1 and outer["wrapper_error"].startswith("KeyError: 'summary'")
metadata = read(directory / "APPLICATION-METADATA.json")
assert metadata == read(directory / "APPLICATION-METADATA-POST.json") == assessment["run_binding"]
assert assessment["epoch_sha256"] == policy["epoch_sha256"] == sha(directory / "EPOCH.json")
epoch = read(directory / "EPOCH.json")
assert epoch == read(capsule / "OBSERVATION-EPOCH.json")
assert assessment["native_sources"] == policy["source_roles"]["candidate"] == read(directory / "PHASE-BINDING.json")["native_sources"]
assert all(epoch["pins"][name] == pin for name,pin in assessment["native_sources"].items())
assert read(directory / "NORMAL-BINARIES.json") == policy["phase_binaries"]
assert all(epoch["pins"][name] == pin for name,pin in policy["phase_binaries"].items())
for name,pin in read(directory / "OWNED-INPUT-PINS.json").items():
    assert sha(directory / name) == pin
parser = load("saved_parser", capsule / "assess.py")
checks = load("saved_checks", ROOT / policy["helpers"]["checks"])
events = [json.loads(line) for line in (directory / "raw.jsonl").read_text().splitlines()]
possible = []
for code in [0,1]:
    replay = parser.assess(events,code,policy,checks,original=None,run_binding=metadata)
    if replay["complete"]:
        possible.append(code)
        for key,value in replay.items():
            if key in ["subtest_cardinality_policy","oracle_caveat"]:
                continue
            assert assessment[key] == value,key
assert possible == [1]
assert assessment["subtest_cardinality_policy"] == policy["cardinality_description"]
assert assessment["oracle_caveat"] == "Provider repair candidate observations against exact775 baseline; no automatic acceptance; review full color snapshots even when FAIL persists"
assert len(assessment["rows"]) == 775 and len(assessment["ends"]) == 36
observations = load("saved_history", capsule / "observations.py")
histories = observations.validate(ROOT,capsule,policy,SimpleNamespace(**vars(run)))
comparison = observations.compare(assessment,histories,policy)
assert comparison == read(directory / "COMPARISON.json") and comparison["complete"]
assert comparison["native_fix_acceptance"] is False
source = ast.parse((capsule / "run.py").read_text())
result_node = next(n.value for n in ast.walk(source) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=="result" for t in n.targets))
summary = result_node.values[next(i for i,k in enumerate(result_node.keys) if isinstance(k,ast.Constant) and k.value=="comparison_summary")]
try:
    eval(compile(ast.Expression(summary),"<frozen-publication-defect>","eval"),{"compared":comparison})
except KeyError as error:
    assert error.args == ("summary",)
else:
    raise AssertionError("saved publication failure not reproduced")
receipt = {"posthoc_observation_replay_complete":True,"original_wrapper_exit":1,"original_RESULT_present":False,
    "original_wrapper_success":False,"browser_rerun":False,"separately_observed_WPT_exit":False,
    "unique_WPT_exit_consistent_with_raw_and_frozen_assessor":possible[0],
    "saved_preservation_and_cleanup_pass":True,"raw_assertions":775,"page_ends":36,
    "statuses":dict(Counter(x["status"] for x in assessment["rows"])),
    "comparison_replayed_exactly":True,"missing_summary_publication_defect_reproduced":True,
    "comparisons":[{k:v for k,v in item.items() if k!="changes"} for item in comparison["comparisons"]],
    "native_fix_accepted":False,"causal_release_MCP_comparison":False}
serialized = json.dumps(receipt,indent=2)+"\n"
if (HERE / "RECOVERY.json").exists():
    assert (HERE / "RECOVERY.json").read_text() == serialized
else:
    with (HERE / "RECOVERY.json").open("x") as output:
        output.write(serialized)
print(json.dumps(receipt))
