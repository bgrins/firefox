import copy, hashlib, importlib.util, json, os, stat, subprocess, sys, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
ENV=dict(os.environ,GIT_OPTIONAL_LOCKS='0')
GIT=['git','--no-optional-locks','-c','core.fsmonitor=false']
def git(*args,env=ENV): return subprocess.check_output(GIT+list(args),cwd=ROOT,env=env)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,v):
 with p.open('x') as f: json.dump(v,f,indent=2,sort_keys=True);f.write('\n')
def load(name,path):
 s=importlib.util.spec_from_file_location(name,ROOT/path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
h=load('preserve','artifacts/css-keyframe-commit-styles-implicit-clean-comparison-v1/compare.py')
a=load('epoch','artifacts/css-keyframe-operation-descriptor-post-signing-proposal-v2/epoch.py')
epoch=json.loads((HERE/'CURRENT-EPOCH.json').read_text());before=a.verify_current(h,ROOT,ENV,epoch)
receipts={n:json.loads((HERE/(n+'-receipt.json')).read_text()) for n in ['compact-borrow-research','compact-borrow-native','steps-research','steps-native']}
assert all(r['signature_verified'] for r in receipts.values())
native=receipts['steps-native']['commit'];research=receipts['steps-research']['commit'];arc=receipts['compact-borrow-native']['commit']
ledger=ROOT/'artifacts/stylo-bloom-tools/CURRENT-COMMITS.json';d=json.loads(ledger.read_text())
assert d['committed_native_fixes']==131 and not any(e.get('fix')==133 for e in d['new_queue'])
item=json.loads((HERE/'native-steps-input.json').read_text())
entry={'fix':133,'status':'COMMITTED_NATIVE_WPT','repair':'calculated-jump-none-minimum','group':'Animations, timelines and transitions','native_commit':native,'research_commit':research,'native_paths':item['files'],'gecko_paths':[n for n in item['files'] if n.startswith('servo/')],'wpt_paths':[n for n in item['files'] if n.startswith('testing/')],'patch_sha256':item['patch_sha256'],'selected_cases':77,'mandatory_candidate_passes':22,'observed_repairs':20,'strict_other_controls':55,'phase_counts':[[52,25],[72,5],[52,25]],'restored_all_outcomes_exact':True,'both_builds_pass':True,'wpt_lint_pass':True,'clean_HEAD_browser_build':False,'signature_verified':True,'candidate_source_installed':True,'installed_browser_binary':'Restored original steps implementation; tested candidate was restored before signing.','formal_attribution':'Source/specification audit and browser reproduction found the bug. Standalone Lean model supports conditional origin-sensitive consumer laws; no native-refinement or integrated coverage claim.','triage':'Tentative P3 conformance; no demonstrated security or performance impact.','related_bug':2037743,'claims_full_related_bug_fixed':False,'raw_index_change_cause_established':False,'semantic_staging_preserved':True,'acceptance':{'path':'artifacts/css-steps-jump-none-acceptance-v1/ACCEPTANCE.json','root_adoption':'artifacts/css-local-signing-20261027-v2/STEPS-INSTALLATION.json'},'comparison_runtime':'artifacts/css-steps-jump-none-continuation-runtime-v1','limits':['Five unrelated controls retain failures.','Unresolved contextual calculations remain rejected.','Comparison ran on the experimental owner branch, not a clean upstream-only browser.']}
d['new_queue'].append(entry);d['committed_native_fixes']=132
d['previous_signing']=d.get('latest_signing');d['latest_signing']={'directory':str(HERE.relative_to(ROOT)),'commits':{n:r['commit'] for n,r in receipts.items()},'all_signatures_verified':True,'new_accepted_bug':133}
d['verified_working_epoch_history'].append(d['latest_verified_working_epoch']);d['latest_verified_working_epoch']={'path':'artifacts/css-local-signing-20261027-v2/CURRENT-EPOCH.json','status':'Locally verified and reanchored after each signed commit','browser_binary':'Restored original steps build; candidate source installed'}
d['signing_next_action']='Accepted fixes committed; retain unfinished prototypes in recovery snapshot and continue independent validation.'
paths=[ledger,ROOT/'artifacts/stylo-bloom-tools/PLAN-OF-RECORD.md',ROOT/'artifacts/stylo-bloom-tools/BUGFIX-COMMITS.md',ROOT/'artifacts/css-fix-readout-20261023/README.md',ROOT/'artifacts/css-fix-readout-20261023/GROUPS.json']
save(HERE/'LEDGER-PREIMAGES.json',{str(f.relative_to(ROOT)):sha(f) for f in paths})
ledger.write_text(json.dumps(d,indent=2)+'\n')
intro=f'Latest signed work: fix 133 `{native[:12]}` repairs calculated jump-none counts, preceded by evidence `{research[:12]}`. The compact Arc borrow API and tests are separate in `{arc[:12]}`. All 132 accepted fixes are committed; repair 120 remains held and excluded. See the [signing record](../css-local-signing-20261027-v2/CHECKPOINT.md).'
for f in paths[1:4]:
 text=f.read_text()
 if f.name=='PLAN-OF-RECORD.md':
  text=text.replace('## Latest verified work\n\n','## Latest verified work\n\n- '+intro+'\n',1)
  lines=text.splitlines()
  for i,line in enumerate(lines):
   if line.startswith('2. **Complete current-provider'):
    lines[i]='2. **Complete current-provider animation resolution.** Compact borrowing now passes five unit tests under each allocation configuration and three compile-fail doctests. The normal/GTest builds and all 17 selected host tests pass. Browser comparison preserves all 166 outcomes (162 PASS, four provider FAIL), two passing crashes and eleven OK harnesses. The pointer-sized API is committed; the owner prototype remains experimental. Review and compile the prepared current-provider resolver next, then connect winning-provider enumeration, cycle policy and publication. [Results](../css-keyframe-owner-browser-terminal-review-v1/REPORT.md).'
   if line.startswith('3. **Validate isolated'):
    lines[i]='3. **Calculated easing ranges: jump-none fixed; cubic-bezier next.** Fix 133 is committed with its WPTs. Original/candidate/restored comparison repaired 20 failures, passed all 22 targets, preserved 55 controls and reproduced all 77 baseline outcomes after restoration. The separate Lean model has 10 audits, 11 examples and three false controls; no native-refinement or integrated coverage claim. The next prepared cubic-bezier experiment has 113 cases and needs independent review, compilation and browser comparison. Contextual integers and held repair 120 stay separate. [Acceptance](../css-steps-jump-none-acceptance-v1/REPORT.md).'
  text='\n'.join(lines)+'\n'
 else:
  old=text.split('\n\n')[1];text=text.replace(old,intro,1)
 text=text.replace('**131 accepted fixes: 131 committed locally, 0 accepted pending, and 1 additional held repair excluded.**','**132 accepted fixes: 132 committed locally, 0 accepted pending, and 1 additional held repair excluded.**',1)
 text=text.replace('| Animations, timelines and transitions | 14 | 0 |','| Animations, timelines and transitions | 15 | 0 |',1).replace('| **Total** | **131** | **0** |','| **Total** | **132** | **0** |',1)
 if f.name=='BUGFIX-COMMITS.md': text=text.replace(intro,intro+f'\n\n| Fix | Native/WPT commit | Preceding evidence |\n|---|---|---|\n| 133: calculated jump-none minimum | `{native}` | `{research}` |\n\nTwenty observed failures repaired; 22 targets pass, 55 controls unchanged, all 77 restored outcomes exact. Tentative P3 conformance. Source/spec audit and browser reproduction found this issue; the separate Lean model supports conditional laws. No full bug 2037743, clean-upstream browser or security claim. Earlier checkpoint text below is historical.',1)
 if f.parent.name=='css-fix-readout-20261023': text=text.replace('| Fix | Gecko/WPT commit | Preceding research |\n|---|---|---|','| Fix | Gecko/WPT commit | Preceding research |\n|---|---|---|'+f'\n| 133: calculated-jump-none-minimum | `{native}` | `{research}` |',1)
 f.write_text(text)
groups=json.loads(paths[4].read_text());groups['head']=native;groups['committed']=132
g=next(g for g in groups['groups'] if g['group']==entry['group']);g['committed']+=1;g['fixes'].append({'fix':133,'repair':entry['repair'],'native_commit':native})
assert sum(g['committed'] for g in groups['groups'])==132
paths[4].write_text(json.dumps(groups,indent=2)+'\n')
report='# Signed local work, 2026-10-27\n\n| Commit | Contents |\n|---|---|\n'+''.join(f"| `{r['commit']}` | {name} |\n" for name,r in receipts.items())+'\nAll four signatures and exact committed trees were verified. Research precedes each native commit. Fix 133 contains only one Rust file and three WPTs; the Arc API includes its unit and compile-fail tests. There are 132 accepted committed browser fixes; held repair 120 is excluded.\n\nThe jump-none comparison repaired 20 failures, passed all 22 targets, preserved 55 controls and exactly reproduced all 77 baseline outcomes after restoration. Tests ran on the experimental owner tree, not a clean upstream-only build. Source/specification audit found the issue; the standalone Lean model proves conditional consumer laws. Raw index drift in the comparison has no established cause; semantic staging was preserved.\n\nThe remaining prototypes are preserved by the accompanying recovery patch. They remain applied for continued development and are not counted as accepted fixes. The installed browser binary still contains the restored original steps implementation; signing installs the tested candidate source but does not rebuild it. Canonical Lean counts remain 11,830 audits, 12,424 examples and 170 expected-false cases. Nothing was pushed or submitted.\n'
(HERE/'CHECKPOINT.md').write_text(report)
current=copy.deepcopy(epoch)
for f in paths:
 n=str(f.relative_to(ROOT));pin=sha(f)
 if n in current['pins']:current['pins'][n]=pin
 if n in current['committed_research_working_payloads']:current['committed_research_working_payloads'][n]=pin
state=h.index_state(ROOT,ENV);current['semantic_index']=h.semantic_index(state);current['raw_index_observation']['current']=state['raw_index'];a.verify_current(h,ROOT,ENV,current)
save(HERE/'LEDGER-EPOCH.json',current);(HERE/'CURRENT-EPOCH.json').write_text(json.dumps(current,indent=2,sort_keys=True)+'\n')
save(HERE/'LEDGER-PATHS.json',[str(f.relative_to(ROOT)) for f in paths])
print('Ledger updated: 132 accepted committed fixes; documents and preservation verified',flush=True)
