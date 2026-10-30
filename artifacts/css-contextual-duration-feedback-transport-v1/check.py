import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import tempfile
from types import SimpleNamespace

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
V1 = ROOT / 'artifacts/css-contextual-duration-regression-plan-v1'
V2 = ROOT / 'artifacts/css-contextual-duration-regression-plan-v2'
WPT = ROOT / 'testing/web-platform/tests'
sys.path[:0] = [str(p) for p in (WPT / 'tools/third_party').iterdir() if p.is_dir()] + [str(WPT / 'tools'), str(WPT)]
import html5lib
from manifest.manifest import Manifest
from tools.lint import lint

for path, expected in json.loads((PACKAGE / 'REFERENCES.json').read_text()).items():
    assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == expected
name = 'animation-duration-self-feedback-observation.tentative.html'
path = 'css/css-animations/' + name
handler_path = 'css/css-animations/duration-feedback-record.py'
source = (PACKAGE / name).read_text()
start = source.index('  const record = records[records.length - 1];')
end = source.index('  assert_equals(samples.length, 8,', start)
assert source[:start] + source[end:] == (V2 / name).read_text()
assert source.index('samples.push(sample);') < source.index('output.textContent = JSON.stringify(records);') < start
assert source.count('fetch(') == 1
scripts = [node.text or '' for node in html5lib.parse(source, namespaceHTMLElements=False).iter('script')
           if not node.get('src') and node.get('type') != 'application/json']
assert len(scripts) == 1
program = "const vm=require('vm');let s='';process.stdin.on('data',x=>s+=x);process.stdin.on('end',()=>{const names=[];vm.runInNewContext(s,{promise_test:(fn,name)=>names.push(name)});process.stdout.write(JSON.stringify(names));});"
names = json.loads(subprocess.run(['node', '-e', program], input=scripts[0], text=True,
                                  capture_output=True, check=True).stdout)
assert names == json.loads((V2 / 'CHECK.json').read_text())['registered_names']

spec = importlib.util.spec_from_file_location('duration_record', PACKAGE / 'duration-feedback-record.py')
handler = importlib.util.module_from_spec(spec)
spec.loader.exec_module(handler)
run_id = 'static-test-owner-0123456789'
fields = {'font': '24px', 'cssDuration': '1.5s', 'opacity': '0.5',
          'repeatFont': '16px', 'repeatDuration': '1s',
          'effects': [{'name': 'fontCycle', 'time': 750, 'duration': 1500,
                       'progress': 0.5, 'state': 'paused'}]}
