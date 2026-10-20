import hashlib,json,pathlib,shutil,subprocess,sys
root=pathlib.Path(__file__).resolve().parent
source=root.parent/'css-animation-base-metadata-proof-v1'
scratch=root/'guard-targets';scratch.mkdir(exist_ok=False)
inputs=json.loads((source/'MANIFEST.json').read_text());rows=[]
for kind,expect in [('modified','input hash'),('missing','closed file roster'),('extra','closed file roster'),('symlink','nonregular input'),('duplicate-json','duplicate JSON key'),('nonisolated','isolated nonoptimized Python required'),('optimized','isolated nonoptimized Python required'),('output-alias','fresh external output required')]:
 base=scratch/kind;capsule=base/'capsule';capsule.mkdir(parents=True)
 for n in [*inputs,'MANIFEST.json','FREEZE.json']:
  p=capsule/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source/n,p)
 output=base/'output'
 if kind=='modified':(capsule/'lean/BaseModel.lean').write_text((capsule/'lean/BaseModel.lean').read_text()+'\n')
 if kind=='missing':(capsule/'Driver.lean').unlink()
 if kind=='extra':(capsule/'unexpected.txt').write_text('extra\n')
 if kind=='symlink':
  p=capsule/'Driver.lean';p.unlink();p.symlink_to(source/'Driver.lean')
 if kind=='duplicate-json':
  p=capsule/'FREEZE.json';s=p.read_text();p.write_text(s.replace('{','{"status":"duplicate",',1))
 flags=['-I','-S']
 if kind=='nonisolated':flags=[]
 if kind=='optimized':flags=['-I','-S','-O']
 if kind=='output-alias':
  alias=base/'alias';alias.symlink_to(capsule,target_is_directory=True);output=alias/'new-output'
 command=[sys.executable,*flags,str(capsule/'check.py'),'--output',str(output)]
 p=subprocess.run(command,capture_output=True,text=True)
 log=p.stdout+p.stderr;(root/(kind+'-guard.log')).write_text(log)
 assert p.returncode!=0 and expect in log and not output.exists(),(kind,log)
 rows.append(dict(id=kind,exit=p.returncode,expected_reason=expect,output_created=False,command=command))
(root/'GUARDS.json').write_text(json.dumps(rows,indent=2)+'\n')
print(json.dumps(rows))
