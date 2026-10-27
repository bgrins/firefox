import copy
import hashlib
import json
from pathlib import Path

import epoch

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
read = lambda p: json.loads(p.read_text())
for name, pin in read(HERE / 'REFERENCES.json').items():
    assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == pin, name
old = read(ROOT / 'artifacts/css-pending-121-131-signing-execution-v2/CURRENT-EPOCH.json')
sources = read(ROOT / 'artifacts/css-keyframe-operation-descriptor-runtime-v1/SOURCE-PINS.json')
binaries = read(ROOT / 'artifacts/css-keyframe-operation-descriptor-runtime-v1/GTEST-RESULT.json')['binaries_after']
ledgers = [
    'artifacts/stylo-bloom-tools/CURRENT-COMMITS.json',
    'artifacts/stylo-bloom-tools/PLAN-OF-RECORD.md',
    'artifacts/stylo-bloom-tools/BUGFIX-COMMITS.md',
    'artifacts/css-fix-readout-20261023/STATUS.md',
    'artifacts/css-fix-readout-20261023/GROUPS.json',
    'artifacts/css-fix-readout-20261023/README.md',
]
check = dict(status='POST_SIGNING_LEDGER_ROOT_VERIFIED', index_empty=True,
             native_and_binary_bodies_unchanged=True, head=old['semantic_index']['head'],
             ledger_paths=ledgers, roles=len(old['pins']))
provenance = {n: {'path': 'synthetic-only', 'sha256': '0' * 64} for n in (
    'build', 'compile_sources', 'gtest_attempt', 'gtest_results', 'packaging_validation',
    'post_signing_epoch', 'post_signing_check', 'signing_execution', 'signing_manifest',
    'failed_reconciliation')}
def run(value):
    return epoch.derive(old, value, check, sources, binaries, ledgers, provenance)
assert run(old)['pins'] == old['pins']
cases = []
def reject(label, change):
    value = copy.deepcopy(old)
    change(value)
    try:
        run(value)
    except AssertionError:
        cases.append(label)
    else:
        raise AssertionError(label)
reject('compiled source changed', lambda d: d['pins'].__setitem__(next(iter(sources)), '0' * 64))
reject('tested binary changed', lambda d: d['pins'].__setitem__(next(iter(binaries)), '0' * 64))
reject('old role dropped', lambda d: d['pins'].pop(next(iter(sources))))
reject('installed identity changed', lambda d: d['installed_identities'].__setitem__(next(iter(d['installed_identities'])), [0, 0]))
reject('untracked addition dropped', lambda d: d['untracked_native'].pop())
reject('extra native modification', lambda d: d['modified_native_paths'].append('synthetic-extra'))
reject('old research dropped', lambda d: d['committed_research_working_payloads'].pop(next(iter(d['committed_research_working_payloads']))))
reject('staging nonempty', lambda d: d['staged_working'].__setitem__('synthetic', '0' * 64))
reject('nested index changed', lambda d: d['nested_semantic_index'].__setitem__('head', '0' * 40))
print(json.dumps({'status': 'SOURCE_ADAPTER_INERT_CHECK_PASS', 'rejections': cases,
                  'synthetic_positive_only': True, 'actual_post_signing_validation': False,
                  'live_verify_executed': False, 'capture_activation': False}, indent=2))
