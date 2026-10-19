import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'development-build/full';records=[]
for name,renames in [('extract-firstline.py',[('event-types.hpp','scan-event-types.hpp'),('firstline-types.hpp','scan-firstline-types.hpp'),('event-{flavor}','scan-event-{flavor}'),('firstline-{flavor}','scan-firstline-{flavor}'),('firstline-extraction.json','scan-firstline-extraction.json')]),('extract-firstline-reflow.py',[('firstline-types.hpp','scan-firstline-types.hpp'),('firstline-reflow-types.hpp','scan-firstline-reflow-types.hpp'),('firstline-{flavor}','scan-firstline-{flavor}'),('firstline-reflow-{flavor}','scan-firstline-reflow-{flavor}'),('firstline-reflow-extraction.json','scan-firstline-reflow-extraction.json')])]:
 source=ROOT/'native'/name;program=source.read_text()
 for before,after in renames:
  assert before in program,(name,before);program=program.replace(before,after)
 if name=='extract-firstline-reflow.py':
  program=program.replace("ROOT/'native/scan-firstline-reflow-types.hpp'","ROOT/'native/firstline-reflow-types.hpp'")
  program=program.replace("ROOT/'native/scan-firstline-reflow-invoke.cpp'","ROOT/'native/firstline-reflow-invoke.cpp'")
 exec(compile(program,str(source),'exec'),{'__file__':str(source),'__name__':'__main__'})
 records.append({'source':str(source.relative_to(ROOT)),'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'renames':renames})
(OUT/'scan-firstline-extractor-adaptations.json').write_text(json.dumps(records,indent=2)+'\n')
