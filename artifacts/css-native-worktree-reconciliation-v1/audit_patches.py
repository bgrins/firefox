import json, hashlib, re, difflib
from pathlib import Path
ROOT=Path(__file__).resolve().parent
REPO=ROOT/'inputs'
patches=[
'css-view-transition-types-fix-v1/fix-candidate-v1.patch',
'css-quote-scope-append-fix-v1/fix-candidate-v1.patch',
'css-shape-margin-basis-fix-v1/fix-candidate-v1.patch',
'css-flex-collapsed-alignment-fix-v1/fix-candidate-v1.patch',
'css-sticky-writing-mode-fix-v1/fix-candidate-v1.patch',
'css-sticky-auto-inset-fix-v1/fix-candidate-v1.patch',
'css-nowrap-partitions-fix-v1/fix-candidate-v1.patch',
'css-hyphenation-ownership-fix-v1/fix-candidate-v4.patch',
'css-line-break-language-fix-v1/fix-candidate-v2.patch',
'css-layer-cutoff-composition-probe-v1/fix-c-after-a-b-d-v1.patch',
'css-layer-cutoff-composition-probe-v1/fix-a-b-d-v1.patch',
'css-shadow-context-order-fix-v1/fix-candidate-v1.patch',
'css-page-selector-name-fix-v1/fix-candidate-v1.patch',
'css-variable-backslash-newline-root-v1/native.patch',
]
texts={r['path']:(ROOT/'source/worktree'/r['path']).read_text() for r in json.loads((ROOT/'SOURCE-PINS.json').read_text())}
results=[]
for patch in patches:
 data=(REPO/'artifacts'/patch).read_bytes(); lines=data.decode().splitlines(keepends=True)
 row={'patch':'artifacts/'+patch,'sha256':hashlib.sha256(data).hexdigest(),'hunks':[]}; path=None;i=0
 while i<len(lines):
  l=lines[i]
  if l.startswith('+++ '):path=l[4:].strip().split('\t')[0];path=path[2:] if path.startswith('b/') else path
  if not l.startswith('@@ '):i+=1;continue
  header=l.strip();i+=1;old=[];new=[]
  while i<len(lines) and lines[i][:1] in [' ','+','-'] and not lines[i].startswith(('--- ','+++ ')):
   v=lines[i]
   if v[0] in ' -':old.append(v[1:])
   if v[0] in ' +':new.append(v[1:])
   i+=1
  if path not in texts:continue
  a=''.join(old);b=''.join(new);n=texts[path].count(b)
  h={'path':path,'hunk':header,'exact_candidate_context_occurrences':n}
  if n==1:texts[path]=texts[path].replace(b,a,1);h['reverse']='exact'
  else:h['reverse']='not_matched'
  row['hunks'].append(h)
 results.append(row)
residual=[]
for path,txt in texts.items():
 original=(ROOT/'source/head'/path).read_text()
 if txt!=original:
  out=ROOT/'residual'/path;out.parent.mkdir(parents=True,exist_ok=True)
  out.write_text(''.join(difflib.unified_diff(original.splitlines(True),txt.splitlines(True),fromfile='HEAD/'+path,tofile='after-recorded-reversals/'+path)))
  residual.append(path)
(ROOT/'PATCH-CORRESPONDENCE.json').write_text(json.dumps({'reversals':results,'residual_paths':residual},indent=2)+'\n')
print(json.dumps({'hunks':sum(len(r['hunks']) for r in results),'unmatched':[(r['patch'],h) for r in results for h in r['hunks'] if h['reverse']!='exact'],'residual':residual},indent=2))
