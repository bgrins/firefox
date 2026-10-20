import hashlib,json
from collections import Counter
from pathlib import Path
HERE=Path(__file__).resolve().parent

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
state=json.loads((HERE/'STATE.json').read_text())
assert state['status']=='terminal' and state['candidate_build_exit']==state['restore_build_exit']==0
assert all(state[k] for k in ['source_restored','head_unchanged','index_unchanged'])
b=json.loads((HERE/'baseline/RUN.json').read_text());c=json.loads((HERE/'candidate/RUN.json').read_text())
for d in [b,c]:
 assert d['complete'] and d['before']==d['after']
 for n,h in d['before'].items():
  if h is not None and not n.startswith('objdir-full.noindex/'):
   kind='baseline' if d is b else 'candidate'
   assert sha(HERE/kind/'inputs'/n)==h,n
allowed={'layout/generic/nsContainerFrame.cpp','objdir-full.noindex/dist/Nightly.app/Contents/MacOS/firefox','objdir-full.noindex/dist/Nightly.app/Contents/MacOS/XUL'}
assert b['before'].keys()==c['before'].keys()
assert all(b['before'][n]==c['before'][n] for n in b['before'] if n not in allowed)
key=lambda r:(r['test'],r['subtest'])
brows={key(r):r for r in b['rows']};crows={key(r):r for r in c['rows']}
assert brows.keys()==crows.keys() and len(brows)==283
new=lambda r:r['test'].endswith('/relative-position-overflow-continuations-rtl.html')
changes=Counter((r['status'],crows[k]['status']) for k,r in brows.items() if new(r))
assert changes=={('PASS','PASS'):220,('FAIL','PASS'):60},changes
assert all(r['status']==crows[k]['status']=='PASS' for k,r in brows.items() if not new(r))
ends=lambda d:{r['test']:r['status'] for r in d['ends']}
assert ends(b)==ends(c) and len(b['ends'])==62
assert c['exit']==0 and b['exit']==1
assert sha(HERE/'before.cpp')==json.loads((HERE/'PATCH.json').read_text())['native_base_sha256']
assert sha(HERE/'candidate.cpp')==json.loads((HERE/'PATCH.json').read_text())['native_candidate_sha256']
print(json.dumps({'paired_new_subtests':280,'corrected':60,'preserved':220,'other_subtests_preserved':3,'existing_file_outcomes':dict(Counter(r['status'] for r in b['ends'] if not new(r))),'source_restored':True,'builds_passed':True},indent=2))
