import json
from pathlib import Path
MIN32=-(1<<31);MAX32=(1<<31)-1;Q=(1<<30)-1
cases=[('doc_group',0,[-2000000000,1400000000,1400000000]),('rect_origin',-2000000000,[1500000000,1000000000])]
rows=[]
for name,origin,positions in cases:
    x=origin;prefix=[]
    for p in positions:x+=p;prefix.append(x)
    assert all(MIN32<=p<=MAX32 for p in prefix) and -Q<=x and x+1<=Q
    translation=sum(positions);doc=sum(positions[1:])
    rows.append({'name':name,'rect_origin':origin,'width':1,'positions':positions,'v1_prefixes':prefix,'v1_admitted':True,'translation':translation,'translation_fits_nsPoint':MIN32<=translation<=MAX32,'legacy_doc_group':doc,'doc_group_fits_signed32':MIN32<=doc<=MAX32})
assert not rows[0]['doc_group_fits_signed32']
assert not rows[1]['translation_fits_nsPoint']
text=json.dumps({'status':'PASS','cases':rows,'browser_reachability':'not established'},indent=2)+'\n'
Path(__file__).with_name('DOMAIN-CHALLENGES.json').write_text(text)
print(text)
