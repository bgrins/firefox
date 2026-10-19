import argparse, hashlib, json, pathlib, shutil, subprocess
ROOT = pathlib.Path(__file__).resolve().parent
p = argparse.ArgumentParser()
p.add_argument('--output', type=pathlib.Path, required=True)
a = p.parse_args()
out = a.output.resolve(); out.mkdir(parents=True, exist_ok=False)
relocated = out/'relocated'; shutil.copytree(ROOT, relocated)
records = []
def run(label, cmd, success):
    r = subprocess.run(cmd, text=True, capture_output=True)
    records.append({'label':label,'command':list(map(str,cmd)),'exit':r.returncode,'stdout':r.stdout,'stderr':r.stderr})
    (out/'GATES.json').write_text(json.dumps(records,indent=2)+'\n')
    assert (r.returncode == 0) == success
run('relocated replay', ['python3',str(relocated/'check.py'),'--replay',str(out/'replay')],True)
for i, name in enumerate(['lean/TrackingEpoch.lean','native/witness.rs','vendor/cssparser/src/parser.rs','MANIFEST.json']):
    path = relocated/name; original = path.read_bytes(); path.write_bytes(original+b'\n ')
    destination = out/f'must-not-execute-{i}'
    run('tamper '+name,['python3',str(relocated/'check.py'),'--replay',str(destination)],False)
    assert not destination.exists()
    path.write_bytes(original)
run('restored integrity',['python3',str(relocated/'check.py')],True)
print('PASS: fresh relocated replay and four authentication-before-execution rejections')
