import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
path = ROOT / "artifacts/css-minmax-relative-infinity-broader-browser-v5/assess.py"
spec = importlib.util.spec_from_file_location("executed_strict_assessor", path)
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)
signature = base.signature
bound_run_info = base.bound_run_info


def assess(*args, **kwargs):
    result = base.assess(*args, **kwargs)
    result["oracle_caveat"] = "Original progress observation: nine exact callbacks across three pages; PASS and ordinary assertion FAIL retain their actual outcomes. Records preserve first and subsequent samples; missing records after failed acquisition are incomplete collection. No automatic calibration, convergence, native acceptance or causality claim."
    return result
