import ast
import builtins
import copy
import dis
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
from types import CodeType, SimpleNamespace


assert sys.flags.isolated and sys.flags.no_site and sys.dont_write_bytecode
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
read = lambda path: json.loads(path.read_bytes())
spec = importlib.util.spec_from_file_location('new_direct_capture', HERE/'baseline.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
binding = module.binding
records = {key:module.equivalence.decode((ROOT/path).read_bytes()) for key,path in binding['saved_inputs'].items()}
receipt = records['native_receipt']
actual = module.saved_native_state(receipt)
assert actual == records['post']
negative = []


def rejects(label, action):
    try:
        action()
    except (AssertionError, KeyError, ValueError, RuntimeError):
        negative.append(label)
    else:
        raise AssertionError('accepted '+label)


for label, path, value in (
    ('origin-epoch', ['native_receipt','epoch_sha256'], '0'*64),
    ('other-epoch-state', ['current_epoch','counts','roles'], 1),
    ('epoch-int-as-bool', ['current_epoch','counts','native_modified_paths'], False),
    ('epoch-int-as-float', ['current_epoch','counts','native_modified_paths'], 0.0),
    ('snapshot-nested-raw', ['post','nested_index','raw_index'], '0'*64),
    ('current-raw-join', ['current_epoch','raw_index_observation','current'], '0'*64),
    ('original-capture-join', ['original_capture','prior_receipt_sha256'], '0'*64),
    ('refresh-result-join', ['terminal','result_sha256'], '0'*64),
    ('verification-post-join', ['verification','post_sha256'], '0'*64),
    ('terminal-bool-as-int', ['verification_terminal','exit'], False),
):
    changed = copy.deepcopy(records)
    target = changed
    for key in path[:-1]: target = target[key]
    target[path[-1]] = value
    rejects(label, lambda: module.compare_saved(receipt,changed))


def global_names(code):
    result = {i.argval for i in dis.get_instructions(code) if i.opname == 'LOAD_GLOBAL'}
    for item in code.co_consts:
        if isinstance(item, CodeType): result |= global_names(item)
    return result


required = global_names(module.observe.__code__) | global_names(module.claim_additional_sources.__code__)
assert required <= set(module.__dict__) | set(vars(builtins)), required-set(module.__dict__)-set(vars(builtins))
for name in ('RUNTIME','read','sha','digest','load','environment','metadata_guard','require_role'):
    assert module.__dict__[name] is getattr(module.core,name)
for name in ('environment','load','RUNTIME','require_role','metadata_guard','sha'):
    assert name in required
    missing = set(module.__dict__) - {name}
    rejects('missing-observer-global-'+name, lambda: module.equivalence.require(required <= missing | set(vars(builtins)), 'undefined global'))

previous = ROOT/'artifacts/css-root-font-cancellation-trace-current-capture-v1'
assert (HERE/'capture_current.py').read_bytes() == (previous/'capture_current.py').read_bytes()
source = (HERE/'baseline.py').read_text()
old_source = (previous/'baseline.py').read_text()
def function(text,name):
    return ast.get_source_segment(text,next(n for n in ast.parse(text).body if isinstance(n,ast.FunctionDef) and n.name==name))
assert function(source,'claim_additional_sources') == function(old_source,'claim_additional_sources').replace("{'servo/components/style/traversal.rs', 'servo/components/style/data.rs'}","{'servo/components/style/traversal.rs', 'servo/components/style/gecko/traversal.rs'}")
core_source = (ROOT/'artifacts/css-prioritary-published-original-v1/baseline.py').read_text()
expected = function(core_source,'observe').replace("    assert checkpoint['committed'] and checkpoint['signature_verified']\n", "    native_receipt = checkpoint\n    expected_snapshot = saved_native_state(native_receipt)\n    native_head = native_receipt['commit']\n").replace("checkpoint['epoch_sha256']","binding['current_epoch_sha256']").replace("checkpoint['head']",'native_head')
executed = (ROOT/binding['executed_owner']['directory']/'baseline.py').read_text()
a=executed.index("    assert not state.h.git(ROOT, env, 'merge-base'",executed.index('def observe('));b=executed.index('    metadata_guard(policy)',a)
git=executed[a:b].replace("adapter.binding['native_parent']","binding['native_parent']")
expected=expected.replace("    assert not state.h.git(ROOT, env, 'merge-base', '--is-ancestor', policy['image_commit'], native_head)\n",git)
a=old_source.index("    for name, pin in binding['source_preimages'].items():",old_source.index('def observe('));b=old_source.index('    return result',a)
tail=old_source[a:b].replace("checkpoint['head']",'native_head')
line='    return state, env, controls, epoch, role, sources, flags, snapshot'
expected=expected.replace(line,"    equivalence.equal(snapshot, expected_snapshot, 'fresh whole state equals saved direct target')\n"+tail+line)
assert function(source,'observe') == expected
assert not any(isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr in ('native_head_view','validate_refresh','observe') for n in ast.walk(ast.parse(source)))

ownership=module.core.load('real_capture_ownership','artifacts/css-registered-number-source-transition-v4/transition.py')
sources=read(ROOT/binding['source_binding']['directory']/'SOURCE-ROLES.json')['roles']
assert set(sources)=={'servo/components/style/traversal.rs','servo/components/style/gecko/traversal.rs','servo/ports/geckolib/glue.rs'}
assert set(binding['additional_sources'])==set(sources)-{'servo/ports/geckolib/glue.rs'}
for name,row in binding['additional_sources'].items():
    assert row['base_sha256']==sources[name]['base_sha256']==sha(ROOT/row['base_capture'])
assert records['current_epoch']['pins']['servo/ports/geckolib/glue.rs']==sources['servo/ports/geckolib/glue.rs']['base_sha256']
with tempfile.TemporaryDirectory(prefix='css-normal-handoff-capture-check-',dir='/private/tmp') as temporary:
    scratch=Path(temporary)
    bodies={name:(ROOT/row['base_capture']).read_bytes() for name,row in binding['additional_sources'].items()}
    for name,row in binding['additional_sources'].items():
        for relative in (name,row['base_capture']):
            path=scratch/relative;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(bodies[name])
    def git(root,env,*args):
        assert root==scratch and args[0]=='show' and args[1].startswith(receipt['commit']+':')
        return bodies[args[1].split(':',1)[1]]
    state=SimpleNamespace(h=SimpleNamespace(git=git))
    try:
        module.ROOT=scratch
        claims=module.claim_additional_sources(ownership,state,{},records['current_epoch'],receipt['commit'])
        for name in binding['additional_sources']:
            changed=copy.deepcopy(records['current_epoch']);changed['installed_identities'][name]=[1,2]
            rejects('additional-misclassified-canonical-'+name,lambda:module.claim_additional_sources(ownership,state,{},changed,receipt['commit']))
            path=scratch/name;path.rename(path.with_suffix('.retained'));path.write_bytes(bodies[name])
            claim=claims[name]
            rejects('same-byte-new-inode-'+name,lambda:ownership.claim(scratch,name,claim['owned_sha256'],claim['identity']))
    finally:
        module.ROOT=ROOT
assert not scratch.exists()
print(json.dumps({'success':True,'saved_direct_epoch_and_snapshot_verified':True,'references':len(binding['references']),'source_roles':3,'additional_claims':sorted(binding['additional_sources']),'negative_controls':negative,'ordinary_claim_body_preserved':True,'live_observer_preserved_by_exact_transform':True,'resolved_observer_globals':sorted(required),'capture_script_byte_identical':True,'git_test_double':True,'scratch_removed':True,'live_observe_or_capture_executed':False,'tested_inputs':{n:sha(HERE/n) for n in ('baseline.py','capture_current.py','BINDINGS.json','check_saved.py')}},indent=2,sort_keys=True))
