import ast
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import sys
import tempfile
from types import SimpleNamespace

assert sys.flags.isolated and sys.flags.no_site and sys.dont_write_bytecode
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PARENT = ROOT / 'artifacts/css-selective-cancellation-after-font-publication-v1'
read = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


rejections = []


def reject(label, fn):
    try:
        fn()
    except (AssertionError, KeyError, RuntimeError):
        rejections.append(label)
    else:
        raise AssertionError(label)


policy = read(HERE / 'POLICY.json')
assert policy['enabled_modes'] == []
assert all(policy[k] is None for k in ('bindings', 'pair_binding', 'stage', 'runtime_output'))
for path, pin in policy['references'].items():
    assert sha(ROOT / path) == pin, path
for path in HERE.glob('*.py'):
    compile(path.read_bytes(), str(path), 'exec')
for name in ('transform.py', 'delivery.py', 'native.patch', 'STAGES.json'):
    assert (HERE / name).read_bytes() == (PARENT / name).read_bytes()
runner = load('checked_runner', HERE / 'run.py')
old_runner = load('old_runner', PARENT / 'run.py')
evidence = load('checked_evidence', HERE / 'evidence.py')
transform = load('checked_transform', HERE / 'transform.py')
owner = load('real_owner', ROOT / 'artifacts/css-registered-number-source-transition-v4/transition.py')
stage, = read(HERE / 'STAGES.json')['stages']
binding = read(HERE / 'PAIR-BINDING.json')
font_record = binding['font_native_receipt']
assert sha(ROOT / font_record['path']) == font_record['sha256']
font = read(ROOT / font_record['path'])
font_stage, = read(ROOT / binding['font_publisher']['directory'] / 'STAGES.json')['stages']
evidence.require_font_receipt(font, font_stage)
actual = ROOT / 'artifacts/css-selective-cancellation-publication-install-failure-v1'
for name, pin in read(actual / 'CONTROL-PINS.json').items():
    assert sha(actual / name) == pin
actual_epoch, actual_owned, actual_role = (read(actual / n) for n in ('CURRENT-EPOCH.json', 'OWNED.json', 'ROLE.json'))
assert sha(actual / 'CURRENT-EPOCH.json') == font['epoch_sha256']
assert actual_epoch['semantic_index']['head'] == font['commit']
uninstalled = runner.UNINSTALLED_SOURCE
assert all(uninstalled not in m for m in (actual_epoch['pins'], actual_epoch['installed_identities'], actual_owned))
assert set(stage['head_preimages']) == runner.INSTALLED_SOURCES | {uninstalled}
source = ROOT / 'artifacts/css-root-font-cancellation-selective-handoff-fix-v1/parent'
publish_tree = ast.parse((HERE / 'publish.py').read_text())
main = next(n for n in publish_tree.body if isinstance(n, ast.FunctionDef) and n.name == 'main')
install = next(n for n in main.body if isinstance(n, ast.If) and isinstance(n.test, ast.Compare) and ast.unparse(n.test) == 'installed is None')
assert ast.unparse(install.body[0]) == "binding['source_claims'] = {}"
claim_loop = compile(ast.fix_missing_locations(ast.Module(body=install.body[:2], type_ignores=[])), str(HERE / 'publish.py'), 'exec')
with tempfile.TemporaryDirectory(prefix='selective-unpinned-publication-', dir='/private/tmp') as temporary:
    scratch = Path(temporary)
    epoch, owned = copy.deepcopy(actual_epoch), copy.deepcopy(actual_owned)
    for path, pin in stage['head_preimages'].items():
        target = scratch / path
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source / path, target)
        assert sha(target) == pin
        if path in runner.INSTALLED_SOURCES:
            claim = owner.claim(scratch, path, pin)
            epoch['installed_identities'][path] = claim['identity']
            owned[path] = claim
    ownership_path = scratch / 'OWNED.json'
    ownership_path.write_text(json.dumps(owned))
    def head_blob(*args):
        assert args[0] == 'show' and args[1].startswith(font['commit'] + ':')
        return (source / args[1].split(':', 1)[1]).read_bytes()
    environment = dict(binding={},stage=stage,epoch=epoch,owner=owner,ROOT=scratch,RUNTIME=scratch,
                       runner=SimpleNamespace(git=head_blob,claim_source=runner.claim_source),head=font['commit'],
                       hashlib=hashlib,read=read)
    exec(claim_loop, environment)
    claims = environment['binding']['source_claims']
    assert set(claims) == set(stage['head_preimages'])
    claim = claims[uninstalled]; pin = stage['head_preimages'][uninstalled]
    assert runner.claim_source(owner, scratch, actual_epoch, actual_owned, uninstalled, pin, claim) == claim
    reject('old content-pin assumption rejects genuine absent pin', lambda: old_runner.claim_source(owner, scratch, actual_epoch, actual_owned, uninstalled, pin, claim))
    for label, field, value in [('unexpected pin', 'pins', pin), ('null pin is not absence', 'pins', None), ('unexpected installed identity', 'installed_identities', claim['identity'])]:
        bad = copy.deepcopy(actual_epoch); bad[field][uninstalled] = value
        reject(label, lambda: runner.claim_source(owner, scratch, bad, actual_owned, uninstalled, pin, claim))
    bad_owned = dict(actual_owned); bad_owned[uninstalled] = claim
    reject('unexpected prior ownership', lambda: runner.claim_source(owner, scratch, actual_epoch, bad_owned, uninstalled, pin, claim))
    bad_environment = dict(environment, binding={}, runner=SimpleNamespace(git=lambda *a:b'wrong HEAD blob', claim_source=runner.claim_source))
    reject('publisher actual loop rejects wrong HEAD blob', lambda: exec(claim_loop, bad_environment))
    for path in stage['head_preimages']:
        target = scratch / path; saved = target.with_suffix('.retained')
        target.rename(saved); target.write_bytes(saved.read_bytes())
        reject('same-byte replacement ' + path, lambda: runner.claim_source(owner, scratch, epoch, owned, path, stage['head_preimages'][path], claims[path]))
        target.unlink(); saved.rename(target)
    for path in runner.INSTALLED_SOURCES:
        bad = copy.deepcopy(epoch); bad['pins'].pop(path)
        reject('installed source still requires pin ' + path, lambda: runner.claim_source(owner, scratch, bad, owned, path, stage['head_preimages'][path], claims[path]))
    post_claims = {path:dict(claims.get(path, {'path':path,'identity':[1,i+1]}),owned_sha256=record['sha256']) for i,(path,record) in enumerate(stage['files'].items())}
    installed,new_owned,new_role = transform.installed(actual_epoch,actual_owned,actual_role,stage,post_claims,{'raw_index':'synthetic-index'},actual_epoch['semantic_index'],'synthetic-manifest','synthetic-label')
    assert installed['pins'][uninstalled] == stage['files'][uninstalled]['sha256']
    assert installed['installed_identities'][uninstalled] == post_claims[uninstalled]['identity']
    assert new_owned[uninstalled] == post_claims[uninstalled]
    assert installed['counts']['roles'] == len(actual_epoch['pins']) + 3
    assert installed['keyframe_font_unit_publication'] == actual_epoch['keyframe_font_unit_publication']
    assert all(new_owned[k] == v for k,v in actual_owned.items() if k not in stage['files'])
    committed = transform.committed(installed,stage['stage'],{'raw_index':'synthetic-end'},dict(actual_epoch['semantic_index'],head='synthetic-commit'),'synthetic-commit')
    assert committed['pins'][uninstalled] == installed['pins'][uninstalled]
    assert committed['modified_native_paths'] == []
