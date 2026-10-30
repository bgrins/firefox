import collections
import difflib
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
sha = lambda body: hashlib.sha256(body).hexdigest()


def parse(path):
    lines = path.read_text().splitlines(True)
    files = {}
    index = 0
    while index < len(lines):
        if not lines[index].startswith('--- '):
            index += 1
            continue
        assert lines[index + 1].startswith('+++ b/')
        name = lines[index + 1][6:].strip()
        index += 2
        hunks = []
        while index < len(lines) and lines[index].startswith('@@ '):
            header = re.fullmatch(r'@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@[^\n]*\n', lines[index])
            assert header
            index += 1
            old, new = [], []
            while index < len(lines) and lines[index][:1] in (' ', '+', '-') and not lines[index].startswith('--- '):
                line = lines[index]
                if line[0] != '+': old.append(line[1:])
                if line[0] != '-': new.append(line[1:])
                index += 1
            assert len(old) == int(header[2] or 1) and len(new) == int(header[4] or 1)
            hunks.append((old, new))
        files[name] = hunks
    return files


def apply(body, hunks):
    lines = body.decode().splitlines(True)
    locations = []
    cursor = 0
    for old, new in hunks:
        matches = [i for i in range(cursor, len(lines) - len(old) + 1) if lines[i:i + len(old)] == old]
        assert len(matches) == 1
        position, = matches
        locations.append(position)
        lines[position:position + len(old)] = new
        cursor = position + len(new)
    return ''.join(lines).encode(), locations


source = 'dom/base/nsLineBreaker.cpp'
language_patch = ROOT / 'artifacts/css-line-break-language-fix-v1/fix-candidate-v2.patch'
nowrap_patch = ROOT / 'artifacts/css-nowrap-standalone-formatted-v1/fix.patch'
language, nowrap = parse(language_patch), parse(nowrap_patch)
base = (ROOT / 'artifacts/css-nowrap-standalone-formatted-v1/original.cpp').read_bytes()
assert sha(base) == 'c8b2d4f760e6976bb954eae77983da6b5ea795cdac6ac03db214680e5bd745ea'
old_language, _ = apply(base, language[source])
assert sha(old_language) == '441570e5accda05efcc8618a060af7f14eea396fbf07470f3942152909648404'
nowrap_base, _ = apply(base, nowrap[source])
assert sha(nowrap_base) == 'a87f4210c39f99f27e78df7827b2836362098ff7cd5290a88660d5f943052e03'
candidate, locations = apply(nowrap_base, language[source])
other_order, _ = apply(old_language, nowrap[source])
assert candidate == other_order
restored, _ = apply(candidate, [(new, old) for old, new in language[source]])
assert restored == nowrap_base
payloads = {source: candidate}
for name, hunks in language.items():
    if name != source:
        payloads[name], _ = apply(b'', hunks)
expected_tests = {
    'testing/web-platform/tests/css/css-text/line-break/line-break-language-latin1-partitions.html': '0b304a726d7ce7ebd6c9f080eb1de772b8eee7268115fb34244bd290b0da1d5b',
    'testing/web-platform/tests/css/css-text/line-break/line-break-language-text-partitions.html': '66845fdb6776a311767e2dcbcc86d33163294dd3eb7101d7251185702d86e285',
}
assert set(payloads) == {source, *expected_tests}
for name, pin in expected_tests.items(): assert sha(payloads[name]) == pin
patch = ''
for name, body in payloads.items():
    before = nowrap_base if name == source else b''
    patch += ''.join(difflib.unified_diff(before.decode().splitlines(True), body.decode().splitlines(True), fromfile='a/' + name if before else '/dev/null', tofile='b/' + name))
for name, body in [('base.cpp', nowrap_base), ('candidate.cpp', candidate), ('fix.patch', patch.encode())]:
    with (HERE / name).open('xb') as stream: stream.write(body)
for name in expected_tests:
    target = HERE / 'tests' / name.removeprefix('testing/web-platform/tests/')
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open('xb') as stream: stream.write(payloads[name])
roundtrip = parse(HERE / 'fix.patch')
assert apply(nowrap_base, roundtrip[source])[0] == candidate
assert apply(candidate, [(new, old) for old, new in roundtrip[source]])[0] == nowrap_base

runtime = ROOT / 'artifacts/css-nowrap-native-pair-runtime-1'
assert sha((runtime / 'FILES.json').read_bytes()) == 'f4bb8776b2d4c9b3746210143073f8c44456fec6e15140941b44f1eb5aaf9f7c'
inventory = json.loads((runtime / 'FILES.json').read_bytes())
observations = {}
for role in ('original', 'candidate'):
    name = role + '-wpt-regression/ASSESSMENT.json'
    body = (runtime / name).read_bytes()
    assert sha(body) == inventory[name]['sha256']
    assessment = json.loads(body)
    assert assessment['complete']
    observations[role] = {page: dict(collections.Counter(row['status'] for row in assessment['rows'] if row['test'] == page)) for page in sorted({row['test'] for row in assessment['rows']}) if 'language-' in page or 'hyphenate-limit-chars' in page}
assert observations['original'] == observations['candidate']
result = {'base_sha256': sha(nowrap_base), 'candidate_sha256': sha(candidate), 'patch_sha256': sha(patch.encode()), 'language_native_hunks': len(language[source]), 'exact_unique_context_offsets': locations, 'both_composition_orders_identical': True, 'exact_reverse_restores_nowrap': True, 'test_sha256': expected_tests, 'fresh_nowrap_pair_observations': observations, 'native_build_or_browser_run': False, 'formatting_recheck_pending': True, 'source_worktree_git_index_modified': False}
with (HERE / 'REBASE.json').open('x') as stream: stream.write(json.dumps(result, indent=2, sort_keys=True) + '\n')
print(json.dumps(result, sort_keys=True))
