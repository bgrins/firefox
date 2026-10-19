import argparse,hashlib,json,pathlib,shutil,subprocess
p=argparse.ArgumentParser();p.add_argument('--package',type=pathlib.Path,required=True);p.add_argument('--output',type=pathlib.Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
root=a.output/'package';shutil.copytree(a.package,root);records=[]
def run(label, mutate, restore):
    mutate()
    cmd=['python3','-I','-S','-B',str(root/'check.py')]
    r=subprocess.run(cmd,capture_output=True,text=True)
    records.append({'label':label,'command':cmd,'exit':r.returncode,'stdout':r.stdout,'stderr':r.stderr})
    restore()
    assert r.returncode!=0,label
extra=root/'unlisted.py'
run('unlisted source',lambda:extra.write_text('raise RuntimeError("must not execute")\n'),lambda:extra.unlink())
link=root/'unlisted-symlink'
run('unlisted symlink',lambda:link.symlink_to('check.py'),lambda:link.unlink())
listed=root/'native/reference.py'; original=listed.read_bytes(); external=a.output/'same-reference.py';external.write_bytes(original)
def symlink_listed(): listed.unlink();listed.symlink_to(external)
def restore_listed(): listed.unlink();listed.write_bytes(original)
run('listed symlink with correct bytes',symlink_listed,restore_listed)
run('listed source byte tamper',lambda:listed.write_bytes(original+b'\n'),lambda:listed.write_bytes(original))
man=root/'MANIFEST.json';freeze=root/'FREEZE.json';mb=man.read_bytes();fb=freeze.read_bytes();entries=json.loads(mb);first=next(iter(entries))
def update_manifest(text):
    man.write_text(text);f=json.loads(fb);f['manifest_sha256']=hashlib.sha256(man.read_bytes()).hexdigest();freeze.write_text(json.dumps(f)+'\n')
def restore_manifest():man.write_bytes(mb);freeze.write_bytes(fb)
run('duplicate manifest key with matching outer hash',lambda:update_manifest(mb.decode().rstrip()[:-1]+','+json.dumps(first)+':'+json.dumps(entries[first])+'}\n'),restore_manifest)
run('parent path with matching outer hash',lambda:update_manifest(json.dumps({**entries,'../same-reference.py':hashlib.sha256(original).hexdigest()})),restore_manifest)
run('absolute path with matching outer hash',lambda:update_manifest(json.dumps({**entries, str(external.resolve()):hashlib.sha256(original).hexdigest()})),restore_manifest)
cmd=['python3','-B',str(root/'check.py')];r=subprocess.run(cmd,capture_output=True,text=True);assert r.returncode!=0 and 'invoke Python with -I -S' in r.stderr
records.append({'label':'nonisolated invocation','command':cmd,'exit':r.returncode,'stdout':r.stdout,'stderr':r.stderr})
cmd=['python3','-I','-S','-B',str(root/'check.py')];r=subprocess.run(cmd,capture_output=True,text=True);assert r.returncode==0,r.stdout+r.stderr
records.append({'label':'restored authentication','command':cmd,'exit':r.returncode,'stdout':r.stdout,'stderr':r.stderr})
(a.output/'CHECK.json').write_text(json.dumps({'result':'PASS','rejections':len(records)-1,'records':records},indent=2)+'\n')
