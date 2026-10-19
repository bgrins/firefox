import collections
import hashlib
import itertools
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PROBE = ROOT / 'artifacts/css-ahom-lf-partition-probe-v1'
RESEARCH = ROOT / 'artifacts/css-line-break-language-proof-v1/research'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def authenticate(root, expected):
    assert sha(root / 'MANIFEST.json') == expected
    m = json.loads((root / 'MANIFEST.json').read_text())['files']
    for name, digest in m.items():
        path = root / name
        assert not path.is_symlink() and path.resolve().is_relative_to(root)
        assert sha(path) == digest, name
    return m


def main():
    pins = json.loads((HERE / 'INPUTS.json').read_text())
    for name, digest in pins.items():
        assert sha(ROOT / name) == digest, name
    candidate = RESEARCH / 'ahom-candidate-native-v1'
    cm = authenticate(candidate, '336dffbe6116e4e0c6233467019ab3e0ebcc0b3d860ac563937aaa4252c31e0c')
    adjudication = RESEARCH / 'ahom-lf-adjudication-v1'
    am = authenticate(adjudication, '3006affbbffae8bed60d1b508e6fb732e83ec98908e41a3081015a11bef67db0')
    target = '/css/css-text/line-breaking/complex-prefix-lf-partition.html'
    receipts = {}
    rows = {}
    counts = {}
    for phase in ['paired-original-v1', 'paired-candidate-v1']:
        receipt = json.loads((PROBE / (phase + '-receipt.json')).read_text())
        raw = [json.loads(line) for line in (PROBE / (phase + '.jsonl')).read_text().splitlines()]
        statuses = [r for r in raw if r.get('action') in ['test_status', 'test_end']]
        assert statuses == receipt['statuses']
        assert sum(r.get('action') == 'suite_end' for r in raw) == 1
        assert receipt['pins_before'] == receipt['pins_after']
        assert receipt['absent_before'] == receipt['absent_after']
        for name, digest in receipt['pins_before'].items():
            snapshot = PROBE / (phase + '-sources') / name.replace('/', '__')
            if snapshot.exists():
                assert sha(snapshot) == digest, name
            else:
                assert name.endswith(('/MacOS/XUL', '/MacOS/firefox'))
        by_test = collections.defaultdict(collections.Counter)
        keyed = {}
        for row in statuses:
            key = (row['test'], row.get('subtest'))
            assert key not in keyed
            keyed[key] = row['status']
            by_test[row['test']][row['status']] += 1
        assert dict(by_test) == receipt['counts']
        receipts[phase], rows[phase], counts[phase] = receipt, keyed, dict(by_test)
    before, after = rows.values()
    assert before.keys() == after.keys()
    failures = {(target, f'ahom {white} normal {transform} narrow {partition}')
                for white, transform, partition in itertools.product(
                    ['pre-wrap', 'pre-line'], ['none', 'capitalize'],
                    ['before-lf', 'nested-before-lf'])}
    assert {key for key, status in before.items() if status == 'FAIL'} == failures
    assert all(after[key] == 'PASS' for key in failures)
    assert all(before[key] == after[key] for key in before if key not in failures)
    assert counts['paired-original-v1'][target] == {'PASS': 305, 'FAIL': 8, 'OK': 1}
    assert counts['paired-candidate-v1'][target] == {'PASS': 313, 'OK': 1}
    oldpins, newpins = [r['pins_before'] for r in receipts.values()]
    changed = {p for p in oldpins if oldpins[p] != newpins[p]}
    gate = json.loads((PROBE / 'ROOT-NATIVE-WPT-v1.json').read_text())
    assert changed == set(gate['changed_pins'])
    for phase, expected in gate['paired_receipts'].items():
        assert sha(PROBE / (phase + '-receipt.json')) == expected
    src = 'third_party/rust/icu_segmenter/src/line.rs'
    cargo = 'third_party/rust/icu_segmenter/.cargo-checksum.json'
    a = (PROBE / 'paired-original-v1-sources' / src.replace('/', '__')).read_text()
    b = (PROBE / 'paired-candidate-v1-sources' / src.replace('/', '__')).read_text()
    binding = json.loads((candidate / 'inputs/SOURCE-BINDING.json').read_text())
    assert a == (candidate / binding['source']).read_text()
    assert b == (candidate / binding['candidate']).read_text()
    projected = a
    for old, new in binding['replacements']:
        marker = 'impl LineBreakType for Utf16 {'
        start = projected.index(marker)
        end = projected.index('#[cfg(test)]', start)
        body = projected[start:end]
        assert body.count(old) == 1
        projected = projected[:start] + body.replace(old, new) + projected[end:]
    assert projected == b
    checksums = [json.loads((PROBE / (phase + '-sources') / cargo.replace('/', '__')).read_text())
                 for phase in receipts]
    assert checksums[0]['files']['src/line.rs'] == oldpins[src]
    assert checksums[1]['files']['src/line.rs'] == newpins[src]
    checksums[0]['files']['src/line.rs'] = newpins[src]
    assert checksums[0] == checksums[1]
    patch = PROBE / 'fix-utf16-complex-v1.patch'
    standalone = json.loads((PROBE / 'STANDALONE-v1.json').read_text())
    assert sha(patch) == standalone['patch_sha256']
    headers = [line.split()[2][2:] for line in patch.read_text().splitlines() if line.startswith('diff --git ')]
    assert set(headers) == set(standalone['files']) and len(headers) == 3
    replay = json.loads((PROBE / 'ROOT-FULL-REPLAY-v2.json').read_text())
    assert replay['exit_code'] == 0 and replay['inputs'] == len(cm)
    assert sha(PROBE / 'root-full-replay-v2.log') == replay['log_sha256']
    authenticate(PROBE / 'root-full-replay-v2', replay['manifest_sha256'])
    for actual, expected in [('build/RESULT.json', 'evidence/RESULT.json'),
                             ('build/kernel/RESULT.json', 'evidence/KERNEL-RESULT.json')]:
        assert json.loads((PROBE / 'root-full-replay-v2' / actual).read_text()) == json.loads((candidate / expected).read_text())
    result = {'source_inputs_authenticated': len(cm), 'adjudication_inputs_authenticated': len(am),
              'raw_status_identities': len(before), 'improvements': sorted(x[1] for x in failures),
              'unchanged_statuses': len(before) - len(failures), 'counts': counts,
              'changed_pair_pins': sorted(changed), 'exact_source_delta': True,
              'checksum_only_source_hash_changed': True,
              'patch_sha256': sha(patch),
              'independent_full_native_replay': 'root fresh relocated replay passed; this audit checks its retained results'}
    (HERE / 'RESULT.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: v for k, v in result.items() if k not in ['counts', 'improvements']}, indent=2))


if __name__ == '__main__':
    main()
