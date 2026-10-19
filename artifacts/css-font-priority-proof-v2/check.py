import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

BASE=Path(__file__).resolve().parent
EXPECTED_INPUTS='aab36f78467284b8b64bd11348262b98717a994447a8d161608c5b6d5018eb45'


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def authenticate():
    manifest=BASE/'INPUTS-v2.json'
    assert digest(manifest)==EXPECTED_INPUTS,'input manifest identity'
    data=json.loads(manifest.read_text())
    for name,sha in data['files'].items():
        path=BASE/name
        assert path.is_file() and digest(path)==sha,('source authentication',name)
    inherited=json.loads((BASE/'INHERITED-B-v1.json').read_text())
    assert digest(BASE/'support_b/INPUTS-v1.json')==inherited['input_manifest_sha256']
    assert digest(BASE/'support_b/FREEZE-v1.json')==inherited['freeze_sha256']
    for name,sha in inherited['copied_files'].items():
        assert digest(BASE/'support_b'/name)==sha,('frozen B copy',name)
    tc=json.loads((BASE/'support_b/TOOLCHAIN-v1.json').read_text())
    for name in ('compiler','lean'):
        assert digest(Path(tc[name]))==tc[name+'_sha256'],name
    assert digest(Path(tc['sdk'])/'SDKSettings.json')==tc['sdk_settings_sha256'],'SDK'
    return data


def main():
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);p.add_argument('--worker',action='store_true');p.add_argument('--auth-only',action='store_true');args=p.parse_args()
    data=authenticate()
    if args.auth_only:
        print('AUTHENTICATED',len(data['files']),'inputs before local imports');return
    out=Path(args.out).resolve();out.mkdir(parents=True,exist_ok=True)
    env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1');env.pop('PYTHONPATH',None)
    if not args.worker:
        source=out/'isolated-source';assert not source.exists(),'choose a fresh output directory'
        source.mkdir()
        for name in list(data['files'])+['INPUTS-v2.json','check.py']:
            target=source/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(BASE/name,target)
        command=[sys.executable,str(source/'check.py'),'--worker','--out',str(out/'isolated-results')]
        with (out/'SOURCE-ONLY.log').open('w') as log:
            result=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,env=env,timeout=1800)
        assert result.returncode==0,('isolated replay',out/'SOURCE-ONLY.log')
        (out/'SOURCE-ONLY.json').write_text(json.dumps(dict(status='PASS',authenticated_files=len(data['files']),input_manifest_sha256=EXPECTED_INPUTS,live_source_reads=False,preexisting_binaries_used=False,results='isolated-results'),indent=2)+'\n')
        print('SOURCE-ONLY PASS',out);return
    commands=[
        ('refresh',[sys.executable,str(BASE/'refresh.py'),'--out',str(out/'refresh')]),
        ('native',[sys.executable,str(BASE/'run.py'),'--out',str(out/'native')]),
        ('gtk',[sys.executable,str(BASE/'run.py'),'--gtk','--out',str(out/'gtk')]),
        ('mutations',[sys.executable,str(BASE/'mutations.py'),'--out',str(out/'mutations')]),
        ('lean',[sys.executable,str(BASE/'lean_check.py'),'--out',str(out/'lean'),'--mutations',str(out/'mutations/MUTATIONS.json')]),
        ('cost',[sys.executable,str(BASE/'benchmark.py'),'--out',str(out/'cost')]),
    ]
    for name,command in commands:
        with (out/(name+'.log')).open('w') as log:r=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,env=env,timeout=600)
        assert r.returncode==0,(name,'failed',out/(name+'.log'))
        print(name,'PASS',flush=True)
    summary={name:json.loads((out/name/'RESULT.json').read_text()) for name in ('native','gtk','lean')}
    summary['status']='PASS';summary['source_only']=True
    summary['refresh']=json.loads((out/'refresh/RESULT.json').read_text())
    summary['total_comparison_rows']=sum(summary[k]['total_comparison_rows'] for k in ('native','gtk'))
    summary['complete_consumer_entry_rows']=sum(summary[k]['complete_consumer_entry_rows'] for k in ('native','gtk'))
    assert summary['total_comparison_rows']==53628 and summary['complete_consumer_entry_rows']==30204
    summary['semantic_native_mutants']=len(json.loads((out/'mutations/MUTATIONS.json').read_text()))
    summary['coordinate_float_control']=json.loads((out/'mutations/FLOAT-COORDINATES.json').read_text())
    summary['cost_comparisons']=len(json.loads((out/'cost/COST.json').read_text())['rows'])
    (out/'RESULT.json').write_text(json.dumps(summary,indent=2)+'\n')

if __name__=='__main__':main()
