import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

review = Path(__file__).resolve().parent
locations = json.loads((review/'V2-LOCATIONS.json').read_text())
base = Path(locations['temporary_root'])/'negative'
base.mkdir()
source = Path(locations['capsule'])
results = []
for name,flags,reason in [
    ('optimized',['-I','-S','-O'],'use python3 -I -S without optimization'),
    ('double-optimized',['-I','-S','-OO'],'use python3 -I -S without optimization'),
    ('nonisolated',['-S'],'use python3 -I -S without optimization'),
    ('site-enabled',['-I'],'use python3 -I -S without optimization'),
    ('source-dispatch-tamper',['-I','-S'],'input hash: source_bindings.py'),
    ('unlisted-precompiled',['-I','-S'],'closed file roster'),
    ('unlisted-empty-directory',['-I','-S'],'closed directory roster'),
    ('symlink-model',['-I','-S'],'nonregular input'),
    ('duplicate-freeze-key',['-I','-S'],'duplicate key'),
    ('output-inside-source',['-I','-S'],'fresh external output required'),
    ('output-symlink-inside',['-I','-S'],'fresh external output required'),
]:
    case = base/name
    capsule = case/'capsule'
    shutil.copytree(source,capsule)
    output = case/'output'
    marker = case/'dispatched'
    if name in ('optimized','double-optimized','source-dispatch-tamper'):
        (capsule/'source_bindings.py').write_text('from pathlib import Path\nPath('+repr(str(marker))+').write_text("dispatched")\n')
    elif name == 'unlisted-precompiled':
        (capsule/'lean/PublicationModel.olean').write_bytes(b'untrusted cache')
    elif name == 'unlisted-empty-directory':
        (capsule/'unused').mkdir()
    elif name == 'symlink-model':
        target = capsule/'lean/PublicationModel.lean'
        target.unlink();target.symlink_to(source/'lean/PublicationModel.lean')
    elif name == 'duplicate-freeze-key':
        freeze = capsule/'FREEZE.json';data=json.loads(freeze.read_text());k='manifest_sha256'
        freeze.write_text('{'+json.dumps(k)+':'+json.dumps(data[k])+','+freeze.read_text()[1:])
    elif name == 'output-inside-source':
        output=capsule/'generated-output'
    elif name == 'output-symlink-inside':
        (case/'alias').symlink_to(capsule,target_is_directory=True)
        output=case/'alias/generated-output'
    cmd=[sys.executable,*flags,str(capsule/'check.py'),'--output',str(output)]
    proc=subprocess.run(cmd,capture_output=True,text=True)
    log=proc.stdout+proc.stderr
    (review/(name+'.log')).write_text(log)
    assert proc.returncode != 0 and reason in log,(name,proc.returncode,log)
    assert not output.exists() and not marker.exists(),name
    results.append({'case':name,'exit':proc.returncode,'expected_reason':reason,'output_created':False,'producer_dispatch_marker_created':False})
(review/'INTEGRITY.json').write_text(json.dumps({'version':'v2','results':results},indent=2)+'\n')
print(json.dumps({'rejections':len(results),'status':'PASS'}))
