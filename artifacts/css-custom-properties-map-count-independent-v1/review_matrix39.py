from pathlib import Path
import json,collections
r=Path(__file__).resolve().parent;d=r/'matrix39'
summary={};identity=None;stable=None
builds={x['variant']:x for x in json.loads((d/'BUILD-MATRIX.json').read_text())['runs']}
builds['iterator-only']=next(x for x in json.loads((d/'ITERATOR-PAIR.json').read_text())['runs'] if x['variant']=='candidate')
sources=json.loads((d/'SOURCE-PINS.json').read_text())
for v in ['original','iterator-only','count-only','combined']:
 rows=[json.loads(l) for l in (d/(v+'-raw.json')).read_text().splitlines()]
 sub=[x for x in rows if x['action']=='test_status'];ends=[x for x in rows if x['action']=='test_end'];keys={(x['test'],x['subtest']) for x in sub}
 assert len(sub)==len(keys)==39 and len(ends)==7 and len({x['test'] for x in ends})==7 and all(x['status']=='OK' for x in ends)
 assert sum(x['action']=='suite_end' for x in rows)==1
 end=next(i for i,x in enumerate(rows) if x['action']=='suite_end')
 assert all(i<end for i,x in enumerate(rows) if x['action'] in ['test_status','test_end'])
 assert keys==identity if identity else True
 identity=keys
 run=json.loads((d/(v+'-RUN.json')).read_text());assert run['stable_after'];b=builds[v];assert b['build_exit']==0
 for name in ['firefox','XUL']:
  path='objdir-full.noindex/dist/Nightly.app/Contents/MacOS/'+name
  assert run['pins'][path]==b['binaries'].get(path,b['binaries'].get(name))
 native='servo/components/style/custom_properties_map.rs'
 if native in run['pins']:assert run['pins'][native]==sources[v]
 else:assert v=='original' and b['source']==sources[v]
 other={n:h for n,h in run['pins'].items() if n!=native and not n.startswith('objdir-full.noindex/')}
 assert other==stable if stable else True
 stable=other
 summary[v]={'statuses':dict(collections.Counter(x['status'] for x in sub)),'harnesses':7,'raw_failures':[{'test':x['test'],'subtest':x['subtest'],'message':x.get('message')} for x in sub if x['status']=='FAIL'],'explicit_source_pin':native in run['pins']}
print(json.dumps({'runs':summary,'same_subtest_roster':True,'same_nonvariant_pins':True,'limits':'original runner omitted explicit clean native file before/after pin; build driver pins source before WPT; final expanded pair required'},indent=2))
