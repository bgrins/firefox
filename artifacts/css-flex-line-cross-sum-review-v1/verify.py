import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise RuntimeError("Use python3 -I -S")
sys.dont_write_bytecode=True
import argparse
from pathlib import Path
import runpy
root=Path(__file__).resolve().parent
ap=argparse.ArgumentParser();ap.add_argument('--manifest-sha',required=True);args=ap.parse_args()
check=runpy.run_path(str(root/'check_evidence.py'))
print(check['closure'](root,args.manifest_sha))
