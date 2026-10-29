import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = ROOT / "artifacts/css-contextual-easing-reversible-browser-v4/wpt.py"
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == "d6d71f6a2d6641c1bd9801193a6dcf8e8a48d7237745fa8bd7480210c8bdc5ea"
spec = importlib.util.spec_from_file_location("move_paired_wpt", SOURCE)
implementation = importlib.util.module_from_spec(spec)
spec.loader.exec_module(implementation)


def run_phase(root, output, role, env, verify, owned, cancelled, original=None):
    assert Path(root) == ROOT and role in ("original", "candidate")
    assert isinstance(owned, dict)
    policy = json.loads((HERE / "POLICY.json").read_bytes())
    assert policy["execution_enabled"]
    runtime = ROOT / policy["output"]
    assert Path(output) == runtime / (role + "-wpt")
    assert original is None if role == "original" else Path(original) == runtime / "original-wpt"
    for name, pin in policy["references"].items():
        assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == pin, name
    return implementation.run(ROOT, HERE, Path(output), role, policy, env, verify, owned, cancelled, original)
