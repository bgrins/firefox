import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit('Use python3 -I -S')
import argparse
import collections
import hashlib
import json
import re
from pathlib import Path

p=argparse.ArgumentParser()
p.add_argument('--runtime',type=Path,required=True)
p.add_argument('--output',type=Path,required=True)
a=p.parse_args()
if a.output.exists():
    raise SystemExit('Fresh output required')
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def need(ok,why):
    if not ok:
        raise RuntimeError(why)
result={}
for phase,ordinary in [('trace-baseline','baseline'),('trace-oof-only','oof-only')]:
    path=a.runtime/phase
    events=[json.loads(line) for line in (path/'raw.json').read_text().splitlines()]
    raw=[e for e in events if e.get('action')=='process_output' and '[hidden-oof-' in e.get('data','')]
    need(len(raw)==78,'Wrong raw trace count')
    retained=read(path/'TRACE-LINES.json')
    need(len(retained)==len(raw),'Trace projection count mismatch')
    for line,e in zip(retained,raw):
        need(f"pid:{e['process']} "+e['data'] in line,'Raw/retained trace mismatch')
    triples=[]
    for index in range(0,len(raw),3):
        before,returned,commit=raw[index:index+3]
        mb=re.fullmatch(r'\[hidden-oof-before\] frame=(0x[0-9a-f]+) dirty=([01]) size=(-?\d+),(-?\d+) next=([01])',before['data'])
        mr=re.fullmatch(r'\[hidden-oof-return\] frame=(0x[0-9a-f]+) dirty=([01]) output=(-?\d+),(-?\d+)',returned['data'])
        mc=re.fullmatch(r'\[hidden-oof-commit\] frame=(0x[0-9a-f]+) dirty=([01]) rect=(-?\d+),(-?\d+),(-?\d+),(-?\d+)',commit['data'])
        need(mb and mr and mc,'Wrong trace stage order/shape')
        need(before['process']==returned['process']==commit['process'] and mb[1]==mr[1]==mc[1],'Nonmatching process/frame triple')
        record={'process':before['process'],'frame':mb[1],'dirty':[int(mb[2]),int(mr[2]),int(mc[2])],'before_size':[int(mb[3]),int(mb[4])],'next_continuation':int(mb[5]),'returned_size':[int(mr[3]),int(mr[4])],'committed_rect':[int(mc[k]) for k in range(3,7)]}
        need(record['next_continuation']==0 and record['returned_size']==[0,0] and record['committed_rect'][2:]==[0,0],'Unexpected geometry/continuation trace')
        triples.append(record)
    patterns=collections.Counter(tuple(t['dirty']) for t in triples)
    need(patterns==({(1,1,1):22,(0,0,0):4} if ordinary=='baseline' else {(1,1,1):22,(0,1,1):4}),'Wrong dirty transition counts')
    run=read(path/'RUN.json')
    original=read(a.runtime/ordinary/'RUN.json')
    source={(r['test'],r['subtest']):r for r in original['rows']}
    need(all((source[r['test'],r['subtest']]['status'],source[r['test'],r['subtest']].get('message'))==(r['status'],r.get('message')) for r in run['rows']),'Instrumented outcome drift')
    result[phase]={'raw_sha256':sha(path/'raw.json'),'RUN_sha256':sha(path/'RUN.json'),'TRACE_LINES_sha256':sha(path/'TRACE-LINES.json'),'counts':[{'dirty':list(k),'count':v} for k,v in patterns.items()],'triples':triples,'WPT_status_message_pairs_match_uninstrumented':True,'scope':'Adjacent raw process-output PID/frame triples only; no across-lifetime pointer identity or forced-query gate trace.'}
a.output.write_text(json.dumps(result,indent=2)+'\n')
print('PASS: 26 raw triples per phase; 22 dirty-preserved plus four clean-overwrite/dirty-retention; unchanged WPT outcomes')
