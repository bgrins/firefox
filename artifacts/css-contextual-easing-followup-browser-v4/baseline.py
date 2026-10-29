import hashlib
import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parents[1] / 'artifacts/css-contextual-easing-reversible-browser-v4/baseline.py'
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == '1d6426beea3ac3606f952831cb811794fc4b66f92b07841ff24ae06305c3eb08'
spec = importlib.util.spec_from_file_location('followup_baseline', SOURCE)
implementation = importlib.util.module_from_spec(spec)
spec.loader.exec_module(implementation)
implementation.HERE = HERE
prepare = implementation.prepare
guard = implementation.guard

if __name__ == "__main__":
    implementation.main()
