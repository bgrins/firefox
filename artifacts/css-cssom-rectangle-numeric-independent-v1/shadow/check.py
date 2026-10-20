import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit('Require python3 -I -S without optimization')
sys.dont_write_bytecode = True

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import stat
import subprocess

ROOT = Path(__file__).resolve().parent

def fail(s):
    raise SystemExit(s)

def pairs(entries):
    out = {}
    for k,v in entries:
        if k in out: fail('Duplicate key')
        out[k] = v
    return out

def load(path):
    return json.loads(path.read_text(), object_pairs_hook=pairs)

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def authenticate(expected):
    if sha(ROOT/'FILES.json') != expected: fail('Manifest mismatch')
    entries = load(ROOT/'FILES.json')
    dirs = set()
    for name in entries:
        p = Path(name)
        if p.is_absolute() or str(p) != name or '..' in p.parts: fail('Invalid path')
        if '__pycache__' in p.parts or p.suffix in {'.pyc','.olean','.o'}: fail('Generated input')
        dirs.update(str(x) for x in p.parents if str(x) != '.')
    actual, actual_dirs = set(), set()
    for p in ROOT.rglob('*'):
        mode = p.lstat().st_mode
        if stat.S_ISDIR(mode): actual_dirs.add(p.relative_to(ROOT).as_posix())
        elif stat.S_ISREG(mode): actual.add(p.relative_to(ROOT).as_posix())
        else: fail('Nonregular entry')
    if actual != set(entries)|{'FILES.json'} or actual_dirs != dirs: fail('Roster mismatch')
    for name,h in entries.items():
        if sha(ROOT/name) != h: fail('Input mismatch: '+name)

def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--files-sha256',required=True)
    ap.add_argument('--output',required=True)
    a = ap.parse_args()
    authenticate(a.files_sha256)
    out = Path(a.output).resolve()
    if out.exists() or out == ROOT or ROOT in out.parents: fail('Output must be new and external')
    tools = load(ROOT/'TOOLS.json')
    for tool in tools.values():
        if sha(Path(tool['path'])) != tool['sha256']: fail('Tool mismatch')
    lean = next(v['path'] for k,v in tools.items() if k.endswith('/lean'))
    out.mkdir(parents=True)
    model = (ROOT/'lean/Edges.lean').read_text()
    names = load(ROOT/'AUDITS.json')
    if re.findall(r'^theorem (\w+)',model,re.M) != names: fail('Audit roster mismatch')
    path = out/'Audit.lean'
    path.write_text(model+'\n'+'\n'.join('#print axioms RectangleNumeric.'+n for n in names)+'\n')
    r = subprocess.run([lean,str(path)],capture_output=True,text=True)
    (out/'lean.log').write_text(r.stdout+r.stderr)
    if r.returncode: fail('Lean failed')
    reports = re.findall(r"'RectangleNumeric\.(\w+)' (?:does not depend on any axioms|depends on axioms: \[([^\]]*)\])",r.stdout)
    if [x[0] for x in reports] != names: fail('Audit output mismatch')
    for _,axs in reports:
        if set(x.strip() for x in axs.split(',') if x.strip())-{'propext','Quot.sound','Classical.choice'}:
            fail('Unauthorized axiom')
    false_claims = [
      'example : observe narrow (grid (-7858324)) (grid 6000) = 6553600 := by decide',
      'example : observe narrow (grid (-8382488)) (grid 6001) = 6553600 := by decide',
      'example : appRound 2147483648 = 0 := by decide']
    for i,claim in enumerate(false_claims):
        p=out/('false-'+str(i)+'.lean')
        p.write_text(model+'\nopen RectangleNumeric\n'+claim+'\n')
        r=subprocess.run([lean,str(p)],capture_output=True,text=True)
        (out/(p.stem+'.log')).write_text(r.stdout+r.stderr)
        if r.returncode == 0 or 'error:' not in r.stdout+r.stderr: fail('False claim survived')
    reference=module('reference',ROOT/'native/reference.py')
    native=module('native_run',ROOT/'native/run.py')
    native_receipt=native.run(out/'native',reference)
    bindings=load(out/'native/BINDINGS.json')
    if bindings != load(ROOT/'BINDINGS.json'): fail('Extraction binding mismatch')
    runtime=[]
    for profile in ['release','project']:
        r=load(ROOT/(profile+'-RESULT.json'))
        if not r['stable'] or r['before'] != r['after']: fail('Unstable runtime')
        rows=r['observations'][0]['rows']
        if len(rows)!=56: fail('Runtime row roster')
        selected=[x for x in rows if x['kind']=='non-flex']
        if len(selected)!=8: fail('Non-flex row roster')
        for row in selected:
            horizontal=row['axis']=='horizontal'
            end='right' if horizontal else 'bottom'
            size='inlineSize' if horizontal else 'blockSize'
            large=row['basis']>1000
            expected=100.015625 if large else 100
            if row['item']['bounding'][end]!=expected: fail('Runtime end mismatch')
            if row['marker']['bounding'][end]!=100: fail('Marker mismatch')
            if row['scalar']['missing']: fail('Missing RO callback')
            actual=row['scalar']['values']['box']['borderBoxSize'][0][size]
            scalar=reference.pipeline(6000-(8388488 if large else 7208),8388488 if large else 7208,60,1)[3]
            if actual!=scalar: fail('RO scalar mismatch')
        runtime.append({'profile':profile,'rows':len(rows),'nonflex_calibrations':len(selected)})
    result={'status':'PASS','audits':len(names),'axioms':dict(reports),'false_claims':len(false_claims),
            'native':native_receipt,'bindings':len(bindings),'runtime':runtime,'manifest':a.files_sha256}
    (out/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
    authenticate(a.files_sha256)
    print(json.dumps({'status':'PASS','audits':len(names),'native_cases':len(reference.CASES),'bindings':len(bindings)}))

if __name__ == '__main__': main()
