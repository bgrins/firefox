from pathlib import Path
from urllib.request import urlopen,Request
from concurrent.futures import ThreadPoolExecutor
import datetime,json,hashlib
root=Path(__file__).resolve().parent
names=['css-sizing-3','scroll-animations-1','css-text-3','css-break-3','css-transforms-1','css-font-loading-3','css-conditional-5','css-values-4']
def fetch(name):
 url='https://drafts.csswg.org/'+name+'/'
 with urlopen(Request(url,headers={'User-Agent':'CSS-semantics-research'}),timeout=40) as r:
  data=r.read(); status=r.status;final=r.url
 (root/'spec'/(name+'.html')).write_bytes(data)
 return {'file':name+'.html','url':url,'final_url':final,'status':status,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'sha256':hashlib.sha256(data).hexdigest()}
with ThreadPoolExecutor(max_workers=4) as ex: rows=list(ex.map(fetch,names))
(root/'spec/FETCH.json').write_text(json.dumps(rows,indent=2)+'\n')
print(json.dumps(rows))
