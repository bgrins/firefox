import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name,path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def check():
    policy = json.loads((HERE/'POLICY.json').read_bytes())
    assert not policy['execution_enabled'] and not policy['candidate_execution_enabled']
    assert policy['activation_pending']
    assert policy['checkpoint_mode'] == 'current_native_checkpoint'
    assert policy['head'] and policy['controls'] and policy['prepared_application_metadata'] and policy['prepared_flag_hashes']
    assert 'reference_checkpoint' not in policy and 'research_parent_head' not in policy
    assert set(policy['phases']) == {'feedback'} and policy['wpt'] == policy['phases']['feedback']
    comparison = load('feedback_compare',HERE/'comparison.py')
    assert comparison.expected_wpt(ROOT,policy) == policy['wpt']
    authenticated, deferred = 0, []
    for name,pin in policy['references'].items():
        if not name.startswith('artifacts/'):
            deferred.append(name)
            continue
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest() == pin, name
        authenticated += 1
    for path in HERE.glob('*.py'):
        compile(path.read_bytes(),str(path),'exec')
    original = load('feedback_synthetic',ROOT/policy['baseline_capsule']['directory']/'check.py')
    original_policy = json.loads((ROOT/policy['baseline_capsule']['directory']/'POLICY.json').read_bytes())
    settings, app, events = original.synthetic(original_policy['wpt'])
    assessor = load('feedback_assessor',HERE/'assess.py')
    checks = load('feedback_checks',ROOT/policy['wpt']['checks_helper'])
    observed = assessor.assess(events,0,settings,checks,run_binding=app)
    assert observed['complete']
    candidate_settings = copy.deepcopy(settings)
    candidate_settings['phase_revisions']['candidate'] = 'a'*40
    candidate_settings['candidate_required_pass_pages'] = list(settings['expected_subtests'])
    candidate_app = dict(app,revision='a'*40,build_revision='a'*40,source_role='candidate',browser_build_id='synthetic-candidate')
    candidate = copy.deepcopy(events)
    candidate[0]['run_info']['browser_build_id'] = 'synthetic-candidate'
    def assess(stream,code=0):
        return assessor.assess(stream,code,candidate_settings,checks,original=observed,run_binding=candidate_app)
    assert assess(candidate)['comparison_gate_passed']
    rejected = []
    def reject(label, mutate, code=0):
        stream = copy.deepcopy(candidate)
        mutate(stream)
        assert not assess(stream,code)['comparison_gate_passed'], label
        rejected.append(label)
    reject('callback failure',lambda s:s[2].update(status='FAIL',expected='PASS'),1)
    reject('callback message',lambda s:s[2].update(message='changed'))
    reject('expected presence',lambda s:s[2].update(expected='PASS'))
    reject('intermittent presence',lambda s:s[2].update(known_intermittent=[]))
    reject('ending message',lambda s:s[-2].update(message='changed'))
    reject('missing callback',lambda s:s.pop(2))
    reject('unknown callback',lambda s:s[2].update(subtest='unknown'))
    reject('wrong BuildID',lambda s:s[0]['run_info'].update(browser_build_id='wrong'))
    reject('wrong harness',lambda s:s[0]['run_info'].update(revision='0'*40))
    reject('missing suite end',lambda s:s.pop())
    reject('crash',lambda s:s.append({'action':'crash'}))
    reject('wrong exit',lambda s:None,1)
    annotations = {'build_revision','harness_revision','source_role'}
    synthetic_policy = dict(policy,head='a'*40,prepared_application_metadata={k:v for k,v in app.items() if k not in annotations},wpt=settings)
    assert comparison.original_metadata(synthetic_policy) == app
    for key,value in [('revision','0'*40),('source_role','candidate')]:
        malformed = copy.deepcopy(synthetic_policy)
        malformed['prepared_application_metadata'][key] = value
        try:
            comparison.original_metadata(malformed)
        except AssertionError:
            rejected.append('metadata '+key)
        else:
            raise AssertionError(key)
    baseline = load('feedback_checkpoint',HERE/'baseline.py')
    native = json.loads((ROOT/policy['native_checkpoint']['path']).read_bytes())
    baseline.checkpoint_chain(policy,native)
    for key,value in [('head','0'*40),('signature_chain_verified',False),
                      ('runtime_epoch_synchronized',False),('accepted_fix',151),
                      ('accepted_fixes',150),('tracked',151)]:
        wrong = dict(native)
        wrong[key] = value
        try:
            baseline.checkpoint_chain(policy,wrong)
        except AssertionError:
            rejected.append('native checkpoint '+key)
        else:
            raise AssertionError(key)
    try:
        baseline.checkpoint_chain(dict(policy,checkpoint_mode='future_research'),native)
    except AssertionError:
        rejected.append('wrong checkpoint mode')
    else:
        raise AssertionError('wrong checkpoint mode')
    phases = load('feedback_records',HERE/'phases.py')
    with tempfile.TemporaryDirectory(prefix='duration-feedback-static-') as temporary:
        output = Path(temporary)
        records = output/'feedback-records'
        records.mkdir(mode=0o700)
        run_id = 'synthetic_run_1234567890'
        binding = {'directory':str(records),'identity':[records.stat().st_dev,records.stat().st_ino],'run_id':run_id}
        (output/'FEEDBACK-BINDING.json').write_text(json.dumps(binding))
        bodies = {}
        for name,kind in [('self.json','self font'),('coupled.json','coupled font and opacity'),('zero-start.json','zero-start self font')]:
            effect = {'name':'synthetic','time':None,'duration':1000,'progress':None,'state':'paused'}
            sample = {'font':'28px','cssDuration':'1.75s','opacity':'0.75','effects':[effect]*(2 if kind.startswith('coupled') else 1),'repeatFont':'28px','repeatDuration':'1.75s'}
            bodies[name] = {'run_id':run_id,'kind':kind,'samples':[sample]*8}
        def restore():
            for path in records.iterdir():
                path.unlink()
            os.chmod(records,0o700)
            for name,body in bodies.items():
                path = records/name
                path.write_text(json.dumps(body))
                path.chmod(0o600)
        restore()
        assert phases.feedback_records(output)['numeric_or_convergence_oracle'] is False
        def reject_record(label,mutate):
            restore()
            mutate()
            try:
                phases.feedback_records(output)
            except (AssertionError,FileNotFoundError):
                rejected.append(label)
            else:
                raise AssertionError(label)
        def changed_record(change):
            body = copy.deepcopy(bodies['self.json'])
            change(body)
            (records/'self.json').write_text(json.dumps(body))
        reject_record('missing record',lambda:(records/'self.json').unlink())
        reject_record('extra record',lambda:(records/'extra.json').write_text('{}'))
        reject_record('wrong run ID',lambda:changed_record(lambda b:b.update(run_id='wrong')))
        reject_record('wrong kind',lambda:changed_record(lambda b:b.update(kind='wrong')))
        reject_record('missing sample',lambda:changed_record(lambda b:b['samples'].pop()))
        reject_record('missing effect field',lambda:changed_record(lambda b:b['samples'][0]['effects'][0].pop('duration')))
        reject_record('record permissions',lambda:(records/'self.json').chmod(0o644))
        reject_record('directory permissions',lambda:records.chmod(0o755))
        restore()
        changed_record(lambda b:b['samples'][0]['effects'][0].update(duration='unrestricted-measurement',progress=None))
        assert phases.feedback_records(output)['numeric_or_convergence_oracle'] is False
    actual_replayed = False
    if policy['baseline_binding'] is not None:
        binding = policy['baseline_binding']
        directory = ROOT/binding['directory']
        for capsule,pin in [(ROOT/policy['baseline_capsule']['directory'],policy['baseline_capsule']['sha256']),
                            (directory,binding['manifest_sha256'])]:
            assert hashlib.sha256((capsule/'FILES.json').read_bytes()).hexdigest() == pin
            for name,expected in json.loads((capsule/'FILES.json').read_bytes()).items():
                assert hashlib.sha256((capsule/name).read_bytes()).hexdigest() == expected
        terminal = json.loads((directory/binding['terminal_path']).read_bytes())
        assert terminal == binding['terminal'] and terminal['exit'] == 0
        assert terminal['owner_sha256'] == policy['baseline_capsule']['sha256']
        assert terminal['result_sha256'] == binding['result_sha256'] == hashlib.sha256((directory/'RESULT.json').read_bytes()).hexdigest()
        comparison.replay_all(ROOT,policy)
        actual_replayed = True
    return {'positive_comparisons':1,'positive_metadata_joins':1,'positive_checkpoint_chains':1,'positive_record_sets':2,
            'negative_controls':rejected,'artifact_references_authenticated':authenticated,
            'deferred_nonartifact_references':deferred,'fresh_original_replayed':actual_replayed,
            'browser_build_or_live_guard_executed':False,'scratch_removed':True}


if __name__ == '__main__':
    print(json.dumps(check(),indent=2))
