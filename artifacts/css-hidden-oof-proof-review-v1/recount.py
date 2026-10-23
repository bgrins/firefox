import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit('use python3 -I -S without optimization')
import hashlib
import itertools
import json
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
PRODUCER = HERE.parent / 'css-hidden-oof-proof-v1'
OUTER = 'd658800dad19383ec18b4dd05f0d903b843a520af84e738812947863c0680a1b'
INNER = '39401a7bfe598270b1eb664182a0ff00eb5904bed7608ab68938a86294b5a363'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def authenticate(root, expected):
    assert sha(root / 'FILES.json') == expected
    roster = json.loads((root / 'FILES.json').read_text())['files']
    for name, digest in roster.items():
        path = root / name
        assert path.is_file() and not path.is_symlink() and sha(path) == digest, name
    return len(roster)

def reference():
    rows = []
    for row, inputs in enumerate(itertools.product(range(3), range(8), range(4), *([range(2)] * 6))):
        timing, dm, hm, ph, next_flow, differs, table, owner, anon = inputs
        bits = [dm & 1, (dm >> 1) & 1, (dm >> 2) & 1]
        secondary = [(hm & 1) * 2, 0, hm & 2]
        hidden = bool(ph and not anon)
        def mark():
            if bits[0]:
                return
            bits[0] = 1
            if bits[1] or table:
                return
            bits[1] = 1
            bits[2] = 1
        if timing == 1 and hidden:
            mark()
        resize = int(not bits[0] and differs)
        if timing == 2 and hidden:
            mark()
        width, height = (0, 0) if hidden and not next_flow else (720, 480)
        if not hidden:
            bits[0] = secondary[0] = 0
        states = [a | b for a, b in zip(bits, secondary)]
        root_eligible, leaf_eligible = int(bool(states[0])), int(bool(states[2]))
        values = [row, *inputs, resize, *states, root_eligible, leaf_eligible,
                  int(bool(leaf_eligible and ph)), 600 + (12000 - width) // 2, 600, width, height]
        rows.append(','.join(map(str, values)))
    assert len(rows) == 6144
    return rows

def main():
    counts = {'outer': authenticate(PRODUCER, OUTER), 'inner': authenticate(PRODUCER / 'capsule', INNER)}
    capsule = PRODUCER / 'capsule'
    proposal = HERE.parent / 'css-hidden-flex-oof-review-v1'
    assert sha(capsule / 'input/candidate.cpp') == sha(proposal / 'candidate-v2-AbsoluteContainingBlock.cpp')
    assert sha(capsule / 'input/candidate.patch') == sha(proposal / 'candidate-v2.patch')
    for module in ['Hidden', 'Subtree']:
        assert sha(capsule / f'lean/{module}.lean') == sha(HERE.parent / 'css-hidden-subtree-proof-v1/capsule/lean' / f'{module}.lean')
    names = re.findall(r'^#print axioms (\S+)$', (capsule / 'lean/Audit.lean').read_text(), re.M)
    assert len(names) == len(set(names)) == 89
    oof_names = ['OOF.' + n for n in re.findall(r'^theorem (\w+)', (capsule / 'lean/OOF.lean').read_text(), re.M)]
    assert [n for n in names if n.startswith('OOF.')] == oof_names and len(oof_names) == 23
    expected = reference()
    mutant_counts = {'omit_mark':512, 'root_only':128, 'physical_parent':3592, 'ignore_anon':1472,
                     'clear_hidden_dirty':1408, 'skip_continuations':768, 'query_clean':736, 'late_mark':128}
    result = {'status':'PASS_SOURCE_ONLY_RECEIPT_RECOUNT', 'authenticated_payloads':counts,
              'fresh_compilation':False, 'independent_reference_rows':len(expected), 'replays':{}}
    for dirname in ['replay-first', 'replay-relocated']:
        replay = PRODUCER / dirname
        audit = (replay / 'lean-audits.stdout').read_text().splitlines()
        actual_names = [re.match(r"'([^']+)'", line).group(1) for line in audit]
        assert actual_names == names
        for line in audit:
            suffix = line.split("'", 2)[2].strip()
            if suffix != 'does not depend on any axioms':
                assert suffix.startswith('depends on axioms: [') and suffix.endswith(']')
                assert set(suffix[len('depends on axioms: ['):-1].split(', ')) <= {'propext','Quot.sound','Classical.choice'}
        assert (replay / 'lean-rows.stdout').read_text().splitlines() == expected
        commands = json.loads((replay / 'COMMANDS.json').read_text())
        for command in commands:
            if command['name'].startswith('false-'):
                assert command['exit'] != 0
                out = (replay / (command['name'] + '.stdout')).read_text()
                assert 'is false' in out and 'error: Tactic `decide`' in out
            else:
                assert command['exit'] == 0, command
            assert not (replay / (command['name'] + '.stderr')).read_text(), command['name']
        for opt in ['O0','O2']:
            assert (replay / f'run-none-{opt}.stdout').read_text().splitlines() == expected
            for mutant, count in mutant_counts.items():
                rows = (replay / f'run-{mutant}-{opt}.stdout').read_text().splitlines()
                assert len(rows) == len(expected)
                assert sum(a != b for a,b in zip(rows, expected)) == count
        result['replays'][dirname] = {'audits':len(names), 'new_audits':len(oof_names),
            'native_rows_per_mode':6144, 'modes':['O0','O2'], 'compiled_mutant_differences_per_mode':mutant_counts,
            'false_claims':4, 'commands_checked':len(commands)}
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()
