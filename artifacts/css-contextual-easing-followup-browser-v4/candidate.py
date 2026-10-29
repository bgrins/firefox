import hashlib
import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parents[1] / 'artifacts/css-contextual-easing-reversible-browser-v4/candidate.py'
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == '7c0c30ca2f2825dcf494d8638ef4ad0f1711a583d5bb4d99a09580cb1e0e6418'
spec = importlib.util.spec_from_file_location('followup_candidate', SOURCE)
implementation = importlib.util.module_from_spec(spec)
spec.loader.exec_module(implementation)
implementation.HERE = HERE

if __name__ == "__main__":
    implementation.main()
