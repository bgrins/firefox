from pathlib import Path
import argparse, hashlib, importlib.util, json, os, subprocess, sys
assert sys.flags.isolated and sys.flags.no_site
sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
p = argparse.ArgumentParser()
p.add_argument('--raw', type=Path, required=True)
p.add_argument('--output', type=Path, required=True)
a = p.parse_args()
out = a.output.resolve()
out.mkdir(parents=True, exist_ok=False)
spec = importlib.util.spec_from_file_location('authenticated_state_check', ROOT/'native/check_states.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
cases = json.loads((ROOT/'CASES.json').read_text())
raw = a.raw.read_text()
assert module.check(cases, raw)['complete_trace_equal']
lines = raw.splitlines()
rows = [line.split('|') for line in lines]
results = []

def reject(name, changed):
    text = '\n'.join(changed)+'\n'
    try:
        module.check(cases, text)
    except AssertionError as error:
        results.append({'case': name, 'status': 'REJECTED', 'reason': str(error)})
    else:
        raise AssertionError(('accepted corruption', name))

# Every actual observation is independently required at its exact sequence index.
for i in range(len(lines)):
    reject(f'drop-event-{i}', lines[:i]+lines[i+1:])
    reject(f'duplicate-event-{i}', lines[:i]+[lines[i]]+lines[i:])
    event = rows[i]
    reject(f'unknown-tag-{i}', lines[:i]+['|'.join([event[0], 'unknown', *event[2:]])]+lines[i+1:])
    reject(f'extra-field-{i}', lines[:i]+[lines[i]+'|unexpected']+lines[i+1:])
    reject(f'missing-field-{i}', lines[:i]+['|'.join(event[:-1])]+lines[i+1:])
for i in range(len(lines)-1):
    assert lines[i] != lines[i+1]
    reject(f'swap-adjacent-{i}', lines[:i]+[lines[i+1],lines[i]]+lines[i+2:])
for tag in ['enter','exit','step','slice','bulk','token']:
    reject('drop-all-'+tag,[line for line in lines if line.split('|')[1]!=tag])
for tag in ['step','slice','bulk']:
    chosen = next(i for i,r in enumerate(rows) if r[1]==tag)
    reject('move-'+tag+'-after-token',lines[:chosen]+lines[chosen+1:]+[lines[chosen]])
# Removing a whole seam must not relabel it as a non-URL call.
row = next(r[0] for r in rows if r[1]=='enter')
reject('remove-entire-seam',[line for line in lines if line.split('|')[0]!=row or line.split('|')[1]=='token'])
# Both annotation Option tags and payload are significant.
chosen = next(i for i,r in enumerate(rows) if r[1]=='token')
for suffix in [('some:', 'none'),('none','some:')]:
    event=rows[chosen][:-2]+list(suffix)
    reject('annotation-'+str(suffix),lines[:chosen]+['|'.join(event)]+lines[chosen+1:])

# Reproduce accepted corruptions using the pinned historical v1 validator.
history = ROOT/'validator-history'
manifest = json.loads((history/'MANIFEST.json').read_text())
assert hashlib.sha256((history/'native/check_states.py').read_bytes()).hexdigest()==manifest['native/check_states.py']
previous = []
variants = {
    'drop-all-helpers': [line for line in lines if line.split('|')[1]!='step'],
    'drop-all-bulk': [line for line in lines if line.split('|')[1]!='bulk'],
    'insert-unknown': [lines[0],row+'|unknown',*lines[1:]],
}
for tag in ['slice','step','bulk']:
    i=next(i for i,r in enumerate(rows) if r[1]==tag)
    variants['append-field-'+tag]=lines[:i]+[lines[i]+'|unexpected']+lines[i+1:]
    variants['move-'+tag+'-to-end']=lines[:i]+lines[i+1:]+[lines[i]]
for name, variant in variants.items():
    path=out/(name+'.txt');path.write_text('\n'.join(variant)+'\n')
    command=[sys.executable,'-I','-S',str(history/'native/check_states.py'),'--cases',str(ROOT/'CASES.json'),'--raw',str(path),'--output',str(out/(name+'-v1.json'))]
    done=subprocess.run(command,capture_output=True,text=True,env={k:v for k,v in os.environ.items() if not k.startswith(('PYTHON','LEAN_'))})
    (out/(name+'-v1.log')).write_text(done.stdout+done.stderr)
    assert done.returncode==0,(name,done.stdout,done.stderr)
    reject('historical-'+name,variant)
    previous.append({'case':name,'v1_exit':done.returncode,'v2':'REJECTED','command':command})
reviewer = ROOT/'validator-history/reviewer'
findings = json.loads((reviewer/'FINDINGS.json').read_text())
reviewer_results = []
for record in findings['records']:
    text = (reviewer/(record['name']+'.txt')).read_text()
    assert hashlib.sha256(text.encode()).hexdigest()==record['raw_sha256']
    reject('reviewer-'+record['name'],text.splitlines())
    reviewer_results.append({'case':record['name'],'input_sha256':record['raw_sha256'],'v1_recorded_exit':record['exit'],'v2':'REJECTED'})
receipt={'reviewer_corruptions':reviewer_results,'status':'PASS','fixed_inputs':len(cases),'base_events':len(lines),'rejected':len(results),'checks':results,'historical_acceptances':previous}
(out/'CHECK.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({k:v for k,v in receipt.items()if k!='checks'}))
