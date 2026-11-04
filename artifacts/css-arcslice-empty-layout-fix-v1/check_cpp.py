from pathlib import Path
import json,subprocess,hashlib
P=Path(__file__).resolve().parent;ROOT=P.parents[1];F=ROOT/'artifacts/css-servo-arc-dst-generated-ffi-v1';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
old=json.loads((F/'api-RESULT.json').read_text());types=[x for x in json.loads((F/'CPP-TYPES.json').read_text())['types'] if x!='StyleDashedIdent']+['StyleSimpleShadow'];rows=[]
for variant,name,parentoverlay in [('current','StyleHeaderSlice','base-overlay.json'),('dst','StyleHeaderSliceStorage','overlay.json')]:
 overlay=json.loads((F/parentoverlay).read_text());helper=P/'cpp'/variant/'candidate/layout/style/ServoStyleConstsInlines.h'
 for item in overlay['roots']:
  if item['name'].endswith('/ServoStyleConstsInlines.h'):item['external-contents']=str(helper)
 overlaypath=P/(variant+'-overlay.json');overlaypath.write_text(json.dumps(overlay,indent=2)+'\n')
 source='#include "mozilla/ServoStyleConsts.h"\nusing namespace mozilla;\n'
 source+='template<class T> void Compatible() { using S='+name+'<uint64_t,uint64_t>; using D='+name+'<uint64_t,T>; using A=StyleArcInner<S>; using B=StyleArcInner<D>; static_assert(alignof(B)<=alignof(A),"alignment"); static_assert(sizeof(B)<=sizeof(A),"extent"); static_assert(offsetof(A,data)==offsetof(B,data),"base"); static_assert(offsetof(S,header)==offsetof(D,header),"header"); static_assert(offsetof(S,len)==offsetof(D,len),"length"); StyleArcSlice<T> empty; (void)empty.Length(); }\n'
 source+=''.join('template void Compatible<'+t+'>();\n' for t in types)
 source+='struct alignas(64) High { unsigned char data[64]; }; void Nondefault(const StyleArcSlice<High>& a) { auto b=a; (void)b.AsSpan(); }\n'
 for negative in [False,True]:
  label=variant+('-negative' if negative else '-positive');f=P/(label+'.cpp');f.write_text(source+('void RejectedDefault() { StyleArcSlice<High> value; }\n' if negative else ''))
  for path,row in old['dependencies'].items():assert sha(Path(path))==row['sha256'],path
  cmd=[str(overlaypath) if x==str(F/'overlay.json') else str(f) if x==str(F/'api.cpp') else x for x in old['command']]
  r=subprocess.run(cmd,cwd=P,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=90);(P/(label+'.log')).write_text(r.stdout);assert (r.returncode!=0)==negative,(label,r.stdout)
  if negative:assert 'Empty singleton cannot represent this element alignment' in r.stdout
  for path,row in old['dependencies'].items():assert sha(Path(path))==row['sha256'],path
  rows.append({'label':label,'exit':r.returncode,'source_sha256':sha(f),'helper_sha256':sha(helper),'log_sha256':sha(P/(label+'.log')),'command':cmd})
result={'rows':rows,'types':types,'type_count':len(types),'unchanged_parent_dependencies':len(old['dependencies']),'scope':'Configured aarch64 concrete default layouts; High nondefault ownership compiles, only High default rejected.'};(P/'CPP.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
