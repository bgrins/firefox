import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
LAB=ROOT/'artifacts/css-keyframe-font-sampling-runtime-20261110-v1'
def load(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    assert sha(LAB/'RUN-INPUTS.json')=='1b32949c6fec8b10df3781d2ef4ee41561a203b1f10d941d019254f1f21f7aee'
    assert all(sha(LAB/n)==d for n,d in load(LAB/'RUN-INPUTS.json').items())
    plan=load(LAB/'RUN-PLAN.json');directory=LAB/'baseline1';before=load(directory/'BEFORE.json');result=load(directory/'RESULT.json')
    assert result['head']==plan['head']==before['head']
    assert result['runner_inputs_sha256']==sha(LAB/'RUN-INPUTS.json')
    assert set(result['commands'])=={'lint','build','wpt'}
    assert result['commands']['lint']['exit_code']==result['commands']['wpt']['exit_code']==0
    assert result['commands']['build']['skipped'] is True
    assert result['error'] is None and result['restoration_verified'] and result['restoration_errors']==[]
    assert result['observation_count']==15
    expected=load(LAB/'EXPECTED-BASELINE.json')
    expectedrows={(kind,r['test'],r.get('subtest')):r['status'] for kind,field in [('assertion','subtests'),('harness','harness')] for r in expected[field]}
    callbacks={}; observations={}; active=None; begun=ended=False
    def unique(pairs):
        d={}
        for k,v in pairs:
            assert k not in d
            d[k]=v
        return d
    schema=load(LAB/'OBSERVATION-SCHEMA.json')
    for line in (directory/'wpt-raw.jsonl').read_text().splitlines():
        row=json.loads(line,object_pairs_hook=unique)
        action=row['action']
        assert action!='crash'
        assert not(action=='log' and row.get('level') in ['ERROR','CRITICAL'])
        if action=='suite_start':
            assert not begun and not ended;begun=True
        elif action=='test_start':
            assert begun and not ended and active is None;active=row['test']
        elif action in ['test_status','test_end']:
            assert active==row['test']
            key=('assertion' if action=='test_status' else 'harness',row['test'],row.get('subtest'))
            assert key not in callbacks;callbacks[key]=row['status']
            if action=='test_end':active=None
        elif action=='suite_end':
            assert begun and not ended and active is None;ended=True
        elif action=='assertion_count':
            assert row['min_expected']<=row['count']<=row['max_expected']
        if action=='process_output' and 'KFONT' in row.get('data',''):
            assert row['data'].startswith('KFONT-V1 ')
            item=json.loads(row['data'][9:],object_pairs_hook=unique)
            assert set(item)==set(schema['required_record_fields'])
            key=(item['id'],item['phase']);assert key not in observations;observations[key]=item
            assert item['id'] in schema['ids'] and item['phase'] in schema['phases']
            assert all(set(item[field])==set(schema['style_fields']) and all(type(v) is str for v in item[field].values()) for field in ['before','after'])
            assert type(item['frames']) is list
            assert all({'offset','computedOffset','easing','composite'}<=set(f) for f in item['frames'])
    assert begun and ended and active is None and callbacks==expectedrows and len(callbacks)==4
    assert set(observations)=={(name,phase) for name in schema['ids'] for phase in schema['phases']}
    assert [observations[k] for k in sorted(observations)]==load(directory/'OBSERVATIONS.json')
    spec_observe=importlib.util.spec_from_file_location('observe_review',LAB/'observe.py');observe=importlib.util.module_from_spec(spec_observe);spec_observe.loader.exec_module(observe)
    assert observe.parse(directory/'wpt-raw.jsonl')==load(directory/'OBSERVATIONS.json')
    spec=importlib.util.spec_from_file_location('review_bundle',LAB/'bundle.py');bundle=importlib.util.module_from_spec(spec);spec.loader.exec_module(bundle)
    assert bundle.semantic(bundle.scan(ROOT/'objdir-full.noindex/dist/Nightly.app'))==bundle.semantic(before['app'])
    assert bundle.semantic({p:bundle.entry(ROOT/p) for p in before['extras']})==bundle.semantic(before['extras'])
    retained=load(LAB/'runtime-inputs/retained-build.json')
    assert all(sha(ROOT/n)==d for n,d in retained['sources'].items())
    assert all(sha(ROOT/n)==d for n,d in retained['binaries'].items())
    assert sha(ROOT/'mozconfig')==plan['mozconfig_sha256']
    for n,d in load(LAB/'runtime-inputs/test-source-pins.json').items():
        assert not ((ROOT/n).exists() or (ROOT/n).is_symlink()) if d is None else sha(ROOT/n)==d
    def git(*args):return subprocess.check_output(['git','-c','core.fsmonitor=false',*args],cwd=ROOT)
    assert git('rev-parse','HEAD').decode().strip()==plan['head']
    assert hashlib.sha256(git('ls-files','--stage','-z')).hexdigest()==before['index']
    assert not git('diff','--name-only').strip() and not git('diff','--cached','--name-only').strip()
    assert not (directory/'backups').exists() and not (LAB/'runtime.lock').exists()
    assert load(directory/'RESTORED.json')['backup_removed']
    processes=[load(f) for f in directory.glob('*.process.json')];assert len(processes)==2
    assert all(process['state']=='terminal' and process['group_absent'] for process in processes)
    alive={int(parts[0]) for line in (HERE/'process-snapshot.txt').read_text().splitlines() if len(parts:=line.split())==3 and not parts[1].startswith('Z')}
    assert all(process['pgid'] not in alive for process in processes)
    print(json.dumps({'status':'PASS','callbacks_PASS':3,'harness_OK':1,'raw_observations':15,'browser_executed':True,'application_entries_restored':len(before['app']),'extras_restored':len(before['extras']),'source_test_binary_config_HEAD_index_restored':True,'owned_group_absent':True,'temporary_fixture_backups_lock_absent':True},indent=2))
if __name__=='__main__':main()
