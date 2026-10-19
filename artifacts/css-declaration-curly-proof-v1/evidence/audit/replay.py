import sys
assert sys.flags.isolated and sys.flags.no_site
import argparse, hashlib, json, subprocess
from pathlib import Path
R = Path(__file__).resolve().parent
p = argparse.ArgumentParser()
p.add_argument('--output', type=Path, required=True)
a = p.parse_args()
out = a.output.resolve()
out.mkdir(parents=True, exist_ok=False)
S = R / 'evidence'
cfg = json.loads((S / 'TOOLCHAIN.json').read_text())
rustc = Path(cfg['rustc'])
assert hashlib.sha256(rustc.read_bytes()).hexdigest() == cfg['rustc_sha256']
commands = []
def run(cmd):
    p = subprocess.run(cmd, cwd=out, capture_output=True, text=True)
    commands.append(dict(command=cmd, exit=p.returncode, stdout=p.stdout, stderr=p.stderr))
    (out / 'COMMANDS.json').write_text(json.dumps(commands, indent=2) + '\n')
    assert p.returncode == 0, p.stderr
    return p.stdout
for name, edition, deps in [('dtoa','2015',[]),('dtoa-short','2015',['dtoa']),('itoa','2018',[]),('smallvec','2018',[]),('cssparser','2024',['dtoa_short','itoa','smallvec'])]:
    crate = name.replace('-', '_')
    cmd = [str(rustc), '--crate-name', crate, '--crate-type', 'rlib', '--edition', edition, '-C', 'opt-level=1', '-L', 'dependency=' + str(out), str(S / 'vendor' / name / 'src/lib.rs'), '-o', str(out / ('lib' + crate + '.rlib'))]
    for dep in deps:
        cmd += ['--extern', dep + '=' + str(out / ('lib' + dep + '.rlib'))]
    run(cmd)
original = (S / 'helper.rs').read_text()
needle = '    // Look for var(), env() and top-level curly blocks after the error.\n'
assert original.count(needle) == 1
candidate = original.replace(needle, '    input.reset(start);\n\n    // Look for var(), env() and top-level curly blocks in the whole value.\n')
results = {}
for mode, helper, expected in [('original', original, 7), ('candidate', candidate, 0)]:
    work = out / mode
    work.mkdir()
    (work / 'helper.rs').write_text(helper)
    (work / 'witness.rs').write_text((R / 'witness.rs').read_text().replace('include!("evidence/helper.rs")', 'include!("helper.rs")'))
    exe = work / 'witness'
    run([str(rustc), '--edition', '2024', '-L', 'dependency=' + str(out), '--extern', 'cssparser=' + str(out / 'libcssparser.rlib'), str(work / 'witness.rs'), '-o', str(exe)])
    rows = [json.loads(x) for x in run([str(exe)]).splitlines()]
    failures = [x for x in rows if x['gateway'] and not x['curly_rule']]
    assert len(rows) == 26 and len(failures) == expected, failures
    results[mode] = dict(rows=rows, forbidden_gateways=failures)
changed = [(a, b) for a, b in zip(results['original']['rows'], results['candidate']['rows']) if a != b]
assert len(changed) == 7
(out / 'RESULT.json').write_text(json.dumps(results, indent=2) + '\n')
print(json.dumps(dict(rows_per_variant=26, old_forbidden_gateways=7, candidate_forbidden_gateways=0, changed=7)))
