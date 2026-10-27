import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
proposal = ROOT / 'artifacts/css-integer-resolve-range-repair-v1'
manifest = proposal / 'FILES.json'
assert sha(manifest) == '5300ae417fb473da0dadec498e47d2220c8fe7edb25068fd0fabb7ccf13abb20'
pins = json.loads(manifest.read_text())
source = proposal / 'results/helper.rs'
assert sha(source) == pins['results/helper.rs']
prefix = source.read_text().split('fn main(){', 1)[0]
results = json.loads((HERE / 'results/RESULT.json').read_text())
assert results['all_passed']
rows = []
for name, mode in [('nonnegative', 'NonNegative'), ('at-least-one', 'AtLeastOne'),
                   ('zero-to-one', 'ZeroToOne')]:
    output = (HERE / ('results/omission-' + name + '.stdout')).read_text()
    values = dict(re.findall(r'\((bits|mode|old32|new32|old64|new64) #(x[0-9a-f]+|b[01]+)\)', output))
    assert len(values) == 6
    values = {k: int(v[1:], 16 if v[0] == 'x' else 2) for k, v in values.items()}
    assert values['mode'] == {'NonNegative': 1, 'AtLeastOne': 2, 'ZeroToOne': 3}[mode]
    rows.append((name, mode, values))
main = 'fn main() {\n'
expected = []
for name, mode, values in rows:
    main += '{ let raw = f32::from_bits(' + str(values['bits']) + '); let mode = Mode::' + mode + '; let got = Number(raw).get(); let clamped = mode.clamp(got);\n'
    for role, suffix in [('head90', '32'), ('118', '64')]:
        main += f'println!("{name} {role} {{}} {{}} {{}}", round_{role}(got) as u32, round_{role}(clamped) as u32, context_{role}(raw, mode) as u32);\n'
        expected.append(f"{name} {role} {values['old' + suffix]} {values['new' + suffix]} {values['new' + suffix]}")
    main += '}\n'
main += '}\n'
out = HERE / 'witness-replay'
out.mkdir(exist_ok=False)
(out / 'helper.rs').write_text(prefix + main)
rust = Path('/Users/bgrins/.cargo/bin/rustc')
version = subprocess.check_output([str(rust), '--version'], text=True).strip()
with tempfile.TemporaryDirectory(prefix='range-smt-witness-') as temporary:
    for opt in [0, 2]:
        exe = Path(temporary) / ('witness' + str(opt))
        build = subprocess.run([str(rust), '--edition=2021', '-C', 'overflow-checks=yes',
                                '-C', 'opt-level=' + str(opt), str(out / 'helper.rs'), '-o', str(exe)],
                               capture_output=True, text=True, timeout=60)
        (out / ('build-' + str(opt) + '.log')).write_text(build.stdout + build.stderr)
        assert build.returncode == 0
        run = subprocess.run([str(exe)], capture_output=True, text=True, timeout=10)
        (out / ('run-' + str(opt) + '.log')).write_text(run.stdout + run.stderr)
        assert run.returncode == 0 and not run.stderr
        assert run.stdout.splitlines() == expected
(out / 'RESULT.json').write_text(json.dumps({
    'passed': True, 'witnesses': [dict(name=n, mode_name=m, **v) for n, m, v in rows],
    'rows_per_optimization': len(expected), 'optimizations': [0, 2],
    'source_helper_sha256': sha(source), 'rust_version': version,
    'rust_launcher_sha256': sha(rust), 'temporary_products_removed': True,
    'full_native_pipeline': False,
}, indent=2) + '\n')
print('PASS: three solver witnesses match the extracted Rust facade at opt0 and opt2.')
