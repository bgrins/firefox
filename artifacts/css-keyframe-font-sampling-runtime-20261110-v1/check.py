import argparse
import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path):
    return json.loads(path.read_text())


def git_file(revision, name):
    return subprocess.run(['git', '-c', 'core.fsmonitor=false', 'show', revision + ':' + name], cwd=ROOT, capture_output=True)


def input_names():
    names = ['run.py','analyze.py','bundle.py','process.py','freeze.py','check.py','parser-controls.py','RUN-PLAN.json','SOURCE-ROLES.json','EXPECTED-BASELINE.json','EXPECTED-CALLBACKS.json','EXPECTED-CHANGES.json','OBSERVATION-SCHEMA.json','ROOT-PROFILE-PIN.json','observe.py','ORIGINS.json','ORIGIN-RUN-INPUTS.json']
    names += [str(p.relative_to(HERE)) for p in sorted((HERE/'runtime-inputs').rglob('*')) if p.is_file()]
    return sorted(names)


def artifact_bridge(left, right):
    names = subprocess.check_output(['git', '-c', 'core.fsmonitor=false', 'diff', '--name-only', left, right], cwd=ROOT, text=True).splitlines()
    assert all(name.startswith('artifacts/') for name in names), names


def validate_retained(retained, head, plan, origins, roles):
    assert roles == {}
    assert retained['status'] == 'pass' and retained['build_exit'] == 0
    assert retained['final_wpt_pending'] is False and retained['tracked_tree_clean'] is True
    assert retained['mozconfig_sha256'] == plan['mozconfig_sha256']
    assert set(retained['binaries']) == {'objdir-full.noindex/dist/Nightly.app/Contents/MacOS/firefox', 'objdir-full.noindex/dist/Nightly.app/Contents/MacOS/XUL', 'objdir-full.noindex/dist/Nightly.app/Contents/Resources/application.ini'}
    assert len(retained['sources']) == 7
    artifact_bridge(origins['source_test_pin_revision'], retained['head'])
    artifact_bridge(retained['head'], head)
    for name, digest in retained['sources'].items():
        for rev in [retained['head'], head]:
            result = git_file(rev, name)
            assert result.returncode == 0 and hashlib.sha256(result.stdout).hexdigest() == digest, name


def main():
    assert sys.flags.isolated and not sys.flags.optimize
    parser=argparse.ArgumentParser();parser.add_argument('--frozen',action='store_true');args=parser.parse_args()
    origins=load(HERE/'ORIGINS.json');plan=load(HERE/'RUN-PLAN.json');roles=load(HERE/'SOURCE-ROLES.json')
    assert roles=={} and load(HERE/'EXPECTED-CHANGES.json')==[]
    assert sha(HERE/'ORIGIN-RUN-INPUTS.json')==origins['wrapper_manifest_sha256']
    previous=load(HERE/'ORIGIN-RUN-INPUTS.json')
    for name,digest in origins['unchanged_executables'].items():
        assert sha(HERE/name)==digest==previous[name]
        if name!='run.py':
            result=git_file(origins['signed_origin'],origins['origin_directory']+'/'+name)
            assert result.returncode==0 and result.stdout==(HERE/name).read_bytes()
    for path in HERE.glob('*.py'):ast.parse(path.read_text(),filename=str(path))
    run=(HERE/'run.py').read_text();assert "assert mode == 'baseline' and not prior" in run and "'build', 'binaries'" not in run
    assert len(plan['fixtures'])==1 and plan['suites']==plan['lint_paths']==list(plan['fixtures'])
    fixture=HERE/'runtime-inputs'/next(iter(plan['fixtures'].values()))
    assert sha(fixture)==origins['proposal_sha256']==sha(ROOT/origins['proposal_origin'])
    assert sha(ROOT/origins['proposal_manifest_origin'])==origins['proposal_manifest_sha256']
    assert 'console.' not in fixture.read_text()
    profile=load(HERE/'ROOT-PROFILE-PIN.json');raw=git_file(profile['head'],profile['path'])
    assert raw.returncode==0 and hashlib.sha256(raw.stdout).hexdigest()==profile['sha256']
    assert b'user_pref("browser.dom.window.dump.enabled", true)' in raw.stdout
    pins=load(HERE/'runtime-inputs/test-source-pins.json');assert pins[profile['path']]==profile['sha256']
    for name,digest in pins.items():
        result=git_file(origins['source_test_pin_revision'],name)
        assert result.returncode!=0 if digest is None else result.returncode==0 and hashlib.sha256(result.stdout).hexdigest()==digest
    for name in plan['fixtures']:assert pins[name] is None and pins[name.replace('/tests/','/meta/',1)+'.ini'] is None
    expected=load(HERE/'EXPECTED-BASELINE.json');schema=load(HERE/'OBSERVATION-SCHEMA.json')
    assert len(expected['subtests'])==3 and all(row['status']=='PASS' for row in expected['subtests'])
    assert expected['harness']==[{'test':expected['subtests'][0]['test'],'status':'OK'}]
    assert schema['callbacks']==[row['subtest'] for row in expected['subtests']]
    assert len(set(schema['ids']))==3 and len(set(schema['phases']))==5 and schema['records']==15
    import re
    scripts=re.findall(r'<script>(.*?)</script>',fixture.read_text(),re.S);assert len(scripts)==1
    cmd=['node','-e',"const vm=require('vm'),fs=require('fs'),names=[];vm.runInNewContext(fs.readFileSync(0,'utf8'),{promise_test:(_body,name)=>names.push(name)});process.stdout.write(JSON.stringify(names));"]
    result=subprocess.run(cmd,input=scripts[0],text=True,capture_output=True);assert result.returncode==0 and json.loads(result.stdout)==schema['callbacks']
    assert load(HERE/'EXPECTED-CALLBACKS.json')==[[row['test'],row['subtest']] for row in expected['subtests']]
    controls=json.loads(subprocess.check_output([sys.executable,'-I',str(HERE/'parser-controls.py')]))
    assert controls['status']=='PASS' and len(controls['rejected_controls'])>=35
    retained=HERE/'runtime-inputs/retained-build.json';assert sha(retained)==origins['retained_build_sha256']
    if args.frozen:
        assert isinstance(plan['head'],str) and len(plan['head'])==40
        assert sha(retained)==plan['retained_build_sha256']==sha(ROOT/plan['retained_build_origin'])
        validate_retained(load(retained),plan['head'],plan,origins,roles)
        manifest=load(HERE/'RUN-INPUTS.json');assert set(manifest)==set(input_names())
        assert all(sha(HERE/n)==d for n,d in manifest.items())
    else:
        assert plan['head'] is None and not (HERE/'RUN-INPUTS.json').exists() and not (HERE/'FREEZE-READY.json').exists()
        validate_retained(load(retained),origins['source_test_pin_revision'],plan,origins,roles)
    print(json.dumps({'status':'PASS','frozen':args.frozen,'execution_head':plan['head'],'native_roles':0,'temporary_fixtures':1,'callbacks_PASS':3,'harness_OK':1,'observations':15,'parser_rejection_controls':len(controls['rejected_controls']),'browser_executed':False},indent=2))


if __name__=='__main__':main()
