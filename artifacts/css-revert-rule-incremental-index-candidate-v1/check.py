#!/usr/bin/env python3
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
REL = Path('servo/components/style/properties/cascade.rs')
BASE = ROOT / 'artifacts/css-revert-rule-lazy-index-candidate-v1/candidate' / REL
CANDIDATE = HERE / 'candidate' / REL


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def region(text, start, end):
    return text[text.index(start):text.index(end, text.index(start))]


def main():
    assert digest(BASE) == 'b454e10310175f3c41bbe8cadde6fb8d0b12ee3e1bb900f91422cd44cad453f3'
    before = BASE.read_text()
    after = CANDIDATE.read_text()
    retained = [
        ('struct Declaration<', 'enum DeclarationSources'),
        ('fn substitute_variables_if_needed', 'fn apply_one_longhand'),
        ('fn cascade_custom_property', '/// Fast check to avoid calling'),
    ]
    for start, end in retained:
        assert region(before, start, end) == region(after, start, end), start
    assert after.count('rule_exclusions: None,') == 2
    assert after.count('self.rule_exclusions.get_or_insert_with') == 1
    start = "pub(crate) struct Cascade<'a>"
    expected_tail = before[before.index(start):].replace(
        '.rule_exclusions\n                .as_ref()',
        '.rule_exclusions\n                .as_mut()')
    assert after[after.index(start):] == expected_tail
    assert before[:before.index("type DeclarationSourceIndex<'a>")] == after[:after.index("struct DeclarationSourceIndex<'a>")]
    assert 'containing_block(' not in after and 'fn block_contains(' not in after
    assert 'priority: priority.unimportant(),' in after
    assert 'exclusions.insert(longhand_id, priority, original_declaration)' in after
    with (HERE / 'CHECK.log').open('w') as log:
        def run(command, cwd=None):
            log.write('$ ' + ' '.join(map(str, command)) + '\n')
            log.flush()
            subprocess.run(list(map(str, command)), cwd=cwd, check=True, stdout=log, stderr=subprocess.STDOUT)

        run(['rustfmt', '--config-path', ROOT / 'servo/rustfmt.toml', '--check', CANDIDATE])
        with tempfile.TemporaryDirectory(prefix='css-rule-index-', dir='/private/tmp') as scratch:
            copy = Path(scratch) / REL
            copy.parent.mkdir(parents=True)
            shutil.copy2(BASE, copy)
            run(['patch', '-p1', '--fuzz=0', '--batch', '-i', HERE / 'native.patch'], scratch)
            assert copy.read_bytes() == CANDIDATE.read_bytes()
            run(['patch', '-R', '-p1', '--fuzz=0', '--batch', '-i', HERE / 'native.patch'], scratch)
            assert copy.read_bytes() == BASE.read_bytes()
    result = {
        'base_path': str(BASE.relative_to(ROOT)), 'base_sha256': digest(BASE),
        'candidate_path': str(CANDIDATE.relative_to(HERE)), 'candidate_sha256': digest(CANDIDATE),
        'patch_sha256': digest(HERE / 'native.patch'),
        'format_config_path': 'servo/rustfmt.toml', 'format_config_sha256': digest(ROOT / 'servo/rustfmt.toml'),
        'format_check': True, 'forward_reverse_byte_exact': True,
        'declaration_buffer_and_cutoff_state_unchanged': True,
        'substitution_and_both_dispatchers_unchanged': True,
        'custom_consumer_unchanged': True, 'scratch_removed': True,
        'native_typecheck': False, 'native_build': False, 'browser_run': False,
        'benchmark_run': False, 'status': 'reviewable incremental-index alternative, not adopted',
        'changes_limited_to_index_exclusions_and_mutable_lookup': True,
    }
    (HERE / 'CHECK.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
