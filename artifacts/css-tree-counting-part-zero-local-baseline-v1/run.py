import hashlib
import json
from pathlib import Path
import sys

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
record = json.loads((HERE / "LIFECYCLE.json").read_bytes())
digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
assert digest(ROOT / record["capsule_manifest_path"]) == record["capsule_manifest_sha256"]
assert digest(ROOT / record["path"]) == record["sha256"]
policy = json.loads((HERE / "BASELINE-POLICY.json").read_bytes())
assert digest(ROOT / policy["candidate_manifest_path"]) == policy["candidate_manifest_sha256"]
assert digest(HERE / "fixture/baseline.html") == policy["observation_sha256"]
source = (ROOT / record["path"]).read_text()
for line in ["(page.parent / 'record.py').write_bytes((HERE / 'fixture/record.py').read_bytes())\n",
             "(page.parent / 'observation.js').write_bytes((ROOT / policy['observation_path']).read_bytes())\n"]:
    assert source.count(line) == 1
    source = source.replace(line, "")
start = source.index("assessment_error = None\nsummary = {}\ntry:\n")
end = source.index("\nsuccess = error is None", start)
replacement = '''assessment_error = None
summary = {}
try:
    spec = importlib.util.spec_from_file_location('part_baseline_assessment', HERE / 'assess.py')
    assessment = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(assessment)
    summary = assessment.assess(output, code, policy)
except BaseException as exc:
    assessment_error = repr(exc)
'''
source = source[:start] + replacement + source[end:]
exec(compile(source, str(ROOT / record["path"]), "exec"), {"__file__": str(HERE / "run.py"), "__name__": "__main__"})
