import ast
import copy
import importlib.util
import json
import os
from pathlib import Path
import signal
import tempfile
import textwrap

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
owner = load('owner', ROOT/'artifacts/css-registered-number-source-transition-v4/transition.py')
create = load('creation', ROOT/'artifacts/css-registered-admission-wpt-install-v1/install.py')
source = (HERE/'install.py').read_text()
start = source.index('        current = copy.deepcopy(epoch)')
forward = textwrap.dedent(source[start:source.index('        index = s.h.index_state',start)])
start = source.index('            for test, item in reversed(list(created.items())):')
reverse = textwrap.dedent(source[start:source.index('            restored = copy.deepcopy(epoch)',start)])
ast.parse(forward); ast.parse(reverse)
results = []
for fault in ('none','third-source-write','after-retirement'):
    with tempfile.TemporaryDirectory(prefix='counter-promotion-transaction-') as tmp:
        root = Path(tmp).resolve()
        output = root/'runtime'; output.mkdir()
        bases = {f'source-{n}.rs':f'base-{n}'.encode() for n in range(4)}
        desired = {n:b'candidate-'+body for n,body in bases.items()}
        for n,body in bases.items(): (root/n).write_bytes(body)
        overwritten,retired,created_test = 'ordinary.html','old-api.html','new-values.html'
        original_tests = {overwritten:b'old ordinary',retired:b'old registered'}
        for n,body in original_tests.items(): (root/n).write_bytes(body)
        source_claims = {n:owner.claim(root,n,owner.digest(body)) for n,body in bases.items()}
        existing = {n:owner.claim(root,n,owner.digest(body)) for n,body in original_tests.items()}
        original_ids = {n:v['identity'][:] for n,v in {**source_claims,**existing}.items()}
        parents = {n:create.parent_pins(root,root/n) for n in (overwritten,retired,created_test)}
        class Helper:
            def __getattr__(self, name): return getattr(owner,name)
            def write_owned(self, root, claim, body):
                owner.write_owned(root,claim,body)
                if fault == 'third-source-write' and claim['path'] == 'source-2.rs' and body == desired['source-2.rs']:
                    raise RuntimeError('injected source failure after owned write')
            def save(self, path, data):
                owner.save(path,data)
                if fault == 'after-retirement' and path.name == 'RETIREMENT.json':
                    raise RuntimeError('injected receipt failure after retirement')
        scope = dict(copy=copy,os=os,signal=signal,ROOT=root,output=output,h=Helper(),create=create,
            source_claims=source_claims,bases=bases,desired=desired,owned={},existing=existing,
            original_tests=original_tests,tests={overwritten:b'landing ordinary',created_test:b'landing registered'},
            parents=parents,overwritten=overwritten,retired=retired,created_test=created_test,
            changed=[],created={},test_changed=False,retirement=None,
            epoch={'pins':{},'installed_identities':{},'counts':{'roles':0,'installed_identities':0}},
            policy={'sources':{n:{'candidate_sha256':owner.digest(body)} for n,body in desired.items()}})
        caught = None
        try: exec(compile(forward,'actual-install-forward','exec'),scope)
        except RuntimeError as error: caught = str(error)
        assert (caught is None) == (fault == 'none')
        if fault == 'none':
            assert not (root/retired).exists() and (root/created_test).read_bytes() == b'landing registered'
        exec(compile(reverse,'actual-install-rollback','exec'),scope)
        assert not (root/created_test).exists()
        assert not (output/'RETIRED-WPT.html').exists()
        for n,body in {**bases,**original_tests}.items():
            owner.claim(root,n,owner.digest(body),original_ids[n])
        results.append({'case':fault,'all_original_bytes_and_inodes_restored':True})
print(json.dumps({'actual_code_fragments':True,'cases':results,'live_sources_or_controls_touched':False}))
