import hashlib
import json
import os
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
AUTHOR = ROOT / 'artifacts/css-flex-total-violation-caller-proof-20261111-v1'
REPLAY = ROOT / 'artifacts/css-flex-total-violation-caller-proof-root-replay-20261111-v1'
TARGET = ROOT / 'artifacts/css-flex-total-violation-caller-target-20261111-v1'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text())


def absent(group):
    assert isinstance(group, int) and group > 1
    try:
        os.killpg(group, 0)
    except ProcessLookupError:
        return True
    return False


assert sha(AUTHOR / 'FILES.json') == '6c7df589da4b6728fcc181df1e5742f95875461b29e5d3acdc71f5de0fd1d0bc'
files = read(AUTHOR / 'FILES.json')
assert len(files) == 838
for name, expected in files.items():
    assert sha(AUTHOR / name) == expected, name
assert sha(AUTHOR / 'SOURCE-ONLY.json') == 'dfe63cc51e67be00029c46246caa5afb8fec42dc3c15d3119531e6d7bb9fe3c0'
assert sha(REPLAY / 'SOURCE-ONLY.json') == sha(AUTHOR / 'SOURCE-ONLY.json')
source = read(AUTHOR / 'SOURCE-ONLY.json')
assert len(source) == 44
for name, expected in source.items():
    assert sha(AUTHOR / name) == sha(REPLAY / name) == expected, name
assert sha(TARGET / 'FILES.json') == 'e954d8318eb1dcbdbe892db732b46c87fc0db07813203b77f2e430fa3ada229b'
for name, expected in read(TARGET / 'FILES.json').items():
    assert sha(TARGET / name) == expected, name
for name in ['FlexViolation/Model.lean', 'FlexViolation/Target.lean',
             'FlexViolationCaller/Model.lean', 'FlexViolationCaller/Target.lean']:
    assert sha(REPLAY / 'proof' / name) == sha(TARGET / 'proof' / name), name
names = read(AUTHOR / 'AUDIT-NAMES.json')
assert len(names) == len(set(names)) == 232
for name in ['universal_target', 'initial_target', 'history_target', 'pass_target',
             'selection_target', 'fallback_target', 'completion_target',
             'delta_admission_target', 'joint_target']:
    assert 'FlexViolationCaller.' + name in names
expected_axioms = read(AUTHOR / 'EXPECTED-AXIOMS.json')
order = read(AUTHOR / 'ORDER.json')
refusals = read(AUTHOR / 'REFUSALS.json')
assert len(order) == 27 and len(refusals) == 6
lean = str(ROOT / 'artifacts/stylo-bloom-tools/lean-4.35.0-rc4-darwin_aarch64/bin/lean')
assert sha(Path(lean)) == 'd1d9c26a539f54fe839d2aa7760bf1ac1dd76a30b26e2c9684bebf2900038fcf'
for base in [AUTHOR, REPLAY]:
    run = base / 'verification-1'
    result = read(run / 'RESULT.json')
    assert result == {'status': 'PASS', 'commands': 33, 'scope': 'full caller proof and controls',
        'universal_target_proofs': 1, 'target_conjuncts': 8, 'finite_history_witness_proofs': 3,
        'audit_roots': 232, 'expected_refusals': 6, 'scratch_removed': True, 'groups_absent': True}
    assert not (run / 'scratch').exists()
    original_sources = {name.removeprefix('proof/'): value for name, value in source.items()
                        if name.startswith('proof/')}
    assert read(run / 'SOURCES.json') == original_sources
    for name, expected in original_sources.items():
        assert sha(run / 'source' / name) == expected, name
    commands = read(run / 'COMMANDS.json')
    modules = order + ['refusal-' + name for name in refusals]
    assert len(commands) == len(modules) == 33
    for command, module in zip(commands, modules):
        assert command['module'] == module
        assert command['argv'] == [lean, '-j1', '-M1024', '-DwarningAsError=true',
                                  '-o', module + '.olean', module + '.lean']
        assert command['group_absent'] and absent(command['pgid'])
        log = run / (module.replace('/', '-') + '.log')
        assert sha(log) == command['log_sha256']
        if module.startswith('refusal-'):
            text = log.read_text()
            assert command['exit'] == 1 and text.count('error:') == 1
            assert 'proved that the proposition' in text and 'is false' in text
        else:
            assert command['exit'] == 0
    audits = []
    for line in (run / 'ProofAudit.log').read_text().splitlines():
        match = re.fullmatch(r"'([^']+)' (?:depends on axioms: \[(.*)\]|does not depend on any axioms)", line)
        assert match, line
        axioms = list(filter(None, (match[2] or '').split(', ')))
        assert len(axioms) == len(set(axioms))
        assert set(axioms) == set(expected_axioms[match[1]]) <= {'propext', 'Classical.choice', 'Quot.sound'}
        audits.append(match[1])
    assert audits == names
    assert (run / 'Controls.log').read_text() == (AUTHOR / 'CONTROL-EXPECTED.txt').read_text()
    assert (run / 'Falsify.log').read_text() == '(57, true)\n'
result = {'status': 'ACCEPTED', 'scope': 'original acquired32 caller/history model',
          'target_conjuncts': 8, 'modules': 27, 'exact_audits': 232, 'semantic_refusals': 6,
          'source_inputs': 44, 'author_files': 838, 'root_replay_session': 67844,
          'root_replay_terminal': 'b2a8ac', 'root_replay_exit': 0,
          'source_manifest_sha256': sha(REPLAY / 'SOURCE-ONLY.json'),
          'author_manifest_sha256': sha(AUTHOR / 'FILES.json'),
          'root_result_sha256': sha(REPLAY / 'verification-1/RESULT.json'),
          'current_native_refinement': False, 'wide_provider_correction_covered': False,
          'protected_comparator': False}
(HERE / 'RESULT.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result))
