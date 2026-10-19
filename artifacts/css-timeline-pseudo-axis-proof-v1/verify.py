#!/usr/bin/env python3
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import types

BASE=Path(__file__).resolve().parent

def sha(path):
    with path.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def authenticate(expected=None):
    manifest_path=BASE/'SOURCE-MANIFEST-v1.json'
    if expected:assert sha(manifest_path)==expected,'manifest authentication failed'
    manifest=json.loads(manifest_path.read_text())
    for entry in manifest['files']:
        p=BASE/entry['path']
        assert p.resolve().is_relative_to(BASE) and not p.is_symlink()
        assert sha(p)==entry['sha256'],('source authentication failed',entry['path'])
    assert sha(BASE/'APPROVED-PLAN-MANIFEST-v1.json')=='aa7411303a53066eb27ee52aea8553898bd1494e6f25890842c6917e6b92762c'
    assert sha(BASE/'APPROVED-SCOPE-v1.md')=='1dd60fe961ac0ebde0c9decd1f8e708e4c5e692f4636c087f41b45378815d2ed'
    approved=json.loads((BASE/'APPROVED-PLAN-MANIFEST-v1.json').read_text())
    for entry in approved['files']:
        if entry['path'].split('/')[0] in ['original','candidate','providers','spec']:
            assert sha(BASE/'source'/entry['path'])==entry['sha256'],('approved source drift',entry['path'])
    return manifest

def tools(lock):
    leanroot=Path(lock['lean']['root'])
    for entry in lock['lean']['files']:
        assert sha(leanroot/entry['path'])==entry['sha256'],('Lean toolchain drift',entry['path'])
    for entry in [lock['cxx']['binary'],lock['cxx']['sdk_settings'],lock['python']['binary']]+lock['cxx']['headers']+lock['python']['files']:
        assert sha(Path(entry['path']))==entry['sha256'],('external dependency drift',entry['path'])
    assert Path(sys.executable).resolve()==Path(lock['python']['executable'])

def helpers():
    sys.dont_write_bytecode=True
    for name in ['cases','extract','native_model','oracle','mutants','replay']:
        p=BASE/f'{name}.py'
        module=types.ModuleType(name);module.__file__=str(p);sys.modules[name]=module
        exec(compile(p.read_bytes(),str(p),'exec'),module.__dict__)
    return sys.modules['replay']

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--expected-manifest')
    parser.add_argument('--replay',type=Path)
    parser.add_argument('--clean',type=Path)
    parser.add_argument('--live',type=Path)
    args=parser.parse_args()
    manifest=authenticate(args.expected_manifest)
    if args.live:
        for suffix in ['cpp','h']:
            assert sha(args.live/f'dom/animation/ScrollTimeline.{suffix}')==sha(BASE/f'source/candidate/ScrollTimeline.{suffix}')
    if not args.replay and not args.clean:
        print(json.dumps(dict(authenticated=len(manifest['files']),manifest_sha256=sha(BASE/'SOURCE-MANIFEST-v1.json'))));return
    lock=json.loads((BASE/'TOOLCHAINS-v1.json').read_text());tools(lock)
    if args.clean:
        destination=args.clean.resolve();assert not destination.exists(),destination
        temp=Path(tempfile.mkdtemp(prefix='css-timeline-proof-',dir='/private/tmp'))
        source=temp/'source';source.mkdir()
        for entry in manifest['files']:
            path=source/entry['path'];path.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(BASE/entry['path'],path)
        shutil.copyfile(BASE/'SOURCE-MANIFEST-v1.json',source/'SOURCE-MANIFEST-v1.json')
        repo=next((p for p in BASE.parents if (p/'mach').is_file()),None)
        assert repo is not None,'clean launch must identify checkout to deny access'
        profile='(version 1) (allow default) (deny network*) (deny file-read* (subpath '+json.dumps(str(repo))+')) (allow file-read* (subpath '+json.dumps(lock['lean']['root'])+'))'
        metadata_paths=[]
        for ancestor in Path(lock['lean']['root']).parents:
            if ancestor==repo or ancestor.is_relative_to(repo):
                metadata_paths.append(str(ancestor))
                profile+=' (allow file-read-metadata (literal '+json.dumps(str(ancestor))+'))'
        (temp/'sandbox.sb').write_text(profile+'\n')
        env={'PATH':'/usr/bin:/bin:/usr/sbin:/sbin','LANG':'C','LC_ALL':'C','PYTHONNOUSERSITE':'1'}
        command=['/usr/bin/sandbox-exec','-f',str(temp/'sandbox.sb'),sys.executable,'-I','-S',str(source/'verify.py'),'--expected-manifest',sha(BASE/'SOURCE-MANIFEST-v1.json'),'--replay',str(temp/'generated')]
        with (temp/'closure.log').open('wb') as output:
            result=subprocess.run(command,cwd=temp,env=env,stdout=output,stderr=subprocess.STDOUT)
        shutil.copytree(temp,destination)
        receipt=dict(status=result.returncode,metadata_only_exceptions=metadata_paths,command=command,source_manifest_sha256=sha(BASE/'SOURCE-MANIFEST-v1.json'),checkout_read_denied=str(repo),network_denied=True,temp=str(temp))
        (destination/'CLOSURE-RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n')
        assert result.returncode==0,('clean replay failed',str(destination/'closure.log'))
        print(json.dumps(receipt,indent=2));return
    result=helpers().run(args.replay,Path(lock['lean']['root'])/lock['lean']['executable'],lock['cxx']['executable'])
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
