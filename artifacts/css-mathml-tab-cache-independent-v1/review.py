import collections
import hashlib
import itertools
import json
from pathlib import Path


def body(text, name):
    start = text.index(name)
    return text[start:text.index('\n}', start) + 2]


def inspect(root):
    original = (root / 'producer/sources/layout/generic/nsTextFrame.cpp').read_text()
    candidate = (root / 'producer/proposal/nsTextFrame.cpp').read_text()
    name = 'TrimmedOffsets nsTextFrame::GetTrimmedOffsets('
    before, after = body(original, name), body(candidate, name)
    assert original.replace(before, after, 1) == candidate
    expected = before.replace(
        '  if (textStyle->WhiteSpaceIsSignificant()) {',
        '  const bool isMathMLToken = HasAnyStateBits(TEXT_IS_IN_TOKEN_MATHML);\n'
        '  if (textStyle->WhiteSpaceIsSignificant() && !isMathMLToken) {', 1)
    expected = expected.replace('HasAnyStateBits(TEXT_START_OF_LINE)))',
                                'HasAnyStateBits(TEXT_START_OF_LINE) || isMathMLToken))', 1)
    expected = expected.replace('  if (!(aFlags & TrimmedOffsetFlags::NoTrimAfter)',
                                '  if (textStyle->WhiteSpaceIsSignificant()) {\n'
                                '    return offsets;\n  }\n\n'
                                '  if (!(aFlags & TrimmedOffsetFlags::NoTrimAfter)', 1)
    assert expected == after
    helper = body(original, 'static uint32_t GetTrimmableWhitespaceCount(')
    assert helper.count('count < aLength') == 2
    assert 'if (!aLength)' in helper
    reflow = body(original, 'nsTextFrame::ReflowText(')
    for token in ['length = newLineOffset + 1 - offset;',
                  'int32_t skipLength = newLineOffset >= 0 ? length - 1 : length;',
                  'offset + charsFit == newLineOffset',
                  'int32_t contentLength = offset + charsFit - GetContentOffset();',
                  'SetLength(contentLength, &aLineLayout, ALLOW_FRAME_CREATION_AND_DESTRUCTION);']:
        assert token in reflow, token

    def trims(significant, math, no_before, no_after, pre, start, end, version):
        if significant and (version == 'original' or not math):
            return False, False
        leading = not no_before and (pre or start or (math and version != 'original'))
        trailing = not no_after and (pre or end)
        if significant and version != 'mutant':
            trailing = False
        return leading, trailing

    cases = 0
    for flags in itertools.product([False, True], repeat=7):
        sig, math, nb, na, pre, start, end = flags
        old = trims(*flags, 'original')
        new = trims(*flags, 'candidate')
        if not math:
            assert old == new
        assert not (nb and new[0])
        assert not (na and new[1])
        assert not (sig and new[1])
        assert new[1] == old[1]
        cases += 1
    witness = (True, True, False, False, False, False, True)
    assert trims(*witness, 'candidate') == (True, False)
    assert trims(*witness, 'mutant') == (True, True)

    phases = {}
    for phase in ['baseline-v2', 'candidate-v2']:
        receipt = json.loads((root / f'root-evidence/{phase}-receipt.json').read_text())
        assert receipt['pins_before'] == receipt['pins_after']
        assert receipt['all_inputs_unchanged']
        counts = collections.defaultdict(collections.Counter)
        ended = 0
        for line in (root / f'root-evidence/{phase}.jsonl').read_text().splitlines():
            row = json.loads(line)
            if row['action'] in ['test_status', 'test_end']:
                counts[row['test']][row['status']] += 1
            ended += row['action'] == 'suite_end'
        assert ended == 1
        target = '/mathml/relations/css-styling/token-leading-whitespace-range.html'
        expected_counts = {'PASS': 12, 'FAIL': 4, 'OK': 1} if phase == 'baseline-v2' else {'PASS': 16, 'OK': 1}
        assert dict(counts[target]) == expected_counts
        assert dict(counts['/mathml/relations/css-styling/ignored-properties-001.html']) == {'PASS': 260, 'OK': 1}
        phases[phase] = dict(counts)
    a = json.loads((root / 'root-evidence/baseline-v2-receipt.json').read_text())['pins_before']
    b = json.loads((root / 'root-evidence/candidate-v2-receipt.json').read_text())['pins_before']
    changed = sorted(k for k in a.keys() & b.keys() if a[k] != b[k])
    assert changed == ['layout/generic/nsTextFrame.cpp',
                       'objdir-full.noindex/dist/Nightly.app/Contents/MacOS/XUL',
                       'objdir-full.noindex/dist/Nightly.app/Contents/MacOS/firefox']
    assert hashlib.sha256(candidate.encode()).hexdigest() == b['layout/generic/nsTextFrame.cpp']
    return {'status': 'STATIC_REVIEW_PASS', 'branch_combinations': cases,
            'trailing_mutant_rejected': True, 'sole_function_delta': name,
            'root_runtime_counts': phases, 'pair_changed_pins': changed,
            'limits': 'Branch model and retained runtime receipt replay only; no native compilation, browser execution, universal heap or shaping proof.'}
