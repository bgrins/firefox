from pathlib import Path
import sys,json,shutil,subprocess,hashlib,os
assert sys.flags.isolated and sys.flags.no_site
source=Path(sys.argv[1]).resolve();out=Path(sys.argv[2]).resolve();out.mkdir(parents=True,exist_ok=False)
manifest=json.loads((source/'MANIFEST.json').read_text());freeze=json.loads((source/'FREEZE.json').read_text());assert hashlib.sha256((source/'MANIFEST.json').read_bytes()).hexdigest()==freeze['manifest_sha256']
for name,h in manifest.items():assert hashlib.sha256((source/name).read_bytes()).hexdigest()==h
cases=['changed-source','missing-source','shadow-module','symlink-file','symlink-directory','duplicate-manifest-key','extra-directory','not-isolated']
results=[]
for name in cases:
 root=out/name/'capsule';shutil.copytree(source,root);target=root/'lean/PublicCache.lean';marker=out/name/'SHADOW-EXECUTED'
 if name=='changed-source':target.write_bytes(target.read_bytes()+b'\n')
 elif name=='missing-source':target.unlink()
 elif name=='shadow-module':(root/'json.py').write_text('from pathlib import Path\nPath('+repr(str(marker))+').touch()\n')
 elif name=='symlink-file':target.unlink();target.symlink_to(source/'lean/PublicCache.lean')
 elif name=='symlink-directory':shutil.rmtree(root/'vendor');(root/'vendor').symlink_to(source/'vendor',target_is_directory=True)
 elif name=='duplicate-manifest-key':
  raw=(root/'MANIFEST.json').read_text();key=next(iter(manifest));raw=raw.rstrip()[:-1]+','+json.dumps(key)+':'+json.dumps(manifest[key])+'}\n';(root/'MANIFEST.json').write_text(raw)
  f=json.loads((root/'FREEZE.json').read_text());f['manifest_sha256']=hashlib.sha256(raw.encode()).hexdigest();(root/'FREEZE.json').write_text(json.dumps(f))
 elif name=='extra-directory':(root/'unlisted').mkdir()
 output=out/name/'output';cmd=[sys.executable,*([] if name=='not-isolated' else ['-I','-S']),str(root/'check.py'),'--run','--output',str(output)]
 env={k:v for k,v in os.environ.items() if not k.startswith(('PYTHON','LEAN_'))}
 r=subprocess.run(cmd,capture_output=True,text=True,env=env,timeout=30);(out/name/'stdout.txt').write_text(r.stdout);(out/name/'stderr.txt').write_text(r.stderr)
 assert r.returncode!=0 and not output.exists() and not marker.exists(),name
 results.append({'case':name,'exit':r.returncode,'output_created':output.exists(),'shadow_executed':marker.exists(),'command':cmd,'stderr_sha256':hashlib.sha256(r.stderr.encode()).hexdigest()})
(out/'CHECK.json').write_text(json.dumps({'status':'PASS','cases':results,'note':'Duplicate-key case updates only its local internal seal to reach duplicate-key rejection; external parent hash authentication would already reject it.'},indent=2)+'\n');print('PASS',len(results),'pre-execution integrity challenges')
