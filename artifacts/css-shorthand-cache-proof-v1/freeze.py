import hashlib,json
from pathlib import Path
import source_check
BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
report=json.loads((BASE/'check-v2/report.json').read_text())
if report['status']!='pass':raise RuntimeError('Gate not accepted')
for path,expected in report['inputs'].items():
 if sha(Path(path))!=expected:raise RuntimeError('Gate input drift: '+path)
for path,expected in report['outputs'].items():
 if sha(BASE/'check-v2'/path)!=expected:raise RuntimeError('Gate output drift: '+path)
source_check.run()
paths=set(Path(p) for p in report['inputs'])
paths.update(p for p in (BASE/'check-v2').rglob('*') if p.is_file())
paths.update(BASE/p for p in ['check-v2.log','REVIEW.md','freeze.py'])
record={'status':'accepted-local-gate','gate_session':37319,'gate_exit':0,'gate_report':'check-v2/report.json',
 'audits':report['audits'],'compiled_controls':list(report['controls']),'record_controls':report['corruptions'],
 'source_controls':report['source_controls'],'pins':{str(p.relative_to(ROOT)):sha(p) for p in sorted(paths)},
 'scope':report['scope'],'excluded_history':['Provenance-discovery-full-key.lean','development-v1.log','development-v2.log','development-v3.log','controls-discovery-v1','controls-discovery-v1.log','check-v1','check-v1.log']}
path=BASE/'PROOF-v1.json'
if path.exists():
 if json.loads(path.read_text())!=record:raise RuntimeError('Frozen proof changed')
else:path.write_text(json.dumps(record,indent=2,sort_keys=True)+'\n')
print(json.dumps({'proof_sha256':sha(path),'pins':len(record['pins'])}))
