from pathlib import Path
import argparse, hashlib, json, os, subprocess, sys
assert sys.flags.isolated and sys.flags.no_site
ROOT = Path(__file__).resolve().parents[1]
p = argparse.ArgumentParser()
p.add_argument('--raw', type=Path, required=True)
p.add_argument('--olean', type=Path, required=True)
p.add_argument('--output', type=Path, required=True)
a = p.parse_args()
out = a.output.resolve()
out.mkdir(parents=True, exist_ok=False)
tools = json.loads((ROOT/'TOOLCHAIN.json').read_text())
lean = Path(tools['lean'])
assert hashlib.sha256(lean.read_bytes()).hexdigest() == tools['lean_sha256']
cases = json.loads((ROOT/'CASES.json').read_text())
env = {k:v for k,v in os.environ.items() if not k.startswith(('PYTHON','LEAN_'))}
env['LEAN_PATH'] = str(a.olean.resolve())
command = [str(lean), '--run', str(ROOT/'lean/NativeDriver.lean')]
r = subprocess.run(command, input=''.join(c['input'].encode().hex()+'\n' for c in cases),
                   text=True, capture_output=True, env=env)
(out/'raw.txt').write_text(r.stdout)
(out/'stderr.txt').write_text(r.stderr)
assert r.returncode == 0, r.stderr
native = [line for line in a.raw.read_text().splitlines() if line.split('|')[1] in ('enter','exit')]
model = [line for line in r.stdout.splitlines() if line.split('|')[1] != 'skip']
assert native == model, [(a,b) for a,b in zip(native,model) if a!=b]
seen = [int(line.split('|')[0]) for line in r.stdout.splitlines() if line.split('|')[1] in ('enter','skip')]
assert seen == list(range(len(cases)))
receipt = {'status':'PASS','cases':len(cases),'entry_exit_events':len(native),
           'command':command,'raw_sha256':hashlib.sha256(r.stdout.encode()).hexdigest()}
(out/'CHECK.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt))
