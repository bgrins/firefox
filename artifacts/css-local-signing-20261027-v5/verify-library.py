import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
RUN = ROOT / 'artifacts/css-steps-origin-library-application-runtime-v1'
LIB = ROOT / 'artifacts/css-spec-lean'
ENV = dict(os.environ, GIT_OPTIONAL_LOCKS='0')


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def read(path):
    return json.loads(path.read_text())


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def save(name, value):
    with (HERE / name).open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write('\n')


h = load('preservation', 'artifacts/css-keyframe-commit-styles-implicit-clean-comparison-v1/compare.py')
a = load('epoch', 'artifacts/css-keyframe-operation-descriptor-post-signing-proposal-v2/epoch.py')
old_epoch = read(ROOT / 'artifacts/css-integer-stored-range-metadata-runtime-v1/CURRENT-EPOCH.json')
result = read(RUN / 'RESULT.json')
assert result['status'] == 'STEPS_ORIGIN_LIBRARY_FULL_CHECK_PASS'
assert read(RUN / 'CHECK-EXECUTION.json')['exit'] == 0
preservation = read(RUN / 'PRESERVATION.json')
assert preservation == dict(application_error=None, preservation_errors=[], applied=True, full_check_exit=0, rollback_performed=False)
plan = read(ROOT / 'artifacts/css-steps-origin-library-proposal-v1/PLAN.json')
postimages = read(RUN / 'APPLIED.json')['postimages']
assert postimages == {n: p['after'] for n, p in plan['changes'].items()}
assert len(postimages) == 10
for name, pin in postimages.items():
    assert sha(LIB / name) == pin, name
report = read(RUN / 'verification/report.json')
assert (LIB / '.lake/verification/report.json').read_bytes() == (RUN / 'verification/report.json').read_bytes()
assert report['status'] == 'pass'
assert (len(report['declaration_axioms']), len(report['executable_cases']), len(report['source_sha256']), sum(not c['result'] for c in report['executable_cases'])) == (11840, 12438, 2155, 173)
previous = read(RUN / 'previous-verification/report.json')
assert report['executable_cases'] == previous['executable_cases'] + [dict(name=n, result=v) for n, v in plan['cases']]
checker = load('checker', 'artifacts/css-spec-lean/check.py')
extra_axioms = checker.parse_axiom_audit((ROOT / 'artifacts/css-steps-origin-library-proposal-v1/replay/audits.log').read_text())
assert set(extra_axioms) == set(plan['audits'])
assert report['declaration_axioms'] == previous['declaration_axioms'] | extra_axioms
for name in ('axioms.log', 'executable-examples.log'):
    assert (RUN / 'verification' / name).read_bytes().startswith((RUN / 'previous-verification' / name).read_bytes())
for name, command in report['commands'].items():
    assert sha(RUN / 'verification' / (name + '.log')) == command['log_sha256']
    assert sha(LIB / '.lake/verification' / (name + '.log')) == command['log_sha256']
for name, pin in report['source_sha256'].items():
    assert sha(LIB / name) == pin, name
epoch = copy.deepcopy(old_epoch)
epoch['pins'].update({'artifacts/css-spec-lean/' + n: p for n, p in postimages.items()})
nested = h.index_state(LIB, ENV)
for key in ('head', 'entries', 'cached_diff'):
    assert nested[key] == old_epoch['nested_semantic_index'][key]
epoch['nested_semantic_index'] = h.semantic_index(nested)
epoch['counts']['roles'] = len(epoch['pins'])
epoch['steps_origin_application'] = dict(result_sha256=sha(RUN / 'RESULT.json'), report_sha256=sha(RUN / 'verification/report.json'), transferred_audits=10, normative_coverage_delta=0)
verified = a.verify_current(h, ROOT, ENV, epoch)
save('INITIAL-EPOCH.json', epoch)
save('CURRENT-EPOCH.json', epoch)
save('LIBRARY-ROOT-VERIFICATION.json', dict(status='STEPS_ORIGIN_TERMINAL_ROOT_VERIFIED', outer_session=36634, outer_terminal_chunk='ddca02', outer_exit=0, report_sha256=sha(RUN / 'verification/report.json'), counts=result, preservation=verified))
print('Canonical sources, full checker, previous prefixes, both indexes, native sources and binaries verified.', flush=True)
