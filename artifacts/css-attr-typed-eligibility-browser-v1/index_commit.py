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
receipt=json.loads((root/'artifacts/css-ahom-lf-partition-probe-v1/attr-typed-eligibility-native-v1-receipt.json').read_text())
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
p=ledger/'CURRENT-COMMITS.json';d=json.loads(p.read_text());assert d['committed_native_fixes']==55
entry={'repair':'attr-typed-fallback-eligibility','native_commit':native,'companion_commit':companion,'model_commit':'bd97b69e209cc493200cbbb06bc88c50694c1723','patch':{'path':str((here/'native-wpt-v1.patch').relative_to(root)),'sha256':sha(here/'native-wpt-v1.patch')},'acceptance':{'path':str((here/'ROOT-SCOPED-ACCEPTANCE-v1.json').relative_to(root)),'sha256':sha(here/'ROOT-SCOPED-ACCEPTANCE-v1.json')},'acceptance_scope':'Occurrence-specific syntax parsing selects typed attribute fallback dependencies. Eight failures repaired; 183 checks pass. Generic parser model remains conditional.','native_paths':receipt['files'],'stack_context':'Exact patch follows namespace, invalid-entry and fallback preparation repairs. Shared experimental browser tree; no isolated-base build.'}
d['new_queue'].append(entry);d['committed_native_fixes']=56
p.write_text(json.dumps(d,indent=2)+'\n')
p=ledger/'BUGFIX-COMMITS.md';s=p.read_text().replace('**55 committed fixes;','**56 committed fixes;')
row=f'| attr-typed-fallback-eligibility | `{native}` | `{companion}` |\n'
lines=s.splitlines(True)
last=max(i for i,l in enumerate(lines) if l.startswith('| mathml-token-range-origin |'))
lines.insert(last+1,row);s=''.join(lines)
s+=f'''\n## Typed attribute fallback eligibility committed\n\n`{native}` contains only three Rust files and the twelve-case WPT.\nReview and browser evidence precede it in `{companion}`.\nFive new-case failures and three retained diagnostics become passes; all 183\nchecks pass. Build and lint pass (zero errors, two warnings). The earlier\ngeneric-parser model has fifteen theorem audits; this integration adds no\nnew theorem and does not close native parser, provider or graph admission.\nThe exact isolated patch excludes unrelated experiments; browser pairing used\nthe shared tree. Additional parse cost is unmeasured.\nSee [acceptance](../css-attr-typed-eligibility-browser-v1/ROOT-SCOPED-ACCEPTANCE-v1.json)\nand [commit check](../css-attr-typed-eligibility-browser-v1/ROOT-COMMIT-CHECK-v1.json).\n'''
p.write_text(s)
p=ledger/'PLAN-OF-RECORD.md';s=p.read_text().replace('There are 55 signed standalone','There are 56 signed standalone')
a=s.index('2. Resolve occurrence-specific');b=s.index('3. Continue cascade',a)
s=s[:a]+f'''2. Typed-fallback eligibility is signed as `{native}`.\n   All twelve new cases and 171 other checks pass, repairing eight failures.\n   Follow the graph-admission audit into dependencies hidden in attribute values:\n   relative-unit ordering and non-custom properties with no lexical var().\n   Require normative adjudication and browser reproduction before counting bugs;\n   the unused-fallback unit-dependency oracle remains ambiguous. Preserve native\n   parser/property-context and full graph-composition obligations.\n'''+s[b:]
a=s.index('The next native candidate is occurrence-specific')
s=s[:a]+f'''Typed-fallback eligibility is now signed as `{native}`.\nThe prior fifteen-audit conditional model guided the local parser/graph boundary;\nsource review, paired browser results and build support the native integration.\nFull parser and SCC correctness remain open. FontFace provider integration has\na sealed source-readiness report, but no native build or browser acceptance yet;\nit is the original producer's second pass, not independent implementation review.\n'''
p.write_text(s)
files=[str((ledger/n).relative_to(root)) for n in ['CURRENT-COMMITS.json','BUGFIX-COMMITS.md','PLAN-OF-RECORD.md']]
files += [str((here/n).relative_to(root)) for n in ['ROOT-COMMIT-CHECK-v1.json','companion-recipe-v1.json','native-recipe-v1.json','companion-commit-driver-v1.log','native-commit-driver-v1.log','index_commit.py']]
files += [str(Path('artifacts/css-ahom-lf-partition-probe-v1')/(base+suffix)) for base in ['attr-typed-eligibility-companion-v1','attr-typed-eligibility-native-v1'] for suffix in ['-receipt.json','-message.txt','-commit.log']]
item={'id':'attr-typed-eligibility-ledger-v1','expected_head':native,'files':files,'source_pins':{f:sha(root/f) for f in files},'message':'No bug - Index the typed attribute fallback repair. r?#firefox-style-system-reviewers'}
(here/'ledger-recipe-v1.json').write_text(json.dumps(item,indent=2)+'\n')
print(json.dumps(check,indent=2))
