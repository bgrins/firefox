import argparse,hashlib,json,shutil,subprocess,re
from pathlib import Path
parser=argparse.ArgumentParser();parser.add_argument('attempt',type=int);parser.add_argument('--cache');parser.add_argument('--select',nargs='+');args=parser.parse_args()
root=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def authenticate():
    for name,e in json.loads((root/'TRANSPORT.json').read_text()).items():
        assert sha(root/'inputs'/name)==e['sha256']==sha(root.parent.parent/e['origin']),name
    assert sha(root.parent/'css-flex-native-schedule-refinement-target-20261112-v1/FILES.json')=='73297f6cfe01d319345d7506fcabc3ba729062b09569f21a527e5c3487d54b12'
authenticate();attempt=root/('development-'+str(args.attempt));attempt.mkdir(exist_ok=False)
shutil.copytree(root/'inputs',attempt/'inputs');(attempt/'output').mkdir()
for name in ['launch.py','check_kernel.py','MODULES.json','ROOTS.json','TRANSPORT.json','IMAGE.json','BASE-MODULES.json']:
    shutil.copyfile(root/name,attempt/name)
modules=json.loads((root/'MODULES.json').read_text())
if args.select:
    required=set(json.loads((root/'BASE-MODULES.json').read_text()))
    def visit(module):
        assert module in modules, module
        if module in required:return
        required.add(module)
        source=(root/'inputs'/(module+'.v')).read_text()
        for clause in re.findall(r'Require\s+(?:Import|Export)\s+(.*?)\.(?=\s|$)',source,re.S):
            for dependency in clause.split():
                if (root/'inputs'/(dependency+'.v')).exists():visit(dependency)
    for module in args.select:visit(module)
    modules=[module for module in modules if module in required]
    (attempt/'SELECTION.json').write_text(json.dumps({'requested':args.select,'modules':modules,'acceptance':False},indent=2)+'\n')
(attempt/'MODULES.json').write_text(json.dumps(modules,indent=2)+'\n')
(attempt/'inputs/MODULES.json').write_text(json.dumps(modules,indent=2)+'\n')
shutil.copyfile(root/'BASE-MODULES.json',attempt/'inputs/BASE-MODULES.json')
pins={str(p.relative_to(root)):sha(p) for p in sorted((root/'inputs').glob('*.v'))}
(attempt/'SOURCE.json').write_text(json.dumps(pins,indent=2)+'\n')
image=json.loads((root/'IMAGE.json').read_text())['Id'];name='css-flex-native-schedule-proof-'+str(args.attempt)
c=['docker','run','--rm','--name',name,'--network=none','--read-only','--cap-drop=ALL','--security-opt=no-new-privileges','--memory=1g','--cpus=1','--pids-limit=128','--tmpfs','/tmp:rw,nosuid,nodev,size=256m','--tmpfs','/work:rw,nosuid,nodev,size=256m','--mount',f'type=bind,source={attempt}/inputs,target=/inputs,readonly','--mount',f'type=bind,source={attempt}/check_kernel.py,target=/check_kernel.py,readonly','--mount',f'type=bind,source={attempt}/output,target=/output',image,'python3','-I','-B','/check_kernel.py']
if args.cache:
    cache=(root/args.cache).resolve()
    assert cache.is_relative_to(root) and cache.name=='base-cache'
    cache_pins=json.loads((cache/'CACHE.json').read_text())
    expected=json.loads((root/'BASE-MODULES.json').read_text())
    assert set(cache_pins)==set(expected)
    for module,entry in cache_pins.items():
        assert sha(root/'inputs'/(module+'.v'))==entry['source_sha256']
        assert sha(cache/(module+'.vo'))==entry['object_sha256']
    c[c.index(image):c.index(image)]=['--mount',f'type=bind,source={cache},target=/cache,readonly']
    (attempt/'CACHE-INPUT.json').write_text(json.dumps({'path':str(cache),'manifest_sha256':sha(cache/'CACHE.json'),'entries':cache_pins},indent=2)+'\n')
(attempt/'COMMAND.json').write_text(json.dumps(c,indent=2)+'\n')
with (attempt/'console.log').open('wb') as log:r=subprocess.run(c,stdout=log,stderr=subprocess.STDOUT)
i=subprocess.run(['docker','ps','-a','--filter','name=^/'+name+'$','--format','{{.ID}}'],capture_output=True,text=True)
receipt={'exit':r.returncode,'container_name':name,'inspection_exit':i.returncode,'inspection_stdout':i.stdout,'inspection_stderr':i.stderr,'container_absent':i.returncode==0 and not i.stdout.strip()}
(attempt/'TERMINAL.json').write_text(json.dumps(receipt,indent=2)+'\n');authenticate()
for path,h in pins.items():assert sha(root/path)==h,path
print(json.dumps(receipt),flush=True);raise SystemExit(r.returncode if receipt['container_absent'] else 2)
