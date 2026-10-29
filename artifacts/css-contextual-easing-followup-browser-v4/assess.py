import hashlib
import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parents[1] / 'artifacts/css-contextual-easing-reversible-browser-v4/assess.py'
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == '06d5ad95c7df382df31182406e3d310b4fafae261e2cb01b399bfde59ab86a9a'
spec = importlib.util.spec_from_file_location('followup_assess', SOURCE)
implementation = importlib.util.module_from_spec(spec)
spec.loader.exec_module(implementation)
assess = implementation.assess
signature = implementation.signature
bound_run_info = implementation.bound_run_info
