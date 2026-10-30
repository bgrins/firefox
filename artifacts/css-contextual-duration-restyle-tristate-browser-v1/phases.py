import hashlib
import importlib.util
import json
import os
from pathlib import Path
import secrets
import stat

read = lambda path: json.loads(path.read_bytes())
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def feedback_records(root, output, policy):
    binding = read(output / 'FEEDBACK-BINDING.json')
    records = output / 'feedback-records'
    assert str(records) == binding['directory'] and not records.is_symlink()
    assert [records.stat().st_dev,records.stat().st_ino] == binding['identity']
    assert stat.S_IMODE(records.stat().st_mode)==0o700 and records.stat().st_uid==os.getuid()
    expected = policy['record_kinds']
    assert expected == {'coupled.json':'coupled','zero-start.json':'zero-start'}
    schema = load('consistency_schema',root / policy['record_schema_helper'])
    assert {p.name for p in records.iterdir()} == set(expected)
    pins = {}
    for filename,kind in expected.items():
        path = records / filename
        assert path.is_file() and not path.is_symlink()
        info = path.stat()
        assert stat.S_IMODE(info.st_mode)==0o600 and info.st_uid==os.getuid() and info.st_nlink==1
        record = read(path)
        assert set(record)=={'run_id','kind','trajectories'} and record['run_id']==binding['run_id']
        assert schema.validate({k:v for k,v in record.items() if k!='run_id'})==kind
        pins[filename]={'sha256':sha(path),'identity':[info.st_dev,info.st_ino],'mode':stat.S_IMODE(info.st_mode)}
    assessment = read(output / 'feedback-wpt/ASSESSMENT.json')
    assert assessment['complete'] and len(assessment['rows']) == 2
    calibrated = all(row['status']=='PASS' for row in assessment['rows'])
    return {'run_id':binding['run_id'],'records':pins,'calibrated_acquisition':calibrated,'numeric_or_convergence_oracle':False}


def run(root, here, output, policy, env, verify, owned, cancelled):
    wpt = load('tristate_wpt', here / 'wpt.py')
    comparison = load('tristate_comparison', here / 'comparison.py')
    initial = verify()
    wpt.save(output / 'PHASES-PRE.json', initial)
    records = output / 'feedback-records'
    records.mkdir(mode=0o700)
    run_id = secrets.token_hex(24)
    wpt.save(output / 'FEEDBACK-BINDING.json', {'directory':str(records),'identity':[records.stat().st_dev,records.stat().st_ino],'run_id':run_id})
    phase_env = dict(env,DURATION_FEEDBACK_RECORD_DIR=str(records),DURATION_FEEDBACK_RUN_ID=run_id)
    phase = output / 'feedback-wpt'
    failure, result, record_result = None, None, None
    try:
        result = wpt.run(root,here,phase,'candidate',policy,phase_env,verify,owned,cancelled,comparison.original_directory(root,policy))
    except BaseException as error:
        failure = error
    diagnostic_errors = []
    try:
        record_result = feedback_records(root,output,policy)
        wpt.save(output / 'FEEDBACK-RECORDS.json',record_result)
    except BaseException as error:
        diagnostic_errors.append(repr(error))
    wpt.save(output / 'DIAGNOSTICS.json',{'phase_error':repr(failure) if failure else None,'record_errors':diagnostic_errors,'numeric_or_convergence_oracle':False})
    if failure is not None:
        raise failure
    assert not diagnostic_errors, diagnostic_errors
    assert record_result['calibrated_acquisition'] is True
    assert not owned and read(phase / 'PRE.json') == read(phase / 'POST.json') == initial
    assert read(phase / 'APPLICATION-METADATA.json') == read(phase / 'APPLICATION-METADATA-POST.json')
    assert read(phase / 'BINARY-PINS.json') == read(output / 'candidate-build/RESULT.json')['binaries']
    assert not owned and verify() == initial
    wpt.save(output / 'PHASES-POST.json',initial)
    return {'feedback':result,'calibrated_acquisition':True,'record_index_sha256':sha(output / 'FEEDBACK-RECORDS.json')}

