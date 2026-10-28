import hashlib
import json
from pathlib import Path
import sys

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
record = json.loads((HERE / 'LIFECYCLE.json').read_bytes())
digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
assert digest(ROOT / record['capsule_manifest_path']) == record['capsule_manifest_sha256']
assert digest(ROOT / record['path']) == record['sha256']
source = (ROOT / record['path']).read_text()
start = source.index('assessment_error = None\nsummary = {}\ntry:\n')
end = source.index('\nsuccess = error is None', start)
replacement = '''assessment_error = None
summary = {}
try:
    spec = importlib.util.spec_from_file_location('admission_assessment', HERE / 'assess.py')
    assessment = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(assessment)
    summary = assessment.assess(output, code, policy)
except BaseException as exc:
    assessment_error = repr(exc)
'''
source = source[:start] + replacement + source[end:]
exec(compile(source, str(ROOT / record['path']), 'exec'), {'__file__': str(HERE / 'run_admission.py'), '__name__': '__main__'})
