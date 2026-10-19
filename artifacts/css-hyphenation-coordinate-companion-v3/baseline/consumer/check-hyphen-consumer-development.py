import itertools,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parent;OUT=ROOT/'development-build/full'
def encode(c):
 return ' '.join(map(str,[c['id'],c['encoding'],c['compression'],c['option'],c['wrap'],c['svg'],c['combined'],c['line'],c['original_start'],c['original_length'],c['start'],c['length'],10000,len(c['units'])]+c['units']+[c['mask']]))
def execute(cases,name):
 data='\n'.join(map(encode,cases))+'\n';(OUT/(name+'-input.txt')).write_text(data)
 r=subprocess.run([str(OUT/'hyphen-consumer')],input=data,capture_output=True,text=True,timeout=180);(OUT/(name+'-output.txt')).write_text(r.stdout);(OUT/(name+'-stderr.txt')).write_text(r.stderr);assert r.returncode==0,(r.returncode,r.stderr)
 lines=r.stdout.splitlines();assert len(lines)==len(cases)
 result=[]
 for c,line in zip(cases,lines):
  words=line.split(' ');assert words[0]==c['id'];result.append({'length':int(words[1]),'units':[int(x)for x in words[2].split(',')if x],'map':[int(x)for x in words[3].split(',')if x],'hyphens':[int(x)for x in words[4]],'measurement':words[5:]})
 return result
texts=['ab','a\u00adb','\u00adab','a\u00ad\u00adb','a\u00ad b','a\u00ad\u200bb','a-\u00adb','a-b','a\u058ab','a\u2010b','a\u2012b','a\u2013b','a\u2014b','a b','a  b','a\tb','a\nb','a\n \u00adb','á\u00adé','a\U00010428b','a\u0301\u00adb','a\u202ab','\u00ad','  ','a\r\nb']
seeds=[]
for text in texts:
 units=list(int.from_bytes(text.encode('utf-16-le')[i:i+2],'little')for i in range(0,len(text.encode('utf-16-le')),2))
 for encoding,compression in itertools.product([8,16],range(4)):
  if encoding==8 and any(c>255 for c in units):continue
  seeds.append({'id':str(len(seeds)),'encoding':encoding,'compression':compression,'option':2,'wrap':1,'svg':0,'combined':0,'line':0,'original_start':0,'original_length':len(units),'start':0,'length':0,'mask':'-','units':units})
transforms=execute(seeds,'hyphen-consumer-transform')
cases=[];oracles=[]
for seed,t in zip(seeds,transforms):
 n=t['length']
 if not n:continue
 ranges={(0,n),(0,1),(n-1,1)}
 if n>1:ranges.add((1,n-1))
 for (start,length),option,wrapmode,line,maskmode in itertools.product(sorted(ranges),range(3),range(4),range(2),range(3)):
  c=dict(seed);c.update(id=str(len(cases)),start=start,length=length,option=option,wrap=int(wrapmode!=1),svg=int(wrapmode==2),combined=int(wrapmode==3),line=line,mask=('0'*n if maskmode==0 else '2'*n if maskmode==1 else ''.join(str(i%4)for i in range(n))))
  expected=[]
  for pos in range(start,start+length):
   original=t['map'][pos];ch=c['units'][original]
   soft=original>0 and c['units'][original-1]==0xad and not(line and pos==0)
   result=2 if soft else 0
   if option==2:
    explicit=pos>start and c['units'][t['map'][pos-1]] in [45,0x58a,0x2010,0x2012,0x2013]
    if explicit:result=1
    elif result==0 and ch not in [45,0x58a,0x2010,0x2012,0x2013] and c['mask'][pos]=='2':result=4
   if option==0 or wrapmode:result=0
   expected.append(result)
  cases.append(c);oracles.append(expected)
observed=execute(cases,'hyphen-consumer-matrix');differences=[]
for c,o,e in zip(cases,observed,oracles):
 if o['hyphens']!=e:differences.append({'case':c,'observed':o,'expected':e})
(OUT/'HYPHEN-CONSUMER-RESULTS.json').write_text(json.dumps({'cases':len(cases),'transform_seeds':len(seeds),'differences':differences,'oracle':'Independent per-kept-source-position classification with actual transform/skip mapping supplied as an explicit provider. All synthetic glyph masks are arbitrary test inputs; dictionary/scanner reachability is separate. Measurement execution uses generous widths and explicit unit metrics, not real shaping. Explicit previous hyphen is considered only inside the queried native range; unrestricted provider partition invariance is not asserted.'},indent=2)+'\n')
print('hyphen consumer',len(cases),'differences',len(differences));assert not differences