assert not scratch.exists()
research = {'committed':True,'signature_verified':True,'accepted_fix_increment':0,'native_working_diff_preserved':True,'head':'1'*40,'parent':font['commit'],'epoch_sha256':'2'*64}
calls = []
def history(*args):
    calls.append(args)
    if args[0] == 'rev-list': return (research['head']+' '+font['commit']).encode()
    if args[0] == 'diff': return b'artifacts/example.json'
    if args[0] in ('-c','merge-base'): return b''
    raise AssertionError(args)
evidence.verify_research_history(history,'signers',research,font,research['head'])
assert {a[0] for a in calls} == {'rev-list','diff','-c','merge-base'}
for key,value in [('committed',False),('signature_verified',False),('accepted_fix_increment',1),('native_working_diff_preserved',False),('parent','3'*40),('head',font['commit'])]:
    bad=dict(research);bad[key]=value
    reject('research receipt '+key,lambda:evidence.verify_research_history(history,'signers',bad,font,research['head']))
for label,command,value in [('extra native change','diff',b'servo/other.rs'),('merge parent','rev-list',b'wrong'),('ancestry failure','merge-base',b'not ancestor')]:
    def changed(*args):return value if args[0]==command else history(*args)
    reject(label,lambda:evidence.verify_research_history(changed,'signers',research,font,research['head']))
def unsigned(*args):
    assert args[0] != '-c'
    return history(*args)
reject('fresh signature failure',lambda:evidence.verify_research_history(unsigned,'signers',research,font,research['head']))
for name in ('verify_completed','verify_font_history','verify_root_self','require_root_self_signatures','compare_lane','archived'):
    def body(path):
        tree=ast.parse(path.read_text());node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==name)
        return ast.dump(node,include_attributes=False)
    assert body(HERE/'evidence.py') == body(PARENT/'evidence.py'),name
start='            with tempfile.TemporaryDirectory('
new=(HERE/'run.py').read_text();old=(PARENT/'run.py').read_text()
assert new[new.index(start):] == old[old.index(start):]
print(json.dumps({'references':len(policy['references']),'negative_controls':rejections,'actual_absent_pin_epoch_sha256':sha(actual/'CURRENT-EPOCH.json'),'actual_font_receipt_sha256':sha(ROOT/font_record['path']),'production_publish_claim_loop_exercised':True,'real_claim_inode_controls':3,'pure_transforms':2,'source_fixture_scope':'Actual post-font controls; temporary file identities substituted only for installed-source ownership tests. New source absence retained exactly.','future_research_history_protocol_double':True,'completed_evidence_functions_unchanged':True,'unchanged_saved_browser_restoration_replay_not_repeated':True,'signing_rollback_tail_exact':True,'scratch_removed':str(scratch),'live_actions':False},sort_keys=True))
