from pathlib import Path
import hashlib, json, subprocess, tempfile
P = Path(__file__).resolve().parent
ROOT = P.parents[1]
r = json.loads((P/'SOURCES.json').read_text())
h = lambda b: hashlib.sha256(b).hexdigest()
assert h((P/'instrumentation.patch').read_bytes()) == r['patch_sha256']
with tempfile.TemporaryDirectory(prefix='css-feedback-') as tmp:
    t=Path(tmp)
    for n,v in r['files'].items():
        base=subprocess.check_output(['git','-c','core.fsmonitor=false','show',r['revision']+':'+n],cwd=ROOT)
        assert h(base)==v['base_sha256'],n
        dest=t/n
        dest.parent.mkdir(parents=True,exist_ok=True)
        dest.write_bytes(base)
    subprocess.run(['git','apply','--check',str(P/'instrumentation.patch')],cwd=t,check=True)
    subprocess.run(['git','apply',str(P/'instrumentation.patch')],cwd=t,check=True)
    for n,v in r['files'].items():
        assert (t/n).read_bytes()==(P/'source'/n).read_bytes(),n
        assert h((t/n).read_bytes())==v['instrumented_sha256'],n
    subprocess.run(['git','apply','--reverse',str(P/'instrumentation.patch')],cwd=t,check=True)
    for n,v in r['files'].items():
        assert h((t/n).read_bytes())==v['base_sha256'],n
print('PASS: four Git bases; patch apply, exact output, reverse restoration in scratch only')
