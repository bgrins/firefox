import hashlib
import itertools
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
LAB = ROOT / 'artifacts/css-named-range-group-order-candidate-20261110-v1'


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def load(p):
    return json.loads(p.read_text())


def expected(records):
    groups = {}
    for position, (key, prop) in enumerate(records):
        groups.setdefault(key, {})[prop] = position
    return list(groups.items())


def candidate(records, rotate_early=False):
    groups, positions, reused = [], [], set()
    for position in reversed(range(len(records))):
        key, prop = records[position]
        matches = [i for i, row in enumerate(groups) if row[0] == key]
        if matches:
            index = matches[0]
            if rotate_early:
                groups.append(groups.pop(index))
                positions.append(positions.pop(index))
                index = len(groups) - 1
            reused.add(index)
            positions[index] = position
        else:
            index = len(groups)
            groups.append((key, []))
            positions.append(position)
        groups[index][1].append((prop, position))
        assert len(groups) == len(positions)
        assert len(set(positions)) == len(positions)
        assert all(i < len(groups) for i in reused)
    for i in reused:
        seen = set()
        groups[i] = (groups[i][0], [(p, v) for p, v in groups[i][1] if p not in seen and not seen.add(p)])
    ordered = sorted(zip(groups, positions), key=lambda x: x[1])
    return [(k, dict(values)) for (k, values), _ in ordered]


def main():
    patch = LAB / 'range-order.patch'
    assert sha(patch) == 'c0884212b8fb2d574395950c8e08abb754614809abe36983bd606accd61725cd'
    sources = load(LAB / 'SOURCES.json')
    for base, pins in [(LAB / 'source', sources), (HERE / 'support', load(HERE / 'SUPPORT.json'))]:
        for p, digest in pins['files'].items():
            data = subprocess.check_output(['git', '-c', 'core.fsmonitor=false', 'show', pins['revision'] + ':' + p], cwd=ROOT)
            assert data == (base / p).read_bytes() and hashlib.sha256(data).hexdigest() == digest
    paths = list(sources['files']) + ['testing/web-platform/tests/scroll-animations/css/named-range-group-earliest-order.html']
    with tempfile.TemporaryDirectory(prefix='range-order-independent-') as d:
        scratch = Path(d)
        for p in sources['files']:
            dest = scratch / p
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(LAB / 'source' / p, dest)
        subprocess.run(['patch', '--batch', '-p1', '-i', str(patch)], cwd=scratch, check=True, capture_output=True)
        for p in paths:
            assert (scratch / p).read_bytes() == (LAB / 'candidate' / p).read_bytes()
        subprocess.run(['patch', '--batch', '-R', '-p1', '-i', str(patch)], cwd=scratch, check=True, capture_output=True)
        for p in sources['files']:
            assert (scratch / p).read_bytes() == (LAB / 'source' / p).read_bytes()
        assert not (scratch / paths[-1]).exists()
    before = (LAB / 'source/servo/ports/geckolib/glue.rs').read_text()
    after = (LAB / 'candidate/servo/ports/geckolib/glue.rs').read_text()
    begin = before.index('    // After appending the missing initial and final keyframes,')
    finish = before.index('\n    true\n}', begin)
    start_after = after.index('    // Keep range group indices stable')
    end_after = after.index('\n    true\n}', start_after)
    assert before[:begin] == after[:start_after] and before[finish:] == after[end_after:]
    inner_before = before[begin:finish]
    inner_after = after[start_after:end_after]
    declaration_start = '        match step.value {'
    declaration_end = '\n    remove_duplicated_property_value_entry('
    assert inner_before[inner_before.index(declaration_start):inner_before.index(declaration_end)] == inner_after[inner_after.index(declaration_start):inner_after.index(declaration_end)]
    assert inner_after.index('remove_duplicated_property_value_entry(') < inner_after.index('.drain(..)') < inner_after.index('sort_unstable_by_key')
    assert '.enumerate().rev()' in inner_after
    assert 'keyframe_source_positions[matched_idx] = source_position;' in inner_after
    assert 'keyframe_source_positions.push(source_position);' in inner_after
    count = 0
    alphabet = list(itertools.product(range(3), range(2)))
    for n in range(7):
        for records in itertools.product(alphabet, repeat=n):
            assert candidate(records) == expected(records)
            count += 1
    witness = [(0, 0), (1, 0), (2, 0), (1, 0), (0, 0)]
    assert candidate(witness, rotate_early=True) != expected(witness)
    evidence = {str(p.relative_to(ROOT)): sha(p) for p in [patch, LAB/'SOURCES.json', LAB/'Slots.lean', *[LAB/'candidate'/p for p in paths]]}
    (HERE / 'INPUTS.json').write_text(json.dumps(evidence, indent=2)+'\n')
    print(json.dumps({'status':'PASS','patch_sha256':sha(patch),'Git_source_pins':6,'forward_reverse_replay':True,'native_exterior_and_declaration_loop_unchanged':True,'finite_abstract_sequences':count,'symbols':6,'max_length':6,'early_rotation_stale_slot_mutant_rejected':True,'native_build_or_browser_run':False},indent=2))


if __name__ == '__main__':
    main()
