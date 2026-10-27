import hashlib,json
from pathlib import Path
import source_check
BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[1]
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
reports=[];paths=set()
for directory,live in [('check-v3',True),('snapshot-check-v1',False)]:
 report=json.loads((BASE/directory/'report.json').read_text())
 if report['status']!='pass' or report['live_native_verified']!=live:raise RuntimeError('Gate status')
 for path,expected in report['inputs'].items():
  if sha(Path(path))!=expected:raise RuntimeError('Gate input drift '+path)
 for path,expected in report['outputs'].items():
  if sha(BASE/directory/path)!=expected:raise RuntimeError('Gate output drift '+path)
 paths.update(Path(p) for p in report['inputs'])
 paths.update(p for p in (BASE/directory).rglob('*') if p.is_file())
 paths.add(BASE/(directory+'.log'));reports.append(report)
source_check.run()
paths.update(BASE/p for p in ['REVIEW.md','SOURCE-COMMIT.md','freeze.py'])
record={'status':'accepted-local-gates','gates':[
 {'report':'check-v3/report.json','session':30514,'exit':0,'live_native_verified':True},
 {'report':'snapshot-check-v1/report.json','session':31949,'exit':0,'live_native_verified':False}],
 'audits':reports[0]['audits'],'compiled_controls':list(reports[0]['controls']),
 'record_controls':reports[0]['corruptions'],'source_controls':reports[0]['source_controls'],
 'pins':{str(p.relative_to(ROOT)):sha(p) for p in sorted(paths)},'scope':reports[0]['scope'],
 'excluded_history':['development-v1.log','development-v2.log','discovery-v1','discovery-v2','discovery-v3','check-v1','check-v2']}
path=BASE/'PROOF-v1.json'
if path.exists():
 if json.loads(path.read_text())!=record:raise RuntimeError('Frozen record drift')
else:path.write_text(json.dumps(record,indent=2,sort_keys=True)+'\n')
print(json.dumps({'proof_sha256':sha(path),'pins':len(record['pins'])}))
