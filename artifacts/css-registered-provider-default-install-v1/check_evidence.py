import copy
import hashlib
import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("provider_install", HERE / "install.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
policy = m.read(HERE / "POLICY.json")
epoch = m.read(HERE / "INITIAL-EPOCH.json")
role = m.read(HERE / "INITIAL-ROLE.json")
run = m.ROOT / policy["required_run"]
original_read = m.read
metadata = original_read(run / "APPLICATION-METADATA.json")
overrides = {}
m.read = lambda path: copy.deepcopy(overrides.get(str(path), original_read(path)))
runner = SimpleNamespace(application_metadata=lambda path, head: copy.deepcopy(metadata))

def validate_phase(root, here, p, e, h):
    assert e == epoch and p["epoch_sha256"] == policy["epoch_sha256"]

m.load = lambda name, path: (runner if name == "provider_baseline_runner" else
    SimpleNamespace(validate_phase=validate_phase) if name == "provider_baseline_bindings" else
    SimpleNamespace(process_census_clear=lambda text, pid: None))
m.subprocess.run = lambda *args, **kwargs: SimpleNamespace(stdout="")

def authenticate(path, expected):
    assert m.sha(path / "FILES.json") == expected
    for name, item in original_read(path / "FILES.json").items():
        assert m.sha(path / name) == (item["sha256"] if isinstance(item, dict) else item)

h = SimpleNamespace(authenticate=authenticate, group_absent=lambda pgid: None,
                    quiescent=lambda runtime: None)
m.check_evidence(h, role, policy, epoch)
mutants = [
    ("OUTER.json", ["wrapper_exit"], 1),
    ("RESULT.json", ["observation_gate_passed"], False),
    ("RESULT.json", ["execution_error"], "failure"),
    ("RESULT.json", ["preservation_error"], "failure"),
    ("ASSESSMENT.json", ["complete"], False),
    ("ASSESSMENT.json", ["execution_preserved"], False),
    ("ASSESSMENT.json", ["errors"], ["timeout"]),
    ("ASSESSMENT.json", ["observed_subtest_count"], 774),
    ("ASSESSMENT.json", ["epoch_sha256"], "0" * 64),
    ("ASSESSMENT.json", ["native_sources", "servo/components/style/custom_properties.rs"], "0" * 64),
    ("ASSESSMENT.json", ["run_binding", "browser_build_id"], "wrong"),
    ("CLEANUP.json", ["owned_group_absent"], False),
    ("CLEANUP.json", ["temporary_root_removed"], False),
    ("FILES.json", ["complete"], False),
]
for name, keys, value in mutants:
    path = run / name
    altered = original_read(path)
    target = altered
    for key in keys[:-1]:
        target = target[key]
    target[keys[-1]] = value
    overrides[str(path)] = altered
    try:
        m.check_evidence(h, role, policy, epoch)
    except AssertionError:
        pass
    else:
        raise AssertionError("accepted mutation: " + name + str(keys))
    finally:
        overrides.clear()
print(json.dumps({"saved_baseline_positive": 1, "record_mutations_rejected": len(mutants),
                  "mocked": ["process probes", "live application metadata", "Git succession helper"],
                  "main_executed": False, "live_mutations": False}))
