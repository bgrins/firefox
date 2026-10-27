import hashlib, json, os, subprocess, tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
pre=json.loads((HERE/'PREIMAGES.json').read_text())
post=json.loads((HERE/'POSTIMAGES.json').read_text())
assert set(pre)==set(post) and len(pre)==5
for n,digest in pre.items():assert sha(HERE/'original'/n)==digest,n
for n,digest in post.items():assert sha(HERE/'candidate'/n)==digest,n
cascade=(HERE/'candidate/servo/components/style/properties/cascade.rs').read_text()
assert cascade.count('if !self.allows_custom_property(context, name, &priority)')==2
collection=cascade[cascade.index('fn collect_custom_winner('):cascade.index('/// Cascade a given custom property declaration.')]
assert 'value_may_affect_style' not in collection
assert 'self.seen.custom.var.entry(name)' in collection
assert '.add(priority, kind)' in collection
assert 'entry.insert(true)' in collection
assert collection.index('revert_kind()')<collection.index('entry.insert(true)')
walk=cascade[cascade.index('pub(crate) fn collect_custom_winners'):cascade.index("fn iter_declarations<'c")]
assert 'rules.self_and_ancestors()' in walk
assert walk.index('rule.pending_customs()')<walk.index('declaration_importance_iter()')
assert 'rule.has_pending_custom(&declaration.name)' in walk
source=(HERE/'candidate/servo/components/style/animation_rule_sample.rs').read_text()
assert '#[cfg(test)]\n    pub(crate) fn new_pending_for_testing' in source
assert 'pending_custom: Default::default()' in source
native=(HERE/'candidate/servo/components/style/native_provider_completion.rs').read_text()
assert 'Ordinary(crate::properties::CustomDeclaration)' in native
assert 'Winner::Pending(winner)' in native
validation=HERE/'validation';validation.mkdir(exist_ok=False)
results=[]
with tempfile.TemporaryDirectory(prefix='css-winning-admission-',dir='/private/tmp') as tmp:
 root=Path(tmp)
 for n in pre:
  p=root/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((HERE/'original'/n).read_bytes())
 for phase,args,pins in [('forward',['apply',str(HERE/'native.patch')],post),('reverse',['apply','--reverse',str(HERE/'native.patch')],pre)]:
  r=subprocess.run(['git','--no-optional-locks','-c','core.fsmonitor=false',*args],cwd=root,capture_output=True,text=True,env=dict(os.environ,GIT_OPTIONAL_LOCKS='0'))
  (validation/(phase+'.log')).write_text(r.stdout+r.stderr)
  assert r.returncode==0,(phase,r.stderr)
  assert {n:sha(root/n) for n in pins}==pins
  results.append({'phase':phase,'exit':r.returncode,'five_bodies_exact':True})
assert not root.exists()
result={'status':'WINNING_ADMISSION_SOURCE_TRANSPORT_PASS','paths':5,'patch_transport':results,'scratch_removed':True,'shared_real_gate_checked':True,'ordinary_winners_retained_unresolved':True,'pending_only_rule_replacement_path_included':True,'native_compiled':False,'native_tests_executed':False,'browser_tested':False,'gecko_gtest_constructor_availability':'UNRESOLVED_CFG_TEST_NOT_ENABLED_IN_STYLE_DEPENDENCY','normal_producer_activated':False}
(validation/'CHECK.json').write_text(json.dumps(result,indent=2)+'\n')
print(result['status'])
