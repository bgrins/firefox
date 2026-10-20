from pathlib import Path
import hashlib,json,shutil,subprocess,sys
repo=Path('/Users/bgrins/code/firefox');source=repo/'artifacts/css-variable-terminal-span-proof-v1';root=Path(__file__).resolve().parent/'negatives';root.mkdir()
records=[]
def repin(c):
 h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
 m=json.loads((c/'MANIFEST.json').read_text())
 for n in m:m[n]=h(c/n)
 (c/'MANIFEST.json').write_text(json.dumps(m,indent=2)+'\n')
 f=json.loads((c/'FREEZE.json').read_text());f['manifest_sha256']=h(c/'MANIFEST.json');(c/'FREEZE.json').write_text(json.dumps(f,indent=2)+'\n')
for name in ['changed','missing','extra','symlink','inside-output','optimized','double-optimized','not-isolated','source-binding','audit-roster']:
 c=root/name;shutil.copytree(source,c);output=root/(name+'-output');args=['-I','-S']
 if name=='changed':(c/'lean/Span.lean').write_text((c/'lean/Span.lean').read_text()+'\n')
 elif name=='missing':(c/'lean/Span.lean').unlink()
 elif name=='extra':(c/'EXTRA').write_text('unexpected')
 elif name=='symlink':
  p=c/'source/tokenizer.rs';p.unlink();p.symlink_to(source/'source/tokenizer.rs')
 elif name=='inside-output':output=c/'absent-output'
 elif name=='optimized':args+=['-O']
 elif name=='double-optimized':args+=['-OO']
 elif name=='not-isolated':args=['-S']
 elif name=='source-binding':
  p=c/'source/custom_properties.rs';b=bytearray(p.read_bytes());binding=json.loads((c/'SOURCE-BINDINGS.json').read_text())[0];b[binding['start_byte']]=ord('!');p.write_bytes(b);repin(c)
 elif name=='audit-roster':
  p=c/'AUDITS.json';a=json.loads(p.read_text());a.pop();p.write_text(json.dumps(a));repin(c)
 cmd=[sys.executable,*args,str(c/'check.py'),'--output',str(output)]
 run=subprocess.run(cmd,capture_output=True,text=True)
 record={'name':name,'command':cmd,'exit':run.returncode,'stdout':run.stdout,'stderr':run.stderr,'output_absent':not output.exists()};records.append(record)
 if run.returncode==0 or output.exists():raise RuntimeError(record)
 shutil.rmtree(c)
(root/'RESULT.json').write_text(json.dumps(records,indent=2)+'\n')
print('PASS',len(records),'pre-output rejections')
