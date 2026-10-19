from pathlib import Path
import json,hashlib,shutil,subprocess,sys
root=Path(__file__).resolve().parent
src=root/'relocated-source'
work=root/'guard-work'; work.mkdir()
results=[]
for name in ['modified','missing','extra','symlink','duplicate-json','unsafe-name','nonisolated','optimized','output-alias']:
 d=work/name;shutil.copytree(src,d)
 args=[sys.executable,'-I','-S',str(d/'check.py')]
 out=work/(name+'-output')
 expected={'modified':'input hash','missing':'closed file roster','extra':'closed file roster','symlink':'nonregular input','duplicate-json':'duplicate JSON key','unsafe-name':'unsafe input name','nonisolated':'isolated nonoptimized Python required','optimized':'isolated nonoptimized Python required','output-alias':'fresh external output required'}[name]
 if name=='modified': (d/'lean/Model.lean').write_text((d/'lean/Model.lean').read_text()+'\n')
 if name=='missing': (d/'lean/Model.lean').unlink()
 if name=='extra': (d/'extra.txt').write_text('extra')
 if name=='symlink':
  (d/'lean/Model.lean').unlink();(d/'lean/Model.lean').symlink_to(src/'lean/Model.lean')
 if name=='duplicate-json':
  (d/'MANIFEST.json').write_text('{"x":"a","x":"b"}\n')
 if name=='unsafe-name':
  m=json.loads((d/'MANIFEST.json').read_text());h=m.pop('lean/Model.lean');m['lean/../lean/Model.lean']=h
  (d/'MANIFEST.json').write_text(json.dumps(m))
  # Closed roster rejects a noncanonical alias before the dedicated spelling gate.
  expected='closed file roster'
 if name in ['duplicate-json','unsafe-name']:
  s=json.loads((d/'FREEZE.json').read_text());s['manifest_sha256']=hashlib.sha256((d/'MANIFEST.json').read_bytes()).hexdigest();(d/'FREEZE.json').write_text(json.dumps(s))
 if name=='nonisolated':args=[sys.executable,'-S',str(d/'check.py')]
 if name=='optimized':args=[sys.executable,'-I','-S','-O',str(d/'check.py')]
 if name=='output-alias': out=d/'lean'/'..'/'in-source-output'
 args+=['--output',str(out)]
 p=subprocess.run(args,capture_output=True,text=True)
 (root/(name+'.log')).write_text(p.stdout+p.stderr)
 assert p.returncode!=0 and expected in p.stdout+p.stderr and not out.exists(),name
 results.append({'name':name,'command':args,'exit':p.returncode,'expected_reason':expected,'no_output':True})
(root/'GUARDS.json').write_text(json.dumps(results,indent=2)+'\n')
print(json.dumps(results))
