import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise RuntimeError("Use python3 -I -S")
sys.dont_write_bytecode = True
import argparse
from pathlib import Path
import runpy
root = Path(__file__).resolve().parent
parser = argparse.ArgumentParser()
parser.add_argument("--manifest-sha", required=True)
args = parser.parse_args()
module = runpy.run_path(str(root / "review.py"))
print(module["closure"](root, args.manifest_sha))
