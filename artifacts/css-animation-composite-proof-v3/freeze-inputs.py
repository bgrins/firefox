from pathlib import Path
import hashlib
import json

root=Path(__file__).resolve().parent
files=[]
for path in sorted(root.iterdir()):
    if path.is_file() and path.name not in ['INPUTS.json','FREEZE.json']:
        files.append(path)
for directory in ['sources','original','candidate','evidence']:
    files.extend(sorted(p for p in (root/directory).rglob('*') if p.is_file()))
rows=[dict(path=str(p.relative_to(root)),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),bytes=p.stat().st_size) for p in sorted(files)]
manifest=dict(schema=1,scope='Complete approved ordinary-WAAPI companion source inputs; development and replay outputs excluded',inputs=rows)
(root/'INPUTS.json').write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n')
print(hashlib.sha256((root/'INPUTS.json').read_bytes()).hexdigest())
