import sys
assert sys.flags.isolated and sys.flags.no_site
import argparse, hashlib, json, os, re, subprocess
from pathlib import Path
R = Path(__file__).resolve().parent
p = argparse.ArgumentParser()
p.add_argument('--output', type=Path, required=True)
a = p.parse_args()
out = a.output.resolve()
out.mkdir(parents=True, exist_ok=False)
cfg = json.loads((R / 'TOOLCHAIN.json').read_text())
for tool in ['rustc', 'lean']:
    assert hashlib.sha256(Path(cfg[tool]).read_bytes()).hexdigest() == cfg[tool + '_sha256']
env = {k: v for k, v in os.environ.items() if not k.startswith(('LEAN_', 'PYTHON'))}
env['LEAN_PATH'] = str(out)
commands = []
def run(cmd):
    p = subprocess.run(cmd, cwd=out, env=env, capture_output=True, text=True)
    commands.append(dict(command=cmd, exit=p.returncode, stdout=p.stdout, stderr=p.stderr))
    (out / 'COMMANDS.json').write_text(json.dumps(commands, indent=2) + '\n')
    assert p.returncode == 0, p.stdout + p.stderr
    return p.stdout
source = (R / 'lean/DeclarationCurly.lean').read_text()
assert not re.search(r'\b(sorry|axiom|admit|native_decide)\b', source)
names = ['DeclarationCurly.' + n for n in re.findall(r'^theorem\s+(\w+)', source, re.M)]
assert names == json.loads((R / 'THEOREMS.json').read_text())
(out / 'DeclarationCurly.lean').write_text(source)
run([cfg['lean'], '-o', str(out / 'DeclarationCurly.olean'), str(out / 'DeclarationCurly.lean')])
(out / 'Audit.lean').write_text('import DeclarationCurly\n' + ''.join('#print axioms ' + n + '\n' for n in names))
axioms = run([cfg['lean'], str(out / 'Audit.lean')])
for name in names:
    assert axioms.count("'" + name + "'") == 1
for group in re.findall(r'depends on axioms:\s*\[([^\]]*)\]', axioms):
    assert set(re.findall(r'[A-Za-z_][\w.]*', group)) <= {'propext', 'Quot.sound', 'Classical.choice'}
assert axioms.count('depends on axioms:') + axioms.count('does not depend on any axioms') == len(names)
(out / 'AXIOMS.txt').write_text(axioms)
S = R / 'evidence/audit/evidence'
for name, edition, deps in [('dtoa','2015',[]),('dtoa-short','2015',['dtoa']),('itoa','2018',[]),('smallvec','2018',[]),('cssparser','2024',['dtoa_short','itoa','smallvec'])]:
    crate = name.replace('-', '_')
    cmd = [cfg['rustc'], '--crate-name', crate, '--crate-type', 'rlib', '--edition', edition, '-C', 'opt-level=1', '-L', 'dependency=' + str(out), str(S / 'vendor' / name / 'src/lib.rs'), '-o', str(out / ('lib' + crate + '.rlib'))]
    for dep in deps:
        cmd += ['--extern', dep + '=' + str(out / ('lib' + dep + '.rlib'))]
    run(cmd)
old = (S / 'helper.rs').read_text()
needle = '    // Look for var(), env() and top-level curly blocks after the error.\n'
assert old.count(needle) == 1
fixed = old.replace(needle, '    input.reset(start);\n\n    // Look for var(), env() and top-level curly blocks in the whole value.\n')
assert 'if !starts_with_curly_block || !at_start {' in fixed
variants = {
    'original': old,
    'candidate': fixed,
    'omit-rewind': fixed.replace('    input.reset(start);\n\n    // Look for var()', '    // Look for var()'),
    'reject-whole': fixed.replace('if !starts_with_curly_block || !at_start {', 'if true {'),
    'ignore-structure': fixed.replace('if !saw_arbitrary_substitution_functions || invalid {', 'if !saw_arbitrary_substitution_functions {'),
    'lose-positive-query': fixed.replace('saw_arbitrary_substitution_functions = input.seen_arbitrary_substitution_functions();', 'let _ = input.seen_arbitrary_substitution_functions();\n            saw_arbitrary_substitution_functions = false;'),
}
observations = {}
for mode, helper in variants.items():
    work = out / mode
    work.mkdir()
    (work / 'helper.rs').write_text(helper)
    (work / 'witness.rs').write_text((R / 'native-witness.rs').read_text())
    exe = work / 'witness'
    run([cfg['rustc'], '--edition', '2024', '-L', 'dependency=' + str(out), '--extern', 'cssparser=' + str(out / 'libcssparser.rlib'), str(work / 'witness.rs'), '-o', str(exe)])
    rows = [json.loads(x) for x in run([str(exe)]).splitlines()]
    assert len(rows) == 57
    observations[mode] = rows
    (work / 'ROWS.json').write_text(json.dumps(rows, indent=2) + '\n')
assert not any(x['gateway'] and not x['curly_rule'] for x in observations['candidate'])
def row(mode, value, callback='comma'):
    matches = [x for x in observations[mode] if x['mode'] == callback and x['value'] == value]
    assert len(matches) == 1
    return matches[0]
mutations = []
for mode, value, proof in [
    ('omit-rewind', 'serif {var(--x)}', 'suffix_only_counterexample'),
    ('reject-whole', '{var(--x)}', 'reject_whole_mutant_witness'),
    ('ignore-structure', 'serif {var(--x)}', 'ignore_structure_mutant_witness'),
]:
    control, mutant = row('candidate', value), row(mode, value)
    assert control['gateway'] != mutant['gateway']
    assert 'DeclarationCurly.' + proof in names
    mutations.append(dict(name=mode, control=control, mutant=mutant, kernel_witness=proof))
control = row('candidate', 'var(--x)', 'consume-success')
mutant = row('lose-positive-query', 'var(--x)', 'consume-success')
assert control['gateway'] and not mutant['gateway']
mutations.append(dict(name='lose-positive-query', control=control, mutant=mutant, kernel_witness='lost_positive_query_mutant_witness', boundary='injected successful callback; no production-property reachability claim'))
result = dict(theorems=len(names), rows_per_variant=57, variants=list(variants), compiled_mutants=mutations,
    original_forbidden_gateways=sum(x['gateway'] and not x['curly_rule'] for x in observations['original']),
    candidate_forbidden_gateways=0,
    changed_original_candidate=sum(x != y for x, y in zip(observations['original'], observations['candidate'])))
(out / 'RESULT.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result))
