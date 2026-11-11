import argparse
import ast
from collections import Counter
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def load(p):
    return json.loads(p.read_text())


def git_file(revision, path):
    return subprocess.run(['git','-c','core.fsmonitor=false','show',revision+':'+path], cwd=ROOT, capture_output=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--frozen', action='store_true')
    args = parser.parse_args()
    origins = load(HERE/'ORIGINS.json')
    plan = load(HERE/'RUN-PLAN.json')
    roles = load(HERE/'SOURCE-ROLES.json')
    for name in ['bundle.py','process.py','analyze.py']:
        data = git_file(origins['signed_origin'],origins['origin_directory']+'/'+name)
        assert data.returncode==0 and data.stdout==(HERE/name).read_bytes()
        assert sha(HERE/name)==origins['origin_hashes'][name]
    for p in HERE.glob('*.py'):
        ast.parse(p.read_text(),filename=str(p))
    assert plan['head'] is None or isinstance(plan['head'],str) and len(plan['head'])==40
    assert len(plan['suites'])==10 and len(set(plan['suites']))==10
    assert len(roles)==2 and len(plan['fixtures'])==1 and len(plan['lint_paths'])==2
    native='servo/ports/geckolib/glue.rs'
    merge='testing/web-platform/tests/scroll-animations/css/merge-timeline-offset-keyframes.html'
    new='testing/web-platform/tests/scroll-animations/css/named-range-group-earliest-order.html'
    assert set(roles)=={native,merge} and not roles[native]['install_both'] and roles[merge]['install_both']
    assert plan['fixtures']=={new:'named-range-group-earliest-order.html'}
    assert plan['lint_paths']==[merge,new]
    author=ROOT/'artifacts/css-named-range-group-order-candidate-20261110-v1'
    assert sha(HERE/'range-order.patch')==origins['candidate_patch_sha256']==sha(author/'range-order.patch')
    for name,role in roles.items():
        data=git_file(origins['source_test_pin_revision'],name)
        assert data.returncode==0 and data.stdout==(HERE/'source'/name).read_bytes()
        assert sha(HERE/'source'/name)==role['base']
        assert (HERE/'candidate'/name).read_bytes()==(author/'candidate'/name).read_bytes()
        assert sha(HERE/'candidate'/name)==role['candidate']
    assert sha(HERE/'runtime-inputs/named-range-group-earliest-order.html')==origins['fixture_sha256']==sha(author/'candidate'/new)
    pins=load(HERE/'runtime-inputs/test-source-pins.json')
    assert pins[new] is None and pins[new.replace('/tests/','/meta/',1)+'.ini'] is None
    for name,digest in pins.items():
        result=git_file(origins['source_test_pin_revision'],name)
        if digest is None:
            assert result.returncode!=0
        else:
            assert result.returncode==0 and hashlib.sha256(result.stdout).hexdigest()==digest
    retained=load(HERE/'runtime-inputs/retained-build.json')
    assert sha(HERE/'runtime-inputs/retained-build.json')==origins['retained_build_sha256']
    assert retained['status']=='pass' and retained['build_exit']==0 and not retained['final_wpt_pending']
    assert retained['mozconfig_sha256']==plan['mozconfig_sha256']
    bridge=subprocess.check_output(['git','-c','core.fsmonitor=false','diff','--name-only',retained['head'],origins['source_test_pin_revision']],cwd=ROOT,text=True).splitlines()
    assert all(name.startswith('artifacts/') for name in bridge),bridge
    for name,digest in retained['sources'].items():
        result=git_file(origins['source_test_pin_revision'],name)
        assert result.returncode==0 and hashlib.sha256(result.stdout).hexdigest()==digest
    spec=importlib.util.spec_from_file_location('analysis',HERE/'analyze.py')
    analysis=importlib.util.module_from_spec(spec);spec.loader.exec_module(analysis)
    base=load(HERE/'EXPECTED-BASELINE.json')
    callbacks=load(HERE/'EXPECTED-CALLBACKS.json')
    changes=load(HERE/'EXPECTED-CHANGES.json')
    assert len(analysis.rows(base))==99 and len(callbacks)==89 and len(changes)==3
    assert len({tuple(r) for r in callbacks})==89
    assert Counter(r['status'] for r in base['subtests'])=={'PASS':77,'FAIL':12}
    assert len(base['harness'])==10 and all(r['status']=='OK' for r in base['harness'])
    for suffix,counts in [('keyframe-attribute-mutation.html',{'PASS':12}),('KeyframeEffect-getKeyframes.tentative.html',{'PASS':31,'FAIL':2})]:
        assert Counter(r['status'] for r in base['subtests'] if r['test'].endswith('/'+suffix))==counts
    changed={(r['test'],r['subtest']) for r in changes}
    candidate=json.loads(json.dumps(base))
    for row in candidate['subtests']:
        if (row['test'],row['subtest']) in changed:
            assert row['status']=='FAIL';row['status']='PASS'
    assert Counter(r['status'] for r in candidate['subtests'])=={'PASS':80,'FAIL':9}
    assert analysis.compare(base,candidate)['accepted_changes_only']
    controls=json.loads(subprocess.check_output([sys.executable,'-I',str(HERE/'parser-controls.py')]))
    assert controls['status']=='pass' and len(controls['rejected_controls'])==26
    if args.frozen:
        assert plan['head'] is not None
        manifest=load(HERE/'RUN-INPUTS.json')
        assert all(sha(HERE/name)==digest for name,digest in manifest.items())
        changed_names=subprocess.check_output(['git','-c','core.fsmonitor=false','diff','--name-only',origins['source_test_pin_revision'],plan['head']],cwd=ROOT,text=True).splitlines()
        assert all(name.startswith('artifacts/') for name in changed_names),changed_names
    print(json.dumps({'status':'PASS','frozen':args.frozen,'execution_head':plan['head'],'source_roles':2,'temporary_fixtures':1,'test_source_metadata_pins':len(pins),'retained_build_source_pins':len(retained['sources']),'retained_build_bridge_artifact_only':True,'records':99,'baseline_callbacks':{'PASS':77,'FAIL':12},'candidate_callbacks':{'PASS':80,'FAIL':9},'harness_OK':10,'exact_improvements':3,'parser_rejection_controls':26,'native_browser_execution':False},indent=2))


if __name__=='__main__':
    main()
