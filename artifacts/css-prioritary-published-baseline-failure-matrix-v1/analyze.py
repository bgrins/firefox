import hashlib
import importlib.util
import json
from pathlib import Path
import sys

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
read=lambda path:json.loads(path.read_bytes())
sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
refs=read(HERE/'REFERENCES.json')
for name,pin in refs.items():assert sha(ROOT/name)==pin['sha256']
fresh=ROOT/'artifacts/css-prioritary-published-original-runtime-1'
historical=ROOT/'artifacts/css-prioritary-selection-candidate-runtime-3'
terminal=read(fresh/'ROOT-OWNER-TERMINAL.json');result=read(fresh/'RESULT.json')
assert (terminal['session'],terminal['launch_chunk'],terminal['terminal_chunk'],terminal['exit'])==(71815,'803a1c','93a058',0)
assert terminal['result_sha256']==sha(fresh/'RESULT.json') and result['success']
assert sha(historical/'FILES.json')=='8114266e01c203cda26f1a9bfd8d0ad144326adb647a0af59779fb81c6018460'
old_manifest=read(historical/'FILES.json')
for lane in ['ordinary','forced_colors']:
 for name in ['raw.jsonl','ASSESSMENT-POLICY.json']:
  relative='candidate-wpt-'+lane+'/'+name
  assert sha(historical/relative)==old_manifest[relative]['sha256']
assert not any(name.startswith('candidate-wpt-mozilla_appearance/') for name in old_manifest)
targets={(page,name) for page,names in read(ROOT/'artifacts/css-prioritary-selection-candidate-v3/TARGETS.json').items() for name in names}
assert len(targets)==24
helper=ROOT/'artifacts/css-minmax-relative-infinity-broader-browser-v5/assess.py'
spec=importlib.util.spec_from_file_location('signatures',helper);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
def events(path):return [json.loads(line) for line in path.read_text().splitlines()]
def signatures(rows):return sorted([module.signature(row) for row in rows if row.get('action') in ('test_status','test_end')],key=lambda row:(row['test'],row['subtest'] or '',row['kind']))
def counts(rows):return {status:sum(row['status']==status for row in rows) for status in ['PASS','FAIL']}
old_forced=events(ROOT/'artifacts/css-prioritary-selection-original-runtime-2/original-wpt-forced_colors/raw.jsonl')
new_forced=events(fresh/'original-wpt-forced_colors/raw.jsonl')
assert signatures(old_forced)==signatures(new_forced)
forced_proof=read(ROOT/'artifacts/css-prioritary-published-forced-baseline-comparison-v1.json')
assert sha(ROOT/'artifacts/css-prioritary-published-forced-baseline-comparison-v1.json')=='cc5e84e2146a174e1d55b07b6e119e30de5b3bacbd7704348b08b39dcceb2e1f'
assert signatures(new_forced)==forced_proof['signatures'] and len(forced_proof['signatures'])==5
matrix=[];all_rows=[];all_ends=[];lanes={};historical_counts={}
for lane in ['ordinary','forced_colors','mozilla_appearance']:
 rows=events(fresh/('original-wpt-'+lane)/'raw.jsonl')
 callbacks=[r for r in rows if r.get('action')=='test_status'];endings=[r for r in rows if r.get('action')=='test_end']
 all_rows.extend(callbacks);all_ends.extend(endings);lanes[lane]=counts(callbacks)
 previous={}
 if lane!='mozilla_appearance':
  oldrows=events(historical/('candidate-wpt-'+lane)/'raw.jsonl')
  previous={(r['test'],r['subtest']):r for r in oldrows if r.get('action')=='test_status'}
  historical_counts[lane]=counts(list(previous.values()))
  oldpolicy=read(historical/('candidate-wpt-'+lane)/'ASSESSMENT-POLICY.json')
  newpolicy=read(fresh/('original-wpt-'+lane)/'ASSESSMENT-POLICY.json')
  assert oldpolicy['expected_subtests']==newpolicy['expected_subtests']
  assert oldpolicy['resources']==newpolicy['resources']
 for row in callbacks:
  if row['status']!='FAIL':continue
  key=(row['test'],row['subtest']);diagnostic=None
  message=row.get('message','')
  if '{' in message:diagnostic=json.JSONDecoder().raw_decode(message[message.index('{'):])[0]
  if 'forced-colors-mode-51' in row['test']:group='known_scheme_serialization_control'
  elif lane=='forced_colors':group='forced_adjustment_selection'
  elif lane=='mozilla_appearance':group='appearance_eligibility_selection'
  elif 'registered-overridden' in row['test']:group='overridden_priority_selection'
  else:group='variable_and_rollback_selection'
  matrix.append({'lane':lane,'test':row['test'],'subtest':row['subtest'],'group':group,
                 'selected_declaration_target':key in targets,'fresh_signature':module.signature(row),
                 'historical_v4_status':previous[key]['status'] if key in previous else None,
                 'historical_v4_observed':key in previous,'diagnostic':diagnostic})
assert len(all_rows)==77 and len(all_ends)==12 and len(matrix)==13
assert len({(r['test'],r['subtest']) for r in all_rows})==77
assert sum(row['selected_declaration_target'] for row in matrix)==12
assert all(r['historical_v4_status']=='PASS' for r in matrix if r['selected_declaration_target'] and r['historical_v4_observed'])
assert counts(all_rows)=={'PASS':64,'FAIL':13}
outcomes=read(fresh/'OUTCOMES.json');assert outcomes['rows']==all_rows and outcomes['endings']==all_ends
for name,pin in refs.items():assert sha(ROOT/name)==pin['sha256']
output={'fresh_counts':counts(all_rows),'fresh_lanes':lanes,'fresh_endings':len(all_ends),'target_pass':sum(r['status']=='PASS' for r in all_rows if (r['test'],r['subtest']) in targets),'target_fail':12,
        'historical_v4_completed_lanes':historical_counts,'historical_v4_appearance':'not executed',
        'old_original_forced':counts([r for r in old_forced if r.get('action')=='test_status']),
        'five_forced_signatures_unchanged':True,'failures':matrix,
        'independent_restoration_claimed':False,'native_candidate_acceptance':False,'new_bug_count':0}
with (HERE/'MATRIX.json').open('x') as stream:json.dump(output,stream,indent=2);stream.write('\n')
print(json.dumps({k:v for k,v in output.items() if k!='failures'}))
