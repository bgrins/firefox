import concurrent.futures, datetime, hashlib, json, pathlib, urllib.request
from html.parser import HTMLParser
class Anchors(HTMLParser):
 def __init__(self): super().__init__(); self.ids=set()
 def handle_starttag(self,tag,attrs): self.ids.update(v for k,v in attrs if k=="id")
root=pathlib.Path(__file__).resolve().parent
sources={
 'sizing':'https://drafts.csswg.org/css-sizing-3/#cyclic-percentage-contribution',
 'scroll':'https://drafts.csswg.org/scroll-animations-1/#event-loop',
 'numeric':'https://drafts.csswg.org/css-values-4/#numeric-types',
 'cssom':'https://drafts.csswg.org/cssom/#resolved-values',
 'html':'https://html.spec.whatwg.org/multipage/webappapis.html#update-the-rendering',
 'svg':'https://www.w3.org/TR/SVG2/render.html#RenderingTree'}
def fetch(item):
 name,url=item
 with urllib.request.urlopen(url,timeout=60) as r:
  body=r.read(); status=r.status; final=r.url
 anchor=url.split('#')[1]
 parser=Anchors(); parser.feed(body.decode("utf-8")); assert anchor in parser.ids, (name,anchor)
 path=root/'spec'/f'{name}.html';path.write_bytes(body)
 return dict(name=name,url=url,final_url=final,status=status,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),sha256=hashlib.sha256(body).hexdigest(),anchor_verified=anchor)
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
 rows=list(pool.map(fetch,sources.items()))
(root/'spec'/'FETCH.json').write_text(json.dumps(rows,indent=2)+'\n')
print(json.dumps(rows,indent=2))
