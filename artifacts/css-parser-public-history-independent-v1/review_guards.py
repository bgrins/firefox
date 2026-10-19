from pathlib import Path
import hashlib,json,shutil,subprocess,sys
assert sys.flags.isolated and sys.flags.no_site
R=Path(__file__).resolve().parent
scratch=R/'generated-guards';scratch.mkdir()
out=R/'evidence/guards';out.mkdir(parents=True)
results=[]
for name in ['changed-source','missing-source','shadow-module','symlink-file','symlink-directory','duplicate-manifest-key','extra-directory','not-isolated']:
 p=scratch/name/'capsule';shutil.copytree(R/'package',p)
 if name=='changed-source':
  f=p/'source/parser.rs';f.write_bytes(f.read_bytes()+b'\n')
 elif name=='missing-source':(p/'source/parser.rs').unlink()
 elif name=='shadow-module':(p/'json.py').write_text('raise RuntimeError("SHADOW_EXECUTED")\n')
 elif name=='symlink-file':
  f=p/'source/parser.rs';f.unlink();f.symlink_to(R/'package/source/parser.rs')
 elif name=='symlink-directory':(p/'unlisted-link').symlink_to(R/'package/source',target_is_directory=True)
 elif name=='duplicate-manifest-key':
  f=p/'MANIFEST.json';m=json.loads(f.read_text());k=next(iter(m));f.write_text('{'+json.dumps(k)+':'+json.dumps(m[k])+','+f.read_text()[1:]);z=p/'FREEZE.json';v=json.loads(z.read_text());v['manifest_sha256']=hashlib.sha256(f.read_bytes()).hexdigest();z.write_text(json.dumps(v))
 elif name=='extra-directory':(p/'unlisted').mkdir()
 command=[sys.executable]+([] if name=='not-isolated' else ['-I','-S'])+[str(p/'check.py'),'--run','--output',str(p.parent/'output')]
 r=subprocess.run(command,capture_output=True,text=True)
 (out/(name+'.stdout')).write_text(r.stdout);(out/(name+'.stderr')).write_text(r.stderr)
 assert r.returncode!=0 and not (p.parent/'output').exists() and 'SHADOW_EXECUTED' not in r.stderr
 results.append({'id':name,'command':command,'exit':r.returncode,'output_created':False,'shadow_executed':False})
(out/'CHECK.json').write_text(json.dumps(results,indent=2)+'\n')
print('PASS',len(results),'integrity challenges')
