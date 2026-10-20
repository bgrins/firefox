import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit('require -I -S without optimization')
sys.dont_write_bytecode=True
import hashlib,json
from pathlib import Path
HERE=Path(__file__).resolve().parent
RUN=HERE.parent/'css-cssom-exact-traversal-standalone-postprocess-v4/runtime-capture'
REPO=HERE.parents[1]
SOURCE_NAMES=['layout/generic/nsIFrame.cpp','layout/generic/nsIFrame.h','layout/base/nsLayoutUtils.cpp','layout/base/nsLayoutUtils.h','dom/base/DOMRect.cpp']
def load(path):
 def unique(items):
  result={}
  for k,v in items:
   assert k not in result
   result[k]=v
  return result
 return json.loads(path.read_text(),object_pairs_hook=unique)
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def pairs(rows):
 result={(r['test'],r['subtest']):[r['status'],r.get('expected',r['status'])] for r in rows}
 assert len(result)==len(rows)
 return result
def ends(rows):
 result={r['test']:[r['status'],r.get('expected',r['status'])] for r in rows}
 assert len(result)==len(rows)
 return result

def review():
 state=load(RUN/'STATE.json')
 assert state['status']=='terminal' and state['accepted'] is False
 for n in ['wpt_lint_exit','format_check_exit','candidate_build_exit','restore_build_exit']:assert state[n]==0
 for n in ['source_restored','other_native_unchanged','head_unchanged','index_unchanged','exact_oracle_match']:assert state[n] is True
 for n in ['candidate-build','restore-build','wpt-lint','format-check']:assert load(RUN/(n+'.json'))['exit']==0
 initial=load(RUN/'BEFORE.json'); final=load(RUN/'FINAL.json'); inputs=load(RUN/'INPUTS.json')
 for n in ['head','index_diff_sha256','index_entries_sha256']:assert initial[n]==final[n]==inputs[n]
 assert final['sources']==initial['sources'] and final['fixed_native_pins']==initial['fixed_native_pins']
 assert final['temporary_tests_absent'] is True
 assert load(RUN/'RESTORED.json')=={**final['sources'],**final['fixed_native_pins']}
 assert len(inputs['pins'])==400 and inputs['staged_paths']==229
 for n,h in inputs['pins'].items():
  if n.startswith('artifacts/css-cssom-exact-traversal-standalone-v4/'):
   path=RUN/n.split('artifacts/css-cssom-exact-traversal-standalone-v4/',1)[1]
  elif n.startswith('artifacts/'):
   path=REPO/n
  elif n in SOURCE_NAMES:
   path=RUN/'original'/n
  else:
   path=RUN/'standalone/inputs'/n
  assert sha(path)==h,n
 for n in SOURCE_NAMES:
  assert sha(RUN/'original'/n)==initial['sources'][n]
  assert sha(RUN/'source-before'/n)==initial['sources'][n]
 assert sha(RUN/'candidate/dom/base/DOMRect.cpp')=='7f3d650772a2053cdac784410c68014a2abb2998e1b1cd4f57430585c7b12cc5'
 assert sha(RUN/'original/dom/base/DOMRect.cpp')=='340a676a79f33faa6f6243bd1c5af4c4bba99310142ee0b24a6ecbf2da1bfc9e'
 events=[json.loads(line) for line in (RUN/'standalone/raw.json').read_text().splitlines()]
 rawrows=[e for e in events if e.get('action')=='test_status']; rawends=[e for e in events if e.get('action')=='test_end']
 run=load(RUN/'standalone/RUN.json')
 assert rawrows==run['rows'] and rawends==run['ends']
 assert len(rawrows)==74 and len(rawends)==23
 assert sum(e.get('action')=='suite_end' for e in events)==1
 assert run['complete'] and run['before']==run['after'] and run['exit']==1
 assert load(RUN/'standalone-wpt.json')['exit']==1
 for n,h in run['before'].items():
  if h is None or n.startswith('objdir-full.noindex/'):continue
  assert sha(RUN/'standalone/inputs'/n)==h,n
 for n in SOURCE_NAMES:assert run['before'][n]==sha(RUN/'candidate'/n)
 for n,h in initial['fixed_native_pins'].items():assert run['before'][n]==h,n
 actual=pairs(rawrows); actualends=ends(rawends)
 oracle=load(RUN/'ORACLE.json')
 history=load(HERE.parent/'css-cssom-rectangle-standalone-runtime-v1/integer-only/RUN.json')
 assert actual==pairs(oracle['rows'])==pairs(history['rows'])
 assert actualends==ends(oracle['ends'])==ends(history['ends'])
 assert run['exit']==oracle['exit']==history['exit']
 tests=load(RUN/'TESTS.json')
 assert set(actualends)=={'/'+n.split('testing/web-platform/tests/',1)[1] for n in tests}
 own='/css/cssom-view/getBoundingClientRect-untransformed-edge-precision.html'
 dom='/css/cssom-view/getBoundingClientRect-transformed-edge-precision.html'
 a={k:v for k,v in actual.items() if k[0]==own};b={k:v for k,v in actual.items() if k[0]==dom};c={k:v for k,v in actual.items() if k[0] not in [own,dom]}
 assert len(a)==4 and all(v==['PASS','PASS'] for v in a.values())
 assert len(b)==4 and sum(v==['PASS','PASS'] for v in b.values())==2 and sum(v==['FAIL','PASS'] for v in b.values())==2
 assert len(c)==66 and sum(v==['PASS','PASS'] for v in c.values())==64 and sum(v==['FAIL','FAIL'] for v in c.values())==2
 return {'status':'PASS_STANDALONE_WITHOUT_FIX102_RUNTIME','prepared_input_pins':400,'historical_head':initial['head'],'historical_index_diff_sha256':initial['index_diff_sha256'],'historical_index_entries_sha256':initial['index_entries_sha256'],'raw_rows':74,'raw_ends':23,'own_pass':4,'separate_DOM_unexpected_fail':2,'existing_expected_fail':2,'wpt_exit':1,'restored_sources':final['sources'],'fixed_native_restored':final['fixed_native_pins'],'all_file_outcomes':actualends,'nonpassing':[{'key':list(k),'outcome':v} for k,v in actual.items() if v[0]!='PASS'],'binary_identity':{n:h for n,h in run['before'].items() if n.startswith('objdir-full.noindex/')},'limits':'Contemporaneous binary hashes, not independently rebuilt or archived executables. Current shared tree minus fix102, not isolated upstream.'}

r=review();text=json.dumps(r,indent=2,sort_keys=True)+'\n'
if sys.argv[1:]==['--check']:
 assert (HERE/'INDEPENDENT-RESULT.json').read_text()==text
 print('Independent standalone raw comparison reproduced')
elif not sys.argv[1:]:
 (HERE/'INDEPENDENT-RESULT.json').write_text(text)
 print(json.dumps({'result':r['status'],'rows':74,'ends':23}))
else:raise SystemExit('usage: review_runtime.py [--check]')
