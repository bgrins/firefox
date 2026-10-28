import ast
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import tempfile

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
spec = importlib.util.spec_from_file_location('owner',REPO/'artifacts/css-registered-number-source-transition-v4/transition.py')
owner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(owner)
tree = ast.parse((HERE/'run.py').read_text())
apply_nodes = [n for n in ast.walk(tree) if isinstance(n,ast.For) and 'ownership.write_owned(ROOT, source_claims[source], candidates[source])' in ast.unparse(n)]
restore_nodes = [n for n in ast.walk(tree) if isinstance(n,ast.For) and 'ownership.write_owned(ROOT, source_claims[source], bases[source])' in ast.unparse(n)]
apply_node = min(apply_nodes,key=lambda n:len(ast.unparse(n)))
restore_node = min(restore_nodes,key=lambda n:len(ast.unparse(n)))
apply_code = compile(ast.Module(body=[apply_node],type_ignores=[]),'actual-apply-loop','exec')
restore_code = compile(ast.Module(body=[restore_node],type_ignores=[]),'actual-restore-loop','exec')
results = []
for case in ('normal','partial-third-write','foreign-body','foreign-inode'):
    with tempfile.TemporaryDirectory(prefix='counter-four-source-',dir='/private/tmp') as tmp:
        root = Path(tmp)
        bases = {str(n)+'.rs':('base'+str(n)).encode() for n in range(4)}
        candidates = {n:b+b'-candidate' for n,b in bases.items()}
        for n,b in bases.items():(root/n).write_bytes(b)
        (root/'accepted-font.rs').write_bytes(b'accepted')
        claims = {n:owner.claim(root,n,hashlib.sha256(b).hexdigest()) for n,b in bases.items()}
        class Writer:
            def write_owned(self,root,claim,body):
                if case=='partial-third-write' and claim['path']=='2.rs' and body==candidates['2.rs']:
                    owner.write_owned(root,claim,body[:3])
                    raise OSError('simulated partial candidate write')
                return owner.write_owned(root,claim,body)
        ns = {'ROOT':root,'policy':{'source_roles':dict.fromkeys(bases)},'source_claims':claims,'bases':bases,'candidates':candidates,'ownership':Writer(),'restoration_errors':[]}
        try:
            exec(apply_code,ns)
            assert case!='partial-third-write'
        except OSError:
            assert case=='partial-third-write'
        if case=='foreign-body':(root/'2.rs').write_bytes(b'foreign')
        if case=='foreign-inode':
            (root/'replacement').write_bytes(candidates['2.rs'])
            os.replace(root/'replacement',root/'2.rs')
        exec(restore_code,ns)
        blocked=case.startswith('foreign')
        assert len(ns['restoration_errors'])==(1 if blocked else 0)
        assert all((root/n).read_bytes()==b for n,b in bases.items() if not(blocked and n=='2.rs'))
        assert (root/'accepted-font.rs').read_bytes()==b'accepted'
        if case=='foreign-body':assert (root/'2.rs').read_bytes()==b'foreign'
        if case=='foreign-inode':assert (root/'2.rs').read_bytes()==candidates['2.rs']
        results.append(case)
print(json.dumps({'actual_owner_loop_controls':results,'all_other_sources_restored_after_rejected_source':True,'scratch_removed':True,'main_executed':False,'live_source_reads':False}))
