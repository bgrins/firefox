import hashlib
import itertools
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys

HERE = Path(__file__).resolve().parent
CAPSULE = HERE / 'relocated-capsule'
OUTPUT = HERE / 'generated'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def check_rows(text, original=False):
    rows = text.splitlines()
    assert len(rows) == 45
    for proc in range(3):
        for mode, left, right in itertools.product(range(3), (False, True), (False, True)):
            i = proc * 15 + mode * 4 + int(left) * 2 + int(right)
            fields = rows[i].split('|')
            assert len(fields) == 9
            assert fields[:5] == [str(i), str(proc), str(mode), str(left).lower(), str(right).lower()]
            if mode:
                assert fields[5:] == ['error', '-', '-', '-']
            else:
                number = [12 * .75 + 8 * .25, 12 + 8, 12 * 2 + 8][proc]
                assert fields[5:] == ['ok', str(int(number)), '17', str(left if original else (left or right)).lower()]
        for j, name in enumerate(('none-none', 'some-none', 'none-some')):
            assert rows[proc * 15 + 12 + j].split('|') == [str(proc * 15 + 12 + j), str(proc), name, 'true']

source = (CAPSULE / 'Provenance.lean').read_text()
names = re.findall(r'^theorem (\w+)', source, re.M)
audits = re.findall(r'^#print axioms (\w+)', source, re.M)
assert names == audits and len(names) == len(set(names)) == 15
assert not re.search(r'\b(sorry|admit|axiom|unsafe)\b', source)
log = (OUTPUT / 'lean.log').read_text().splitlines()
assert log == json.loads((CAPSULE / 'AXIOMS.json').read_text())
for name, line in zip(names, log):
    assert line.startswith("'InterpolationProvenance." + name + "'")
    if 'depends on axioms:' in line:
        allowed = line.split('[')[1].split(']')[0].split(', ')
        assert set(allowed) <= {'propext', 'Quot.sound'}
    else:
        assert line.endswith('does not depend on any axioms')

bindings = json.loads((CAPSULE / 'BINDINGS.json').read_text())
for variant, entries in bindings.items():
    assert len(entries) == 4
    value = CAPSULE / 'source' / ('value.original.rs' if variant == 'omission' else 'value.candidate.rs')
    sources = [value.read_text()] + [(CAPSULE / 'source/animated.rs').read_text()] * 3
    for entry, full in zip(entries, sources):
        assert full.count(entry['body']) == 1
        assert hashlib.sha256(entry['body'].encode()).hexdigest() == entry['sha256']
    assert json.loads((OUTPUT / (variant + '.rs.bindings.json')).read_text()) == entries
old = (CAPSULE / 'source/value.original.rs').read_bytes()
new = (CAPSULE / 'source/value.candidate.rs').read_bytes()
needle = b'attr_tainted: self.attr_tainted,'
assert old.count(needle) == 1
assert old.replace(needle, b'attr_tainted: self.attr_tainted || other.attr_tainted,') == new
candidate = (OUTPUT / 'candidate.rows').read_text()
omission = (OUTPUT / 'omission.rows').read_text()
check_rows(candidate)
check_rows(omission, True)
differences = [i for i, pair in enumerate(zip(candidate.splitlines(), omission.splitlines())) if pair[0] != pair[1]]
assert differences == [1, 16, 31]
rejections = []
for name, corrupt in [('delete', '\n'.join(candidate.splitlines()[:-1]) + '\n'), ('extra', candidate + 'junk\n'), ('nonbinary', candidate.replace('|true', '|2', 1)), ('reorder', '\n'.join([candidate.splitlines()[1], candidate.splitlines()[0]] + candidate.splitlines()[2:]) + '\n')]:
    try:
        check_rows(corrupt)
    except AssertionError:
        rejections.append(name)
    else:
        raise AssertionError(('accepted corrupted rows', name))

scratch = HERE / 'challenge-scratch'
assert not scratch.exists()
scratch.mkdir()
guards = []
for name in ('helper-tamper', 'empty-directory', 'module-shadow', 'symlink', 'duplicate-json', 'path-escape', 'output-inside', 'output-existing'):
    case = scratch / name
    shutil.copytree(CAPSULE, case)
    out = scratch / (name + '-output')
    expected = ''
    if name == 'helper-tamper':
        with (case / 'Driver.rs').open('a') as f:
            f.write('\n// reviewer tamper\n')
        expected = "('hash', 'Driver.rs')"
    elif name == 'empty-directory':
        (case / 'extra').mkdir(); expected = "('directory', 'extra')"
    elif name == 'module-shadow':
        (case / 'json.py').write_text('raise RuntimeError("must not import")\n'); expected = "('entry', 'json.py')"
    elif name == 'symlink':
        (case / 'link').symlink_to(case / 'Driver.rs'); expected = "('entry', 'link')"
    elif name == 'duplicate-json':
        f = case / 'MANIFEST.json'
        f.write_text(f.read_text().replace('{', '{"Driver.rs":"duplicate",', 1)); expected = 'duplicate JSON key'
    elif name == 'path-escape':
        f = case / 'MANIFEST.json'; data = json.loads(f.read_text()); data['../escape'] = '0' * 64
        f.write_text(json.dumps(data)); expected = "assert all(Path(n).as_posix()"
    elif name == 'output-inside':
        out = case / 'new-output'; expected = 'assert out != root'
    else:
        out.mkdir(); expected = 'fresh output directory required'
    cmd = [sys.executable, '-I', '-S', str(case / 'check.py'), '--out', str(out)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    text = r.stdout + r.stderr
    assert r.returncode != 0 and expected in text, (name, r.returncode, text)
    if name != 'output-existing':
        assert not out.exists()
    else:
        assert not list(out.iterdir())
    (HERE / ('guard-' + name + '.log')).write_text(text)
    guards.append({'name': name, 'exit': r.returncode, 'expected_diagnostic': expected, 'rejected_before_generated_output': True})

result = {'verdict': 'bounded component passes independent review', 'theorems_exact': names, 'axioms': ['propext', 'Quot.sound'], 'native_rows_per_variant': 45, 'source_bodies_per_variant': 4, 'compiled_mutant_semantic_mismatches': differences, 'independent_row_rejections': rejections, 'integrity_challenges': guards, 'limits': ['supplied pure payload op and synthetic native payload adapters', 'fixture observers admitted', 'finite expression tree is not effect history', 'zero-weight provenance remains separate normative ambiguity', 'no translation, compiler, provider, scheduling or complete CSS proof', 'isolated nonoptimized Python invocation required by review protocol, not asserted by producer checker']}
(HERE / 'INDEPENDENT-RESULT.json').write_text(json.dumps(result, indent=2) + '\n')
size = sum(p.stat().st_size for p in scratch.rglob('*') if p.is_file() and not p.is_symlink())
shutil.rmtree(scratch)
(HERE / 'CHALLENGE-CLEANUP.json').write_text(json.dumps({'removed_path': str(scratch), 'regular_file_bytes': size, 'retained': 'guard logs and INDEPENDENT-RESULT.json'}, indent=2) + '\n')
print(json.dumps(result))