positive = 0
negative = 0
with tempfile.TemporaryDirectory(prefix='duration-transport-check-') as temporary:
    directory = Path(temporary) / 'records'
    directory.mkdir(mode=0o700)
    old_environment = {key: os.environ.get(key) for key in ['DURATION_FEEDBACK_RECORD_DIR', 'DURATION_FEEDBACK_RUN_ID']}
    os.environ['DURATION_FEEDBACK_RECORD_DIR'] = str(directory)
    os.environ['DURATION_FEEDBACK_RUN_ID'] = run_id
    def snapshot():
        return {p.name: p.read_bytes() for p in directory.iterdir() if p.is_file() and not p.is_symlink()}
    def invoke(value, method='POST'):
        return handler.main(SimpleNamespace(method=method, body=json.dumps(value).encode()), None)
    def reject(call):
        global negative
        before = snapshot()
        try:
            call()
        except (AssertionError, ValueError, TypeError, KeyError, OSError):
            pass
        else:
            raise AssertionError('Negative transport control accepted')
        assert snapshot() == before
        negative += 1
    try:
        for kind, filename in handler.FILES.items():
            sample = copy.deepcopy(fields)
            if kind == 'coupled font and opacity':
                sample['effects'].append({'name': 'fade', 'time': 750, 'duration': 'auto',
                                          'progress': None, 'state': 'paused'})
            value = {'kind': kind, 'samples': [copy.deepcopy(sample) for _ in range(8)]}
            headers, body = invoke(value)
            assert dict(headers)[b'Content-Type'] == b'application/json'
            assert json.loads(body) == {'run_id': run_id, 'kind': kind, 'sampleCount': 8}
            assert json.loads((directory / filename).read_text()) == {'run_id': run_id, **value}
            assert stat.S_IMODE((directory / filename).stat().st_mode) == 0o600
            reject(lambda: invoke(value))
            positive += 1
        for p in directory.iterdir():
            p.unlink()
        value = {'kind': 'self font', 'samples': [copy.deepcopy(fields) for _ in range(8)]}
        wrong = copy.deepcopy(value); wrong['kind'] = '../escape'
        reject(lambda: invoke(wrong))
        wrong = copy.deepcopy(value); wrong['samples'].pop()
        reject(lambda: invoke(wrong))
        wrong = copy.deepcopy(value); wrong['samples'].append(copy.deepcopy(fields))
        reject(lambda: invoke(wrong))
        wrong = copy.deepcopy(value); wrong['extra'] = 'unexpected'
        reject(lambda: invoke(wrong))
        wrong = copy.deepcopy(value); wrong['samples'][0]['extra'] = 1
        reject(lambda: invoke(wrong))
        wrong = copy.deepcopy(value); wrong['samples'][0]['effects'] = []
        reject(lambda: invoke(wrong))
        wrong = copy.deepcopy(value); wrong['samples'][0]['effects'][0]['progress'] = True
        reject(lambda: invoke(wrong))
        reject(lambda: invoke(value, 'GET'))
        reject(lambda: handler.main(SimpleNamespace(method='POST', body=b'{' + b' ' * 65536), None))
        reject(lambda: handler.main(SimpleNamespace(method='POST', body=b'{'), None))
        reject(lambda: handler.main(SimpleNamespace(method='POST', body=b'{"kind": NaN}'), None))
        os.environ['DURATION_FEEDBACK_RUN_ID'] = 'short'
        reject(lambda: invoke(value))
        os.environ['DURATION_FEEDBACK_RUN_ID'] = run_id
        os.environ['DURATION_FEEDBACK_RECORD_DIR'] = 'relative'
        reject(lambda: invoke(value))
        os.environ['DURATION_FEEDBACK_RECORD_DIR'] = str(directory)
        directory.chmod(0o755)
        reject(lambda: invoke(value))
        directory.chmod(0o700)
        alias = Path(temporary) / 'alias';alias.symlink_to(directory, target_is_directory=True)
        os.environ['DURATION_FEEDBACK_RECORD_DIR'] = str(alias)
        reject(lambda: invoke(value))
        os.environ['DURATION_FEEDBACK_RECORD_DIR'] = str(directory)
        destination = Path(temporary) / 'unrelated';destination.write_text('retained')
        (directory / 'self.json').symlink_to(destination)
        reject(lambda: invoke(value))
        assert destination.read_text() == 'retained'
    finally:
        for key, old in old_environment.items():
            if old is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = old

with tempfile.TemporaryDirectory(prefix='duration-transport-manifest-') as temporary:
    scratch = Path(temporary)
    shutil.copytree(V1 / 'capture/tests', scratch, dirs_exist_ok=True)
    (scratch / path).write_text(source)
    shutil.copyfile(PACKAGE / 'duration-feedback-record.py', scratch / handler_path)
    (scratch / 'lint.ignore').write_text('')
    pages = [page.lstrip('/') for page in json.loads((V1 / 'CAPTURE.json').read_text())['pages']]
    manifest = Manifest(str(scratch), '/')
    manifest.update([(page, None, True) for page in pages + [handler_path]], parallel=False)
    serialized = json.loads(json.dumps(manifest.to_json()))
    previous = json.loads((V2 / 'SUBSET-MANIFEST.json').read_text())
    previous['items']['testharness']['css']['css-animations'][name] = serialized['items']['testharness']['css']['css-animations'][name]
    for kind, data in previous['items'].items():
        assert serialized['items'][kind] == data
    assert set(serialized['items']) - set(previous['items']) <= {'support'}
    (PACKAGE / 'SUBSET-MANIFEST.json').write_text(json.dumps(serialized, indent=2, sort_keys=True) + '\n')
    directory = os.getcwd()
    try:
        os.chdir(scratch)
        assert lint.lint(str(scratch), [path, handler_path], 'normal', jobs=1) == 0
    finally:
        os.chdir(directory)
record = {'registered_names': names, 'sampling_and_existing_assertions_byte_identical': True,
          'post_after_complete_samples': True, 'positive_transport_cases': positive,
          'negative_transport_cases': negative, 'browser_callbacks_executed': False,
          'http_server_executed': False, 'lint_errors': 0, 'scratch_removed': True}
(PACKAGE / 'CHECK.json').write_text(json.dumps(record, indent=2, sort_keys=True) + '\n')
print(json.dumps(record))
