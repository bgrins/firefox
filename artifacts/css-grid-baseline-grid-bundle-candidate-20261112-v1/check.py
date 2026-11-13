import difflib
import hashlib
import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ORIGINAL = HERE / 'original'
CANDIDATE = HERE / 'candidate'
NAMES = ['layout/generic/nsGridContainerFrame.cpp',
         'layout/generic/nsGridContainerFrame.h',
         'layout/generic/nsFrameStateBits.h']
BIT = 'NS_STATE_GRID_PRODUCED_BASELINES'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def between(text, start, end):
    first = text.index(start)
    return text[first:text.index(end, first)]


pins = json.loads((HERE / 'ORIGINALS.json').read_text())
for name in NAMES:
    assert sha(ORIGINAL / name) == pins[name]['sha256']
old = (ORIGINAL / NAMES[0]).read_text()
new = (CANDIDATE / NAMES[0]).read_text()
old_key = between(old, '  struct Key final {', '  Key mKey;')
assert old_key == between(new, '  struct Key final {', '  Key mKey;')
assert between(old, '  bool IsValidFor(', '  const MeasuringReflowResult* Result(') == between(
    new, '  bool IsValidFor(', '  Maybe<MeasuringReflowResult> Result(')
old_switch = between(old, '    switch (aRequest) {', '    return result;')
new_switch = between(new, '    switch (aRequest) {', '    result.mHasBaseline =')
assert old_switch.replace('result.mBaseline', 'baseline') == new_switch
assert 'result.mHasBaseline = baseline.isSome();' in new
assert 'grid->HasAnyStateBits(' + BIT + ') &&\n          !grid->IsSubtreeDirty()' in new
assert 'GeometryOnly' not in new
assert 'if (aRequest == MeasuringReflowRequest::Geometry) {\n        return result;\n      }' in new
assert 'mSnapshot = aSnapshot;' in new
assert new.count('mHasGridBaselines = true;') == 1
assert new.count('NS_STATE_GRID_PRODUCED_BASELINES') == 3
start = 'void nsGridContainerFrame::Reflow('
old_reflow = between(old, start, '\n}')
new_reflow = between(new, start, '\n}')
assert new_reflow == old_reflow.replace(
    '  NormalizeChildLists();', '  RemoveStateBits(' + BIT + ');\n  NormalizeChildLists();') + '\n  AddStateBits(' + BIT + ');'
assert old_reflow.count('return;') == 2
assert new_reflow.index('RemoveStateBits(' + BIT) < new_reflow.index('IsHiddenByContentVisibility') < new_reflow.index('IsFrameTreeTooDeep')
assert new_reflow.rindex('CalculateBaselines(') < new_reflow.index('AddStateBits(' + BIT)
old_measure = between(old, 'MeasuringReflowResult MeasuringReflow(', '\n}')
new_measure = between(new, 'MeasuringReflowResult MeasuringReflow(', '\n}')
expected = old_measure.replace('const auto* result = cachedMeasurement->Result(aRequest)',
                               'const auto result = cachedMeasurement->Result(aRequest)')
expected = expected.replace('return aRequest == MeasuringReflowRequest::Geometry\n                 ? result->GeometryOnly()\n                 : *result;', 'return *result;')
expected = expected.replace('const auto result = GridItemCachedBAxisMeasurement::Capture(',
                            'const auto snapshot = GridItemCachedBAxisMeasurement::Capture(')
expected = expected.replace('          childRI.ComputedLogicalBorderPadding(wm).BStartEnd(wm), aRequest);',
                            '          childRI.ComputedLogicalBorderPadding(wm).BStartEnd(wm), aRequest);\n  const auto result = snapshot.Project(aRequest);')
expected = expected.replace('Update(aChild, aCBSize, aRequest, result)', 'Update(aChild, aCBSize, snapshot)')
expected = expected.replace('CachedBAxisMeasurement(aChild, aCBSize, aRequest, result)',
                            'CachedBAxisMeasurement(aChild, aCBSize, snapshot)')
assert expected == new_measure
old_header = (ORIGINAL / NAMES[1]).read_text()
new_header = (CANDIDATE / NAMES[1]).read_text()
assert new_header.replace('    RemoveStateBits(' + BIT + ');\n', '') == old_header
assert new_header.count(BIT) == 1
old_bits = (ORIGINAL / NAMES[2]).read_text()
new_bits = (CANDIDATE / NAMES[2]).read_text()
addition = '\n\n// Both grid baseline axes were produced by the current Reflow.\nFRAME_STATE_BIT(GridContainer, 31, ' + BIT + ')'
assert new_bits.replace(addition, '') == old_bits
inventory = [(group, int(bit), name) for group, bit, name in re.findall(
    r'FRAME_STATE_BIT\((\w+),\s*(\d+),\s*(\w+)\)', old_bits)]
assert not any(bit == 31 and group in ['Generic', 'GridContainer'] for group, bit, name in inventory)
assert sorted(bit for group, bit, name in inventory if group == 'GridContainer') == list(range(20, 31))
patch = ''.join(''.join(difflib.unified_diff((ORIGINAL / name).read_text().splitlines(True),
                                           (CANDIDATE / name).read_text().splitlines(True),
                                           fromfile='a/' + name, tofile='b/' + name))
                for name in NAMES)
(HERE / 'CHANGES.patch').write_text(patch)
commands = []
with tempfile.TemporaryDirectory(prefix='source-roundtrip-', dir=HERE) as scratch:
    scratch = Path(scratch)
    for name in NAMES:
        (scratch / name).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ORIGINAL / name, scratch / name)
    for reverse in [False, True]:
        argv = ['/usr/bin/patch', '-p1', '--batch'] + (['-R'] if reverse else []) + ['-i', str(HERE / 'CHANGES.patch')]
        result = subprocess.run(argv, cwd=scratch, text=True, capture_output=True, timeout=10)
        commands.append(dict(argv=argv, exit=result.returncode, stdout=result.stdout, stderr=result.stderr))
        assert result.returncode == 0
        for name in NAMES:
            assert (scratch / name).read_bytes() == ((ORIGINAL if reverse else CANDIDATE) / name).read_bytes()
result = dict(status='PASS source-only invariants and three-file patch transport',
              originals={name: sha(ORIGINAL / name) for name in NAMES},
              candidate={name: sha(CANDIDATE / name) for name in NAMES},
              key_and_dirty_admission_unchanged=True, original_single_query_switch_preserved=True,
              whole_snapshot_replacement=True, geometry_answer_cleared=True,
              constructor_entry_tail_certificate_checked=True,
              bundle_requires_produced_bit_and_clean_subtree=True,
              grid_bit31_originally_free=True, commands=commands,
              scratch_removed=True, compiled=False, native_execution=False)
(HERE / 'CHECK.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
