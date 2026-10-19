import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

root=Path(__file__).resolve().parents[2]
here=Path(__file__).resolve().parent
ledger=root/'artifacts/stylo-bloom-tools'
git=['git','-c','core.fsmonitor=false']
def get(*args,**kwargs):
    return subprocess.check_output(git+list(args),cwd=root,**kwargs)
def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()
receipt=json.loads((root/'artifacts/css-ahom-lf-partition-probe-v1/attr-noncustom-native-v1-receipt.json').read_text())
native,companion=receipt['after'],receipt['before']
assert get('rev-parse','HEAD').decode().strip()==native
assert b'gpgsig ' in get('cat-file','commit',native)
assert b'gpgsig ' in get('cat-file','commit',companion)
assert sorted(get('diff-tree','--no-commit-id','--name-only','-r',native).decode().splitlines())==sorted(receipt['files'])
assert not get('diff','--cached','--name-only').strip()
with tempfile.TemporaryDirectory(prefix='attr-typed-commit-check-') as tmp:
    env=dict(os.environ,GIT_INDEX_FILE=str(Path(tmp)/'index'))
    get('read-tree',companion,env=env)
    get('apply','--cached',str(here/'native-wpt-v1.patch'),env=env)
    assert get('write-tree',env=env).strip()==get('rev-parse',native+'^{tree}').strip()
    get('apply','--cached','--reverse',str(here/'native-wpt-v1.patch'),env=env)
    assert get('write-tree',env=env).strip()==get('rev-parse',companion+'^{tree}').strip()
check={'status':'PASS','native_commit':native,'companion_commit':companion,'signatures_present':True,'exact_patch_tree':True,'reverse_restores_parent':True,'index_empty':True,'native_paths':receipt['files']}
(here/'ROOT-COMMIT-CHECK-v1.json').write_text(json.dumps(check,indent=2)+'\n')
p=ledger/'CURRENT-COMMITS.json';d=json.loads(p.read_text());assert d['committed_native_fixes']==56
entry={'repair':'attr-noncustom-dependency-collection','native_commit':native,'companion_commit':companion,'patch':{'path':str((here/'native-wpt-v1.patch').relative_to(root)),'sha256':sha(here/'native-wpt-v1.patch')},'acceptance':{'path':str((here/'ROOT-SCOPED-ACCEPTANCE-v1.json').relative_to(root)),'sha256':sha(here/'ROOT-SCOPED-ACCEPTANCE-v1.json')},'acceptance_scope':'Retain attr-only non-custom declarations for runtime dependency traversal. Ten new and 183 prior checks pass; four failures repaired, three distinct metadata-loss failures unchanged.','native_paths':receipt['files'],'stack_context':'Exact patch follows preceding attribute repairs. Shared experimental browser tree; no isolated-base build.'}
d['new_queue'].append(entry);d['committed_native_fixes']=57
p.write_text(json.dumps(d,indent=2)+'\n')
p=ledger/'BUGFIX-COMMITS.md';s=p.read_text().replace('**56 committed fixes;','**57 committed fixes;')
lines=s.splitlines(True);last=max(i for i,l in enumerate(lines) if l.startswith('| attr-typed-fallback-eligibility |'))
lines.insert(last+1,f'| attr-noncustom-dependency-collection | `{native}` | `{companion}` |\n');s=''.join(lines)
s+=f'''\n## Attribute-only non-custom dependencies committed\n\n`{native}` deletes the lexical-VAR early return in\n`Cascade::maybe_note_non_custom_dependency` and adds a ten-case WPT.\nReview/browser companion: `{companion}`.\nThe ten new and 183 prior checks pass. Four baseline failures improve across\nthe scoped WPT and diagnostic; three resolved-unit metadata failures remain.\nBuild passes; warning-enabled lint has zero errors and one ignored-WPT warning.\nIndependent syntax and source/oracle review pass. No new native graph theorem\nis claimed; discovery came from manual analysis of formal admission gaps.\nSee [acceptance](../css-attr-noncustom-browser-v1/ROOT-SCOPED-ACCEPTANCE-v1.json)\nand [commit check](../css-attr-noncustom-browser-v1/ROOT-COMMIT-CHECK-v1.json).\n'''
p.write_text(s)
p=ledger/'PLAN-OF-RECORD.md';s=p.read_text().replace('There are 56 signed standalone','There are 57 signed standalone')
s=s.replace('   Follow the graph-admission audit into dependencies hidden in attribute values:\n   relative-unit ordering and non-custom properties with no lexical var().\n   Require normative adjudication and browser reproduction before counting bugs;\n   the unused-fallback unit-dependency oracle remains ambiguous. Preserve native\n   parser/property-context and full graph-composition obligations.',f'''   The follow-up attr-only collection repair is signed as `{native}`.\n   Its ten new cases and 183 prior checks pass. Preserve native parser/context\n   and full graph-composition obligations.''')
s=s.replace('3. Continue cascade','4. Continue cascade').replace('4. Integrate the prepared','5. Integrate the prepared').replace('5. Keep every accepted','6. Keep every accepted')
pos=s.index('4. Continue cascade')
s=s[:pos]+'''3. Repair resolved relative-unit summaries at the attribute and universal-value\n   persistence sinks. Three browser failures are retained: attribute cycle,\n   universal-chain cycle and acyclic 1em ordering (23px instead of 17px).\n   Use successful output tokens, preserve bytes/taint and avoid unused-fallback\n   contamination. Selected-output Lean composition is underway; tokenizer and\n   separator admission, bounded-stack scanning and unresolved env payloads\n   need explicit treatment. The unused-relative-fallback oracle is ambiguous.\n'''+s[pos:]
s+=f'''\n## Attribute graph admission checkpoint\n\n`{native}` repairs attr-only collection with one three-line deletion.\nAcross 217 paired result rows, four failures improve and 213 outcomes are\nunchanged. The separate metadata-loss diagnostic remains at three failures.\nThe generic typed-eligibility model did not automatically discover these bugs:\nmanual admission analysis identified the missing collection and summary paths,\nthen browser probes confirmed the predictions. Full SCC correctness remains open.\nFontFace now has an independent sealed source review; expanded window/worker\nWPT preparation is underway before fresh baseline, integration and platform gates.\n'''
p.write_text(s)
files=[str((ledger/n).relative_to(root)) for n in ['CURRENT-COMMITS.json','BUGFIX-COMMITS.md','PLAN-OF-RECORD.md']]
files += [str((here/n).relative_to(root)) for n in ['ROOT-COMMIT-CHECK-v1.json','companion-recipe-v1.json','native-recipe-v1.json','companion-commit-driver-v1.log','native-commit-driver-v1.log','index_commit.py']]
files += [str(Path('artifacts/css-ahom-lf-partition-probe-v1')/(base+suffix)) for base in ['attr-noncustom-companion-v1','attr-noncustom-native-v1'] for suffix in ['-receipt.json','-message.txt','-commit.log']]
item={'id':'attr-noncustom-ledger-v1','expected_head':native,'files':files,'source_pins':{f:sha(root/f) for f in files},'message':'No bug - Index the attribute-only dependency repair. r?#firefox-style-system-reviewers'}
(here/'ledger-recipe-v1.json').write_text(json.dumps(item,indent=2)+'\n')
print(json.dumps(check,indent=2))
