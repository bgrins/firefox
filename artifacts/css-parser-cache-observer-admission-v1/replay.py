import argparse, hashlib, json, os, pathlib, shutil, subprocess
ROOT = pathlib.Path(__file__).resolve().parent
p = argparse.ArgumentParser()
p.add_argument('--output', type=pathlib.Path, required=True)
a = p.parse_args()
out = a.output.resolve()
out.mkdir(parents=True, exist_ok=False)
lean = pathlib.Path('/Users/bgrins/code/firefox/artifacts/stylo-bloom-tools/lean-4.35.0-rc4-darwin_aarch64/bin/lean')
assert hashlib.sha256(lean.read_bytes()).hexdigest() == 'd1d9c26a539f54fe839d2aa7760bf1ac1dd76a30b26e2c9684bebf2900038fcf'
commands = []
def run(cmd, cwd=out, env=None, good=True):
    r = subprocess.run(cmd, cwd=cwd, env=env, text=True, capture_output=True)
    commands.append({'command': [str(x) for x in cmd], 'cwd': str(cwd), 'exit': r.returncode, 'stdout': r.stdout, 'stderr': r.stderr})
    (out/'COMMANDS.json').write_text(json.dumps(commands, indent=2)+'\n')
    assert (r.returncode == 0) == good, r.stdout+r.stderr
    return r
for name in ['TrackingEpoch.lean', 'Audit.lean']:
    shutil.copyfile(ROOT/'lean'/name, out/name)
env = dict(os.environ, LEAN_PATH=str(out))
run([str(lean), '-o', str(out/'TrackingEpoch.olean'), str(out/'TrackingEpoch.lean')], env=env)
r = run([str(lean), str(out/'Audit.lean')], env=env)
assert r.stdout.count('depends on axioms') + r.stdout.count('does not depend on any axioms') == 10
for line in r.stdout.splitlines():
    if 'depends on axioms' in line:
        allowed = {'propext', 'Quot.sound', 'Classical.choice'}
        names = line.partition('[')[2].partition(']')[0]
        assert set(x.strip() for x in names.split(',') if x.strip()) <= allowed
base = (ROOT/'lean/TrackingEpoch.lean').read_text()
for name, old, new, witness in [
    ('lost-fresh-observation', '⟨b, s.seen || b⟩', '⟨b, s.seen⟩', '(nativeStep ⟨false, false⟩ (.fresh true)).seen = false'),
    ('lost-raw-observation', '⟨s.cache, s.seen || b⟩', '⟨s.cache, s.seen⟩', '(nativeStep ⟨false, false⟩ (.raw true)).seen = false'),
]:
    mutant = base.replace(old, new, 1)
    assert mutant != base
    definitions = mutant.split('theorem step_inv')[0] + '\nexample : '+witness+' := by decide\nend TrackingEpoch\n'
    m = out/(name+'-definitions.lean'); m.write_text(definitions)
    run([str(lean), str(m)], env=env)
    m = out/(name+'.lean'); m.write_text(mutant)
    failed = run([str(lean), str(m)], env=env, good=False)
    assert 'unsolved goals' in failed.stdout or 'Type mismatch' in failed.stdout
run(['python3', str(ROOT/'native/build.py'), '--output', str(out/'native')])
print(json.dumps({'result':'PASS','lean_modules':2,'axiom_audits':10,'semantic_mutants':2,'native_cases':14}))
