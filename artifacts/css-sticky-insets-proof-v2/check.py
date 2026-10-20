import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit("use Python -I -S without -O or -OO")
sys.dont_write_bytecode=True
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path, PurePosixPath
import stat

ROOT=Path(__file__).resolve().parent

def need(condition,message):
    if not condition:raise SystemExit(message)

def decode(text):
    def pairs(items):
        result={}
        for key,value in items:
            need(key not in result,'duplicate JSON key')
            result[key]=value
        return result
    return json.loads(text,object_pairs_hook=pairs)

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def authenticate():
    for name in ['FILES.json','FREEZE.json']:
        need(stat.S_ISREG((ROOT/name).lstat().st_mode),'nonregular seal')
    seal=decode((ROOT/'FREEZE.json').read_text())
    need(seal['manifest_sha256']==digest(ROOT/'FILES.json'),'manifest hash')
    manifest=decode((ROOT/'FILES.json').read_text())
    need(set(manifest)=={'algorithm','files'} and manifest['algorithm']=='sha256','manifest schema')
    files=manifest['files'];need(type(files)==dict and len(files)>0,'empty source closure')
    directories=set()
    for name,sha in files.items():
        q=PurePosixPath(name)
        need(type(name)==str and not q.is_absolute() and q.as_posix()==name and all(x not in ['.','..',''] for x in q.parts),'noncanonical path')
        need(type(sha)==str and len(sha)==64 and all(x in '0123456789abcdef' for x in sha),'hash grammar')
        directories.update(str(x) for x in q.parents if str(x)!='.')
    actual_files=set();actual_dirs=set()
    for base,dirs,names in os.walk(ROOT,followlinks=False):
        for name in dirs+names:
            path=Path(base)/name;relative=path.relative_to(ROOT).as_posix();mode=path.lstat().st_mode
            if stat.S_ISDIR(mode):actual_dirs.add(relative)
            elif stat.S_ISREG(mode):actual_files.add(relative)
            else:raise SystemExit('nonregular entry: '+relative)
    need(actual_files==set(files)|{'FILES.json','FREEZE.json'},'closed file roster')
    need(actual_dirs==directories,'closed directory roster')
    for name,sha in files.items():need(digest(ROOT/name)==sha,'source hash: '+name)
    return manifest

def main():
    args=argparse.ArgumentParser()
    args.add_argument('--output',required=True)
    for name in ['lean','clang','rustc']:args.add_argument('--'+name)
    options=args.parse_args()
    before=authenticate()
    target=Path(options.output).expanduser().resolve()
    need(target!=ROOT and ROOT not in target.parents,'output must be outside source capsule')
    need(not target.exists(),'output must be new')
    toolinfo=decode((ROOT/'TOOLCHAIN.json').read_text());tools={}
    for name,row in toolinfo.items():
        tool=Path(getattr(options,name) or row['path']).resolve()
        need(tool.is_file() and digest(tool)==row['sha256'],'tool hash: '+name)
        tools[name]=str(tool)
    spec=importlib.util.spec_from_file_location('sticky_replay',ROOT/'replay.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    target.mkdir(parents=True)
    result=module.run(target,tools)
    need(authenticate()==before,'source changed during replay')
    (target/'AUTHENTICATION.json').write_text(json.dumps({'status':'pass','manifest_sha256':digest(ROOT/'FILES.json'),'files':len(before['files']),'tools':tools},indent=2)+'\n')
    print(json.dumps({'status':result['status'],'modules':result['modules'],'audits':result['audits'],'output':str(target)}))

if __name__=='__main__':main()
