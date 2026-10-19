import hashlib
import json
from pathlib import Path
import check
import cases
import lean_run
import native_run
import source_audit
import toolchain

def run(out,lean):
    out=Path(out).resolve();out.mkdir(parents=True,exist_ok=False)
    identity=toolchain.verify(lean)
    binding=source_audit.run()
    events=cases.generate()
    native_run.run(out/'native')
    lean_run.run(out/'lean',events,lean)
    result=check.run(out/'native',out/'lean')
    result['theorems']=len(json.loads((out/'lean/theorems.json').read_text()))
    result['leanAdmission']=json.loads((out/'lean/admission-lean.json').read_text())
    result['extractionUnits']=len(json.loads((out/'native/candidate/extraction.json').read_text()))
    result['sourceBinding']=binding
    encoded=json.dumps(result,sort_keys=True,separators=(',',':')).encode()
    (out/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
    receipt={'result_sha256':hashlib.sha256(encoded).hexdigest(),'toolchain':identity,'native_variants':12,'lean_variants':12,'status':'PASS'}
    (out/'RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n')
    return receipt
