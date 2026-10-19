#!/usr/bin/env python3
import sys

if not (sys.flags.isolated and sys.flags.no_site and sys.dont_write_bytecode):
    raise SystemExit('Run with python3 -I -S -B; project imports are forbidden before isolation')

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import runpy
import stat
import subprocess

ROOT=Path(__file__).absolute().parent
RESERVED_DIRS={'development','replay-v3'}
RESERVED_FILES={'FREEZE.json'}


def fail(message):
    raise ValueError(message)


def unique_object(pairs):
    result={}
    for key,value in pairs:
        if key in result:fail('duplicate JSON key: '+key)
        result[key]=value
    return result


def root_descriptor():
    descriptor=os.open('/',os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
    try:
        for part in ROOT.parts[1:]:
            if part in ('.','..'):fail('noncanonical source root')
            child=os.open(part,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=descriptor)
            os.close(descriptor);descriptor=child
        return descriptor
    except BaseException:
        os.close(descriptor)
        raise


def read_regular(parts):
    descriptor=root_descriptor()
    try:
        for part in parts[:-1]:
            child=os.open(part,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=descriptor)
            os.close(descriptor);descriptor=child
        child=os.open(parts[-1],os.O_RDONLY|os.O_NOFOLLOW,dir_fd=descriptor)
        try:
            if not stat.S_ISREG(os.fstat(child).st_mode):fail('not a regular file')
            data=bytearray()
            while True:
                chunk=os.read(child,1024*1024)
                if not chunk:break
                data.extend(chunk)
            return bytes(data)
        finally:os.close(child)
    finally:os.close(descriptor)


def authenticate(expected, strict):
    raw=read_regular(['INPUTS.json'])
    if hashlib.sha256(raw).hexdigest()!=expected:fail('external manifest pin')
    manifest=json.loads(raw,object_pairs_hook=unique_object)
    files={};folded=set();directories=set()
    for row in manifest['inputs']:
        name=row['path']
        if not isinstance(name,str) or not name or '\\' in name:fail('invalid path')
        path=PurePosixPath(name)
        if path.is_absolute() or str(path)!=name or any(p in ('.','..') for p in path.parts):fail('noncanonical or escaping path: '+name)
        if path.parts[0] in RESERVED_DIRS or name in RESERVED_FILES or name=='INPUTS.json':fail('reserved manifest path: '+name)
        if name in files or name.casefold() in folded:fail('duplicate or alias path: '+name)
        if not re.fullmatch('[0-9a-f]{64}',row['sha256']):fail('invalid digest')
        if not isinstance(row['bytes'],int) or row['bytes']<0:fail('invalid size')
        files[name]=row;folded.add(name.casefold())
        for n in range(1,len(path.parts)):directories.add('/'.join(path.parts[:n]))
    if 'check.py' not in files or 'replay.py' not in files:fail('missing executable closure')
    actual_files=set();actual_dirs=set()
    def visit(directory,relative=''):
        for entry in os.scandir(directory):
            name=relative+entry.name
            mode=entry.stat(follow_symlinks=False).st_mode
            if stat.S_ISLNK(mode):fail('symlink rejected: '+name)
            if stat.S_ISDIR(mode):
                if not strict and not relative and name in RESERVED_DIRS:continue
                actual_dirs.add(name);visit(entry.path,name+'/')
            elif stat.S_ISREG(mode):
                if not strict and not relative and name in RESERVED_FILES:continue
                actual_files.add(name)
            else:fail('nonregular inventory entry: '+name)
    visit(ROOT)
    if actual_files != set(files)|{'INPUTS.json'}:fail('unlisted/missing files: '+repr(sorted(actual_files.symmetric_difference(set(files)|{'INPUTS.json'}))))
    if actual_dirs != directories:fail('unlisted/missing directories: '+repr(sorted(actual_dirs.symmetric_difference(directories))))
    contents={'INPUTS.json':raw}
    for name,row in files.items():
        data=read_regular(PurePosixPath(name).parts)
        if len(data)!=row['bytes'] or hashlib.sha256(data).hexdigest()!=row['sha256']:fail('input hash mismatch: '+name)
        contents[name]=data
    return contents


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--manifest-sha',required=True)
    parser.add_argument('--output')
    parser.add_argument('--authenticate-only',action='store_true')
    parser.add_argument('--worker',action='store_true')
    args=parser.parse_args()
    contents=authenticate(args.manifest_sha,args.worker)
    if args.authenticate_only:
        print(json.dumps({'status':'AUTHENTICATED','files':len(contents)-1,'strict':args.worker}));return
    if not args.output:fail('--output required')
    output=Path(args.output).absolute()
    if args.worker:
        sys.path.insert(0,str(ROOT))
        sys.argv=[str(ROOT/'replay.py'),'--output',str(output)]
        runpy.run_path(str(ROOT/'replay.py'),run_name='__main__')
        return
    if output.exists():fail('output must be fresh')
    output.mkdir(parents=True)
    capsule=output/'source-capsule';capsule.mkdir(mode=0o700)
    for name,data in contents.items():
        destination=capsule/name;destination.parent.mkdir(parents=True,exist_ok=True)
        with destination.open('xb') as file:file.write(data)
        destination.chmod(0o444)
    for directory,_,_ in os.walk(capsule,topdown=False):Path(directory).chmod(0o555)
    command=[sys.executable,'-I','-S','-B',str(capsule/'check.py'),'--manifest-sha',args.manifest_sha,'--worker','--output',str(output/'replay')]
    result=subprocess.run(command,cwd=capsule)
    (output/'CAPSULE.json').write_text(json.dumps({'manifest_sha256':args.manifest_sha,'inputs':len(contents)-1,'child_exit':result.returncode,'isolation':['-I','-S','-B'],'inventory':'exact authenticated copied bytes; no outputs or unlisted modules copied'},indent=2)+'\n')
    if result.returncode:raise SystemExit(result.returncode)


if __name__=='__main__':
    try:main()
    except (ValueError,OSError,KeyError,TypeError) as error:
        print('REJECTED: '+str(error),file=sys.stderr)
        raise SystemExit(1)
