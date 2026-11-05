import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
REL = Path('servo/components/style/properties/cascade.rs')
BASE = ROOT / 'artifacts/css-revert-rule-incremental-index-candidate-v1/candidate' / REL
CANDIDATE = HERE / 'candidate' / REL
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()

assert sha(BASE) == 'd32913bd213ebaf1e5bbff4ed7117ec8af0003990807f6a3f2c3f5ed7ded41f1'
before, after = BASE.read_text(), CANDIDATE.read_text()
start = "struct DeclarationSourceIndex<'a>"
end = '#[derive(Clone, Copy, Eq, Hash, PartialEq)]'
assert before[:before.index(start)] == after[:after.index(start)]
assert before[before.index(end):] == after[after.index(end):]
assert 'blocks: FxHashSet<*const PropertyDeclarationBlock>' not in after
assert 'self.blocks' not in after
assert after.count('.contains_key(&(first as *const PropertyDeclaration))') == 1
assert after.count('let Some(first) = block.declarations().first()') == 1
with (HERE / 'CHECK.log').open('w') as log:
    def run(command, cwd=None):
        log.write('$ ' + ' '.join(map(str, command)) + '\n')
        log.flush()
        subprocess.run(list(map(str, command)), cwd=cwd, check=True,
                       stdout=log, stderr=subprocess.STDOUT)

    run(['rustfmt', '--config-path', ROOT / 'servo/rustfmt.toml', '--check', CANDIDATE])
    with tempfile.TemporaryDirectory(prefix='css-owner-map-dedup-', dir='/private/tmp') as temporary:
        copy = Path(temporary) / REL
        copy.parent.mkdir(parents=True)
        shutil.copy2(BASE, copy)
        run(['patch', '-p1', '--fuzz=0', '--batch', '-i', HERE / 'native.patch'], temporary)
        assert copy.read_bytes() == CANDIDATE.read_bytes()
        run(['patch', '-R', '-p1', '--fuzz=0', '--batch', '-i', HERE / 'native.patch'], temporary)
        assert copy.read_bytes() == BASE.read_bytes()
result = {
    'base_sha256': sha(BASE), 'candidate_sha256': sha(CANDIDATE),
    'patch_sha256': sha(HERE / 'native.patch'),
    'format_config_sha256': sha(ROOT / 'servo/rustfmt.toml'),
    'configured_format_check': True, 'forward_reverse_byte_exact_zero_fuzz': True,
    'outside_source_index_byte_unchanged': True, 'scratch_removed': True,
    'native_typecheck': False, 'native_build': False, 'browser_run': False,
    'performance_measured': False, 'adopted': False,
}
(HERE / 'CHECK.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
