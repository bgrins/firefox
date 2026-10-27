import copy, hashlib, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text())
def ref(p): return {'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def write(p,v): p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')
native=read(HERE/'counter-fix-receipt.json');research=read(HERE/'counter-validation-receipt.json')
assert native['signature_verified'] and research['signature_verified'] and native['parent']==research['commit']
acceptance=ROOT/'artifacts/css-counter-scope-append-acceptance-v1/ACCEPTANCE.json'
a=read(acceptance);assert a['status']=='READY_FOR_STANDALONE_SIGNED_COMMIT'
entry=read(ROOT/'artifacts/css-counter-scope-append-packaging-v1/DRAFT-ENTRY.json')
for k in list(entry):
 if k.startswith('expected_'): del entry[k]
entry.update(status='COMMITTED_NATIVE_WPT',native_commit=native['commit'],research_commit=research['commit'],companion_commit=research['commit'],phase_counts=a['phase_counts'],observed_repairs=a['observed_repairs'],unchanged_landing_controls=a['unchanged_controls'],existing_regressions=a['existing_regressions'],terminal_review=a['terminal_review'],acceptance=ref(acceptance),commit_verification=ref(HERE/'counter-fix-receipt.json'),candidate_source_installed=True,browser_binary_contains_fix=True,signature_verified=True)
p=ROOT/'artifacts/stylo-bloom-tools/CURRENT-COMMITS.json';ledger=read(p)
assert ledger['committed_native_fixes']==134 and all(x.get('fix')!=136 for x in ledger['new_queue'])
ledger['new_queue'].append(entry);ledger['committed_native_fixes']=135
ledger.setdefault('local_signing_history',[]).append(ledger['latest_signing'])
ledger['latest_signing']={'status':'SIGNED_VERIFIED_LOCAL','fix':136,'native_commit':native['commit'],'research_commit':research['commit'],'verification':ref(HERE/'counter-fix-receipt.json')}
ledger.setdefault('research_signing_history',[]).append(ledger['previous_research_signing'])
ledger['previous_research_signing']=ledger['latest_research_signing']
commits=read(HERE/'RESEARCH-PUBLICATION.json')['commits']|{'counter-validation':research['commit']}
ledger['latest_research_signing']={'status':'SIGNED_VERIFIED_LOCAL','commits':commits}
ledger['latest_counter_fix']={'fix':136,'acceptance':ref(acceptance),'commit_verification':ref(HERE/'counter-fix-receipt.json')}
ledger.setdefault('verified_working_epoch_history',[]).append(ledger['latest_verified_working_epoch'])
ledger['signing_next_action']='Compile and validate the typed-attribute demand proposal before integrating actual winning animation providers; keep new fixes standalone and local.'
ledger['latest_verified_working_epoch']={'path':'artifacts/css-local-signing-20261027-v7/CURRENT-EPOCH.json','status':'Final counter candidate and signed sources; full source/binary/nested preservation verified during local signing','browser_binary_contains_fixes':[133,134,135,136]}
for x in ledger['new_queue']:
 if x.get('fix')==135:
  x['limits']=[v.replace('Adjacent counter append hypothesis is unrun and not included in this fix.','Adjacent counter append invalidation is tracked separately as fix 136.') for v in x.get('limits',[])]
write(p,ledger)
p=ROOT/'artifacts/css-fix-readout-20261023/GROUPS.json';groups=read(p)
assert groups['committed']==134 and groups['tracked']==135
for g in groups['groups']:
 for x in g['fixes']:
  if x.get('fix')==135:
   x['limits']=[v.replace('Adjacent counter append hypothesis is unrun and not included in this fix.','Adjacent counter append invalidation is tracked separately as fix 136.') for v in x.get('limits',[])]
 if g['group']=='Text and fonts':
  assert g['committed']==g['total']==14
  g['fixes'].append(copy.deepcopy(entry));g['committed']=15;g['total']=15
assert sum(g['committed'] for g in groups['groups'])==135
groups.update(head=native['commit'],committed=135,accepted=135,tracked=136)
write(p,groups)
summary=f"Fix 136, contained counter append invalidation, is committed as `{native['commit']}` after research `{research['commit']}`. The original/candidate/original/candidate comparison gives 12 PASS + 12 FAIL / 24 PASS / 12 PASS + 12 FAIL / 24 PASS. All 64 quote subtests and eight existing counter regressions remain passing. Three builds and WPT lint pass. Tentative P3 visual correctness. Source audit and browser reproduction found the issue; the separate Lean model corroborates conditional delivery laws (14 audits, 12 examples, five rejected false claims). No clean-upstream build, security, measured performance or universal native-refinement claim. The original outer tool handle was lost; archived child exits and a fresh final-state verification supply the completion evidence."
research_note='The signed animation research now includes owned provider completion, demand-aware endpoint substitution and typed-attribute/context demands with 22 proposed real-resolver calls. Native integration remains unfinished and the new proposal code is not compiled or enabled. The versioned fallback-cycle trace confirms ordinary Stylo already skips unused fallback edges. The canonical Lean coverage counts are unchanged.'
paths=['artifacts/stylo-bloom-tools/PLAN-OF-RECORD.md','artifacts/stylo-bloom-tools/BUGFIX-COMMITS.md','artifacts/css-fix-readout-20261023/README.md']
for name in paths:
 p=ROOT/name;text=p.read_text();title,body=text.split('\n',1)
 text=title+'\n\n'+summary+'\n\n'+research_note+'\n'+body
 replacements={
  'The adjacent counter hypothesis remains unrun and uncounted.':'The adjacent counter append issue is tracked separately as fix 136.',
  '**134 accepted fixes: 134 committed locally, 0 accepted pending, and 1 additional held repair excluded.**':'**135 accepted fixes: 135 committed locally, 0 accepted pending, and 1 additional held repair excluded.**',
  '| Text and fonts | 14 | 0 |':'| Text and fonts | 15 | 0 |',
  '| **Total** | **134** | **0** |':'| **Total** | **135** | **0** |',
  'All 134 accepted fixes remain committed;':'All 135 accepted fixes remain committed;',
 }
 for old,new in replacements.items():
  assert old in text,(name,old)
  text=text.replace(old,new,1)
 text=text.replace('Next: Integrate winning pending animation providers through the real cascade and dependency scheduler; preserve explicit current-base, cycle-policy, dependency-publication and memory-reporting obligations.', 'Next: Compile the typed-attribute demand proposal and execute its 22 real-resolver calls plus existing native tests, then integrate winning pending animation providers through the real cascade and dependency scheduler. Preserve current-base, cycle-policy, dependency-publication and memory-reporting obligations.', 1)
 if name.endswith('PLAN-OF-RECORD.md'):
  text=text.replace('1. Keep quote fix 135 and its research separately reviewable; retain its exact comparison evidence.','1. Keep quote fix 135 and counter fix 136 independently reviewable with their preceding research and exact comparison evidence.',1)
 else:
  marker='| 135: Contained quote append |'
  assert marker in text
  text=text.replace(marker,f"| 136: Contained counter append | `{native['commit']}` | `{research['commit']}` |\n"+marker,1)
 p.write_text(text)
print('Updated five ledgers:135 accepted committed fixes; held120 excluded')
