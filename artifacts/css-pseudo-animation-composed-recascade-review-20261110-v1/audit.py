import difflib, hashlib, json, os, shutil, subprocess, sys, tempfile
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent; ROOT=HERE.parent.parent
SOURCE=ROOT/'artifacts/css-pseudo-animation-composed-recascade-20261110-v1'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
manifest=json.loads((SOURCE/'SOURCE-ONLY.json').read_text())
assert sha(SOURCE/'SOURCE-ONLY.json')=='a21d44b2248380e3e182fa49c026236171d08580e15fb8b7ba24bbc995239608'
for name,digest in manifest.items():assert sha(SOURCE/name)==digest,name
roles=json.loads((SOURCE/'ROLES.json').read_text())
assert {r['path'] for r in roles}=={'dom/base/nsDOMWindowUtils.cpp','dom/interfaces/base/nsIDOMWindowUtils.idl','dom/base/test/mochitest.toml','dom/base/test/test_missing_pseudo_animation_composed.html'}
prior=(SOURCE/'prerequisite/dom/base/nsDOMWindowUtils.cpp').read_text()
start=prior.index('NS_IMETHODIMP\nnsDOMWindowUtils::GetMissingPseudoAnimationValuesForTesting(')
end=prior.index('\nNS_IMETHODIMP',start+10)+1
old=prior[start:end]; new=(SOURCE/'driver.cpp').read_text()
expected=''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='accepted-query-driver.cpp',tofile='combined-driver.cpp'))
assert expected==(SOURCE/'QUERY-DRIVER-DELTA.patch').read_text()
assert old in (SOURCE/'candidate/dom/base/nsDOMWindowUtils.cpp').read_text()
assert old[old.index('  struct State {'):old.index('  nsTArray<State> states;')]==new[new.index('  struct State {'):new.index('  nsTArray<State> states;')]
assert old[old.index('  auto sameEffects = [&] {'):old.index('  bool unchanged = sameEffects();')]==new[new.index('  auto sameEffects = [&] {'):new.index('  bool unchanged = sameEffects();')]
assert old[old.index('  for (const State& state : states) {',old.index('  unchanged &= sameEffects();')):old.index('  JSONStringWriteFunc')]==new[new.index('  for (const State& state : states) {',new.index('  unchanged &= sameEffects();')):new.index('  JSONStringWriteFunc')]
assert new.index('RecascadeStyleForMissingPseudo(')>new.index('const bool admitted = compositor->ComposeServoAnimationRulesForMissingPseudo(')
assert new.index('  unchanged &= sameEffects();')>new.index('RecascadeStyleForMissingPseudo(')
inventory=json.loads((SOURCE/'ASSERTIONS.json').read_text());rows=[r for t in inventory['tasks'] for r in t['assertions']]
assert len(rows)==122 and len(inventory['tasks'])==5 and len({r['name'] for r in rows})==122
probes=[r for r in rows if r['classification']=='probe'];assert len(probes)==3
assert all(r['name'].startswith('Probe:') for r in probes)
assert sum(r['classification']=='setup' for r in rows)==33
assert all(not r['name'].startswith('Probe:') for r in rows if r not in probes)
env=dict(os.environ,GIT_OPTIONAL_LOCKS='0',PYTHONDONTWRITEBYTECODE='1')
with tempfile.TemporaryDirectory(prefix='combined-recascade-review-') as directory:
 scratch=Path(directory);copied=scratch/'copied';copied.mkdir()
 for name in manifest:
  target=copied/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(SOURCE/name,target)
 checker=copied/'check.py';text=checker.read_text();assert text.count('ROOT = P.parent.parent')==1
 code=text.replace('ROOT = P.parent.parent','ROOT = Path('+repr(str(ROOT))+')')
 launcher='import sys; sys.argv='+repr([str(checker)])+'; exec(compile('+repr(code)+', '+repr(str(checker))+', "exec"), {"__file__": '+repr(str(checker))+', "__name__": "__main__"})'
 result=subprocess.run([sys.executable,'-B','-c',launcher],cwd=ROOT,env=env,capture_output=True,text=True)
 (HERE/'source-check.log').write_text(result.stdout+result.stderr);assert result.returncode==0,result.stderr
 shutil.copytree(copied/'verification',HERE/'copied-verification')
 tree=scratch/'tree';shutil.copytree(SOURCE/'prerequisite',tree)
 inventory_files=lambda:{p.relative_to(tree).as_posix():sha(p) for p in tree.rglob('*') if p.is_file()}
 before=inventory_files()
 for mode in ['forward','reverse']:
  cmd=['git','apply']+(['--reverse'] if mode=='reverse' else [])+[str(SOURCE/'driver.patch')]
  r=subprocess.run(cmd,cwd=tree,env=env,capture_output=True,text=True);assert r.returncode==0,r.stderr
  (HERE/(mode+'-patch.log')).write_text(r.stdout+r.stderr)
  if mode=='forward':assert inventory_files()=={p.relative_to(SOURCE/'candidate').as_posix():sha(p) for p in (SOURCE/'candidate').rglob('*') if p.is_file()}
  else:assert inventory_files()==before
for name,digest in manifest.items():assert sha(SOURCE/name)==digest,name
report={'status':'PASS','source_manifest':sha(SOURCE/'SOURCE-ONLY.json'),'source_inputs':len(manifest),'diagnostic_only_paths':[r['path'] for r in roles],'production_helpers_unchanged':True,'original_query_driver_unchanged':True,'exact_original_state_membership_final_comparison_preserved':True,'source_checker_root_locator_only_adjusted_in_memory':True,'exact_forward_reverse_inventory':True,'ordinary_checks':119,'setup_subset':33,'interpretation_probes':[r['name'] for r in probes],'scratch_removed':not scratch.exists(),'native_build':False,'browser_execution':False}
(HERE/'AUDIT.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
