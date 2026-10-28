import ast
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
owner_path = ROOT / "artifacts/css-round-context-quotient-reversible-pair-v2/run.py"
pair_path = ROOT / "artifacts/css-round-context-quotient-paired-wpt-runner-v2/bindings.py"
owner = ast.parse(owner_path.read_text())
pair = ast.parse(pair_path.read_text())
final = ast.parse((HERE / "bindings.py").read_text())

def marker_key(node):
    return isinstance(node, ast.Constant) and isinstance(node.value, str) and node.value.startswith("reversible_") and node.value.endswith("_phase")

written = {n.slice.value for n in ast.walk(owner) if isinstance(n, ast.Subscript) and isinstance(n.ctx, ast.Store) and marker_key(n.slice)}
read = {n.slice.value for n in ast.walk(pair) if isinstance(n, ast.Subscript) and marker_key(n.slice)}
popped = {n.args[0].value for n in ast.walk(final) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == "pop" and n.args and marker_key(n.args[0])}
assert len(written) == 1 and written == read == popped
actual_key = next(iter(written))
projection = {actual_key: {"role": "original"}, "preserved": True}
assert projection.pop(next(iter(popped))) == {"role": "original"}
assert projection == {"preserved": True}
wrong = {actual_key: {"role": "original"}}
try:
    wrong.pop("reversible_round_context_quotient_phase")
except KeyError:
    pass
else:
    raise AssertionError("old mismatched key was accepted")
print(json.dumps({"owner_written_key": actual_key, "paired_reader_equal": True, "final_pop_equal": True, "old_wrong_key_rejected": True, "actual_runtime_replay": False}))
