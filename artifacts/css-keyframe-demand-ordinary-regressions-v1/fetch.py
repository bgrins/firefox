from pathlib import Path
import subprocess,json
p=Path(__file__).resolve().parent
files=['css/css-variables/variable-cycles.html','css/css-variables/variable-css-wide-keywords.html','css/css-values/attr-cycle.html','css/css-values/attr-all-types.html']
receipts=[]
for f in files:
 cmd=['searchfox-cli','--get-file','testing/web-platform/tests/'+f]
 r=subprocess.run(cmd,capture_output=True)
 q=p/'upstream'/f;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(r.stdout)
 receipts.append({'command':cmd,'exit_code':r.returncode,'stderr':r.stderr.decode()})
(p/'FETCH.json').write_text(json.dumps(receipts,indent=2)+'\n')
assert all(r['exit_code']==0 for r in receipts)
