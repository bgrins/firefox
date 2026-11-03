import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import sys
import tempfile

assert sys.flags.isolated and sys.flags.no_site and sys.dont_write_bytecode
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
read = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
for path,pin in read(HERE/'REFERENCES.json').items():
    assert sha(ROOT/path)==pin
policy=read(HERE/'POLICY.json')
assert not policy['execution_enabled'] and not policy['publication_enabled']
assert policy['candidate_smil_evidence'] is None and policy['current_authority'] is None
spec=importlib.util.spec_from_file_location('delivery', HERE/'delivery.py')
delivery=importlib.util.module_from_spec(spec);spec.loader.exec_module(delivery)
stage=read(HERE/'WPT-STAGE.json')
assert set(stage['files']) == set(stage['create_tests']) == delivery.TESTHARNESS | delivery.SUPPORT
assert set(stage['testharness_paths']) == delivery.TESTHARNESS and set(stage['support_paths']) == delivery.SUPPORT
assert len(stage['testharness_paths']) == len(stage['support_paths']) == 2
waapi=read(ROOT/'artifacts/css-root-self-animation-context-fix-v3/MANIFEST.json')
smil=read(ROOT/'artifacts/css-root-self-smil-coverage-probe-v1/MANIFEST.json')
assert waapi['version'] == smil['version'] == 9 and waapi['url_base'] == smil['url_base'] == '/'
manifest=copy.deepcopy(smil)
manifest['items']['testharness']['web-animations']=copy.deepcopy(waapi['items']['testharness']['web-animations'])
negatives=[]
def reject(label, fn):
    try:
        fn()
    except (AssertionError, KeyError, FileNotFoundError):
        negatives.append(label)
    else:
        raise AssertionError(label)
with tempfile.TemporaryDirectory(prefix='root-self-support-delivery-',dir='/private/tmp') as directory:
    scratch=Path(directory);delivery.ROOT=scratch;tests=scratch/'testing/web-platform/tests'
    for name,record in stage['files'].items():
        source=ROOT/record['path'];assert sha(source)==record['sha256']
        target=scratch/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target)
    files={n:r['sha256'] for n,r in stage['files'].items()}
    assert delivery.verify_entries(manifest,tests,files)==sorted('/'+str(Path(n).relative_to('testing/web-platform/tests')) for n in delivery.TESTHARNESS)
    def check(m):return delivery.verify_entries(m,tests,files)
    for label,mutate in [
      ('wrong manifest version',lambda m:m.update(version=8)),
      ('wrong URL base',lambda m:m.update(url_base='/wrong/')),
      ('unexpected item kind',lambda m:m['items'].update(manual={})),
      ('missing support tree',lambda m:m['items'].pop('support')),
      ('support assigned runnable metadata',lambda m:m['items']['support']['svg']['animations']['resources']['root-font-target.svg'].__setitem__(1,[None,{}])),
      ('wrong support blob',lambda m:m['items']['support']['svg']['animations']['resources']['root-font-target.svg'].__setitem__(0,'wrong')),
      ('unexpected support resource',lambda m:m['items']['support']['svg']['animations']['resources'].update(extra=['wrong',[]])),
      ('SMIL timeout omitted',lambda m:m['items']['testharness']['svg']['animations']['root-font-self-reference.html'].__setitem__(1,[None,{}])),
      ('WAAPI timeout omitted',lambda m:m['items']['testharness']['web-animations']['animation-model']['keyframe-effects']['root-font-self-reference.html'].__setitem__(1,[None,{}])),
      ('SVG misclassified as testharness',lambda m:m['items']['testharness']['svg']['animations'].update(resources=m['items']['support']['svg']['animations'].pop('resources')))]:
        m=copy.deepcopy(manifest);mutate(m);reject(label,lambda:check(m))
    missing=dict(files);missing.pop(next(iter(delivery.SUPPORT)))
    reject('support omitted from selected files',lambda:delivery.verify_entries(manifest,tests,missing))
    extra=dict(files);extra['testing/web-platform/tests/svg/animations/resources/other.svg']='wrong'
    reject('unexpected selected file',lambda:delivery.verify_entries(manifest,tests,extra))
    support=scratch/next(iter(delivery.SUPPORT));before=support.read_bytes();support.write_bytes(before+b' ')
    reject('changed support bytes',lambda:check(manifest));support.write_bytes(before)
    assert delivery.verify_entries(manifest,tests,files)
assert not scratch.exists()
print(json.dumps({'saved_only':True,'genuine_manifest_version':9,'testharness_pages':2,'support_files':2,'selected_WPT_files':4,'negative_controls':negatives,'scratch_removed':str(scratch),'candidate_smil_outcome_pending':True,'lint_browser_git_live_operations':False}))
