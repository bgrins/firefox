import hashlib
import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parents[1] / 'artifacts/css-contextual-easing-reversible-browser-v4/wpt.py'
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == 'd6d71f6a2d6641c1bd9801193a6dcf8e8a48d7237745fa8bd7480210c8bdc5ea'
spec = importlib.util.spec_from_file_location('followup_wpt', SOURCE)
implementation = importlib.util.module_from_spec(spec)
spec.loader.exec_module(implementation)
run = implementation.run
