import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import stat
import sys
import tempfile
from types import SimpleNamespace

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('progress_transport', HERE / 'duration-progress-record.py')
handler = importlib.util.module_from_spec(spec)
spec.loader.exec_module(handler)


def example(suite, mode):
    timing = dict(duration=2000, progress=.375, time=750, state='paused')
    if suite == 'two-hop':
        snapshot = dict(childOpacity=.5, childDuration=1500, child=timing.copy(),
                        middleFont=24, middleDuration=2000, middle=timing.copy(), rootFont=32)
        flags = {'membership': dict(middle=True, child=True, middleEffect=True, childEffect=True)}
        driver = timing.copy()
    else:
        snapshot = dict(width=56, cssDuration=2000, parentFont=32, **timing)
        flags = {'same': True}
        driver = dict(time=1000, state='paused')
    dimension = 'opacity' if suite == 'two-hop' else 'width'
    observation = dict(mode=mode, samples=[dict(phase=phase, **{dimension: index}) for index, phase in enumerate(handler.PHASES)],
                       beforeMembership=copy.deepcopy(snapshot), driverTiming=driver if mode == 'animated' else None,
                       afterMembership=copy.deepcopy(snapshot), seek751=copy.deepcopy(snapshot), afterSeek=copy.deepcopy(snapshot), **flags)
    return dict(kind=suite+'-'+mode, observation=observation)


negative = []


def reject(label, call):
    try:
        call()
    except (AssertionError, ValueError, OSError, TypeError, KeyError):
        negative.append(label)
        return
    raise AssertionError(label)


samples = [example(suite, mode) for suite in ('two-hop', 'property-only') for mode in ('literal', 'ordinary', 'animated')]
for value in samples:
    assert handler.validate(value) == value['kind']
for label, alter in [
    ('unknown kind', lambda v: v.update(kind='../escape')),
    ('wrong mode join', lambda v: v['observation'].update(mode='literal')),
    ('missing first sample', lambda v: v['observation']['samples'].pop(0)),
    ('out of order samples', lambda v: v['observation']['samples'].reverse()),
    ('extra observation', lambda v: v['observation'].update(extra=True)),
    ('missing pre-membership', lambda v: v['observation'].pop('beforeMembership')),
    ('missing rescue', lambda v: v['observation'].pop('seek751')),
    ('missing animated driver', lambda v: v['observation'].update(driverTiming=None)),
    ('boolean numeric sample', lambda v: v['observation']['samples'][0].update(opacity=True)),
    ('numeric infinity', lambda v: v['observation']['samples'][0].update(opacity=float('inf'))),
    ('string numeric sample', lambda v: v['observation']['samples'][0].update(opacity='bad')),
    ('nonboolean membership', lambda v: v['observation']['membership'].update(child=1)),
]:
    value = example('two-hop', 'animated'); alter(value)
    reject(label, lambda: handler.validate(value))
observed_failure = example('property-only', 'animated')
observed_failure['observation']['beforeMembership'].update(width=28, duration='auto', progress=None)
observed_failure['observation']['same'] = False
assert handler.validate(observed_failure) == observed_failure['kind']
old = {key: os.environ.get(key) for key in ('DURATION_PROGRESS_RECORD_DIR', 'DURATION_PROGRESS_RUN_ID')}
try:
    with tempfile.TemporaryDirectory(prefix='duration-progress-transport-check-') as temporary:
        target = Path(temporary) / 'records'; target.mkdir(mode=0o700)
        os.environ['DURATION_PROGRESS_RECORD_DIR'] = str(target)
        os.environ['DURATION_PROGRESS_RUN_ID'] = 'synthetic_run_123456'
        for value in samples:
            request = SimpleNamespace(method='POST', body=json.dumps(value).encode())
            _, body = handler.main(request, None)
            acknowledgement = json.loads(body)
            path = target / handler.FILES[value['kind']]
            assert acknowledgement == dict(run_id='synthetic_run_123456', kind=value['kind'], sampleCount=4)
            assert json.loads(path.read_bytes()) == dict(run_id='synthetic_run_123456', **value)
            info = path.stat()
            assert stat.S_IMODE(info.st_mode) == 0o600 and info.st_nlink == 1 and info.st_uid == os.getuid()
        before = {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in target.iterdir()}
        request = SimpleNamespace(method='POST', body=json.dumps(samples[0]).encode())
        reject('duplicate exclusive record', lambda: handler.main(request, None))
        reject('wrong HTTP method', lambda: handler.main(SimpleNamespace(method='GET', body=request.body), None))
        reject('oversize body', lambda: handler.main(SimpleNamespace(method='POST', body=b'x'*65537), None))
        reject('non-JSON token', lambda: handler.main(SimpleNamespace(method='POST', body=b'{"kind":NaN}'), None))
        reject('malformed JSON', lambda: handler.main(SimpleNamespace(method='POST', body=b'{'), None))
        os.environ['DURATION_PROGRESS_RUN_ID'] = 'short'
        reject('invalid run identity', lambda: handler.main(request, None))
        os.environ['DURATION_PROGRESS_RUN_ID'] = 'synthetic_run_123456'
        target.chmod(0o755)
        reject('public output directory', lambda: handler.main(request, None))
        target.chmod(0o700)
        link = Path(temporary) / 'link'; link.symlink_to(target, target_is_directory=True)
        os.environ['DURATION_PROGRESS_RECORD_DIR'] = str(link)
        reject('symlink output directory', lambda: handler.main(request, None))
        assert before == {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in target.iterdir()}
finally:
    for key, value in old.items():
        if value is None: os.environ.pop(key, None)
        else: os.environ[key] = value
result = dict(positive_shapes=6, exclusive_roundtrips=6, semantically_failing_observation_preserved=True,
              negative_controls=negative, scratch_removed=not Path(temporary).exists(), browser_executed=False)
(HERE / 'CHECK.json').write_text(json.dumps(result, indent=2)+'\n')
print(json.dumps(result, indent=2))
