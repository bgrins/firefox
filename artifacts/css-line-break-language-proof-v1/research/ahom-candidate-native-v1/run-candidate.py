import argparse,ast,hashlib,json,os,re,shutil,subprocess,sys
from pathlib import Path
R=Path(__file__).resolve().parent
O=R/'build';O.mkdir(exist_ok=True)
D=R/'imports/complex-encoding-diagnostic-v1'
S=R/'imports/lf-complex-stream-diagnostic-v1'
L=S/'imports/language-dictionary-stream-v1'
P=L/'imports/dictionary-stream-v1'
for root,digest in [(D,'cd95022d7abf2ae31c6d34d8a4245a12107dcf60d7c44483fe09ce8924753a1b'),(S,'6ef82e8a2e9befbcb0981742b8142b6e40b3d083bf4e1951853f5b80ff7f2c2f')]:
 raw=(root/'MANIFEST.json').read_bytes();assert hashlib.sha256(raw).hexdigest()==digest
 for name,h in json.loads(raw)['files'].items():
  q=root/name;assert not q.is_symlink() and q.resolve().is_relative_to(root)
  assert hashlib.sha256(q.read_bytes()).hexdigest()==h,name
candidate=R/'inputs/third_party__rust__icu_segmenter__src__line.rs'
assert hashlib.sha256(candidate.read_bytes()).hexdigest()=='a511212ad35e22fa96ae107063c5107fd9c2eb3cdd173a1f28e3307306bd11a4'
tools=json.loads((D/'TOOLS.json').read_text())
for t in tools.values():assert hashlib.sha256(Path(t['path']).read_bytes()).hexdigest()==t['sha256']
commands=[]
def run(name,args,cwd=None,env=None,input=None):
 result=subprocess.run(list(map(str,args)),cwd=cwd,env=env,input=input,text=True,capture_output=True,timeout=900)
 (O/(name+'.stdout')).write_text(result.stdout);(O/(name+'.stderr')).write_text(result.stderr)
 commands.append({'name':name,'args':list(map(str,args)),'cwd':str(cwd),'exit':result.returncode})
 (O/'COMMANDS.json').write_text(json.dumps(commands,indent=2)+'\n')
 print(name,result.returncode,flush=True);assert result.returncode==0,(name,result.stderr[-2000:])
 return result.stdout
B=O/'candidate-bridge'
if B.exists():shutil.rmtree(B)
source=D/'imports/bridge-v1'
m=json.loads((source/'MANIFEST.json').read_text()) if (source/'MANIFEST.json').exists() else None
for part in ['icu','provider-crates']:
 shutil.copytree(source/part,B/part)
old=B/'icu/vendor/icu_segmenter/src/line.rs'
oldhash=hashlib.sha256(old.read_bytes()).hexdigest();assert oldhash=='08351143911687809801ab86c1c806bca963450c39e6eb6c89872e5ed928d28e'
old.write_bytes(candidate.read_bytes())
checksum=B/'icu/vendor/icu_segmenter/.cargo-checksum.json'
j=json.loads(checksum.read_text());j['files']['src/line.rs']=hashlib.sha256(old.read_bytes()).hexdigest();checksum.write_text(json.dumps(j))
env=dict(os.environ,CARGO_HOME=str(O/'cargo-home'),RUSTC=tools['rustc']['path'],UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1')
run('candidate-icu',[tools['cargo']['path'],'build','--locked','--offline','--target-dir',O/'icu'],B/'icu',env)
results={}
for phase,deps,lib in [('original',P/'development-build/icu/debug/deps',P/'development-build/icu/debug/liblanguage_break_provider.a'),('candidate',O/'icu/debug/deps',O/'icu/debug/liblanguage_break_provider.a')]:
 extern=[]
 for name in ['icu_segmenter','icu_provider']:
  matches=list(deps.glob('lib'+name+'-*.rlib'));assert len(matches)==1
  extern+=['--extern',name+'='+str(matches[0])]
 raw={}
 for name in ['lf-complex-sa-domain','lf-complex-encoding']:
  binary=O/(phase+'-'+name)
  run(phase+'-'+name+'-compile',[tools['rustc']['path'],'--edition','2021',D/'native'/(name+'.rs'),'-L','dependency='+str(deps),*extern,'-o',binary])
  raw[name]=run(phase+'-'+name,[binary],env=env)
 if phase=='original':
  for name,value in raw.items():assert value==(D/'evidence'/name/'raw.txt').read_text()
 else:assert raw['lf-complex-sa-domain']==results['original']['domain']
 records=[]
 for line in raw['lf-complex-encoding'].splitlines():
  match=re.fullmatch(r'(\S+) (Normal|BreakAll) SCALARS (\[.*?\]) UTF8 (\[.*?\]) UTF16 (\[.*?\]) MAP8 .* EQUAL (true|false)',line);assert match,line
  name,mode,scalars,b8,b16,equal=match.groups();scalars,b8,b16=map(ast.literal_eval,[scalars,b8,b16]);a8=[0];a16=[0]
  for c in scalars:a8.append(a8[-1]+len(chr(c).encode('utf8')));a16.append(a16[-1]+len(chr(c).encode('utf-16-le'))//2)
  ps8=[a8.index(x)for x in b8];ps16=[a16.index(x)for x in b16]
  assert (ps8==ps16)==(equal=='true')
  records.append({'name':name,'mode':mode,'utf8':b8,'utf16':b16,'scalar8':ps8,'scalar16':ps16})
 if phase=='candidate':
  assert all(x['scalar8']==x['scalar16']for x in records)
  for before,after in zip(results['original']['encoding'],records,strict=True):
   assert before['utf8']==after['utf8']
   if before['scalar8']==before['scalar16']:assert before==after
 bridge=P/'provider-bridge-v1'
 binary=O/(phase+'-gecko-provider')
 run(phase+'-gecko-compile',[tools['clang']['path'],'-std=c++20','-g','-O1','-fsanitize=undefined','-I',bridge/'development-build/provider','-I',bridge/'provider-crates/icu_capi/bindings/cpp','-I',bridge/'source/providers/intl/icu/source/common','-I',bridge/'native',D/'native/provider-main.cpp',lib,'-licucore','-framework','CoreFoundation','-framework','Security','-o',binary])
 gecko=run(phase+'-gecko',[binary],env=env,input=(D/'evidence/lf-complex-gecko/inputs.txt').read_text())
 if phase=='original':assert gecko==(D/'evidence/lf-complex-gecko/raw.txt').read_text()
 for index,(name,mode)in enumerate([('thai-ahom-thai','Normal')]*3+[('thai-ahom-thai','BreakAll'),('bmp-unknown','Normal')]):
  row=next(x for x in records if x['name']==name and x['mode']==mode)
  length=max(row['utf16']);expected=''.join('1'if i in row['utf16']else'0'for i in range(length))
  assert gecko.splitlines()[index]==expected
 # Use freshly generated complete native bodies and all original link dependencies,
 # replacing only the ICU static library with the explicitly pinned candidate build.
 links=json.loads((L/'development-build/dictionary-stream-language/COMMANDS.json').read_text())
 variants={}
 dictionary=P/'source/providers/intl/locales/en-US/hyphenation/hyph_en_US.hyf'
 for variant in ['original','candidate']:
  command=next(x['args']for x in links if Path(x['args'][-1]).name=='stream-'+variant)
  command=[str(lib)if x.endswith('/icu/debug/liblanguage_break_provider.a')else x for x in command]
  command[-1]=str(O/(phase+'-stream-'+variant));run(phase+'-stream-'+variant+'-compile',command)
  binary=command[-1]
  fixed=run(phase+'-stream-'+variant+'-fixed',[binary,dictionary],env=env,input=(L/'seeds/stream-lean-input.txt').read_text())
  assert fixed==(L/'development-build/dictionary-stream-language'/('stream-'+variant+'.stdout')).read_text()
  lf=run(phase+'-stream-'+variant+'-lf',[binary,dictionary],env=env,input=(S/'evidence/inputs.txt').read_text())
  if phase=='original':assert lf==(S/'evidence'/(variant+'.raw.txt')).read_text()
  cases={}
  for line in lf.splitlines():
   w=line.split()
   if w[0]=='shutdown':continue
   c=cases.setdefault(w[0],{'callbacks':[],'providers':[]})
   if w[1:3]==['CALLBACK_ID','B']:
    sink,owner,base,offset,length,*values=map(int,w[3:]);assert len(values)==length
    c['callbacks'].append({'sink':sink,'owner':owner,'base':base,'offset':offset,'values':values})
   if w[1:4]==['EVENT','provider','input']:c['providers'].append(list(map(int,w[4:])))
   if w[1]=='BREAKS':c.update(breaks=w[2],glyphs=w[4],errors=w[8])
  for name,c in cases.items():
   assert set(c['errors'])=={'0'};v=[0]*len(c['breaks'])
   for cb in c['callbacks']:
    for i,value in enumerate(cb['values']):
     pos=cb['base']+cb['offset']+i;assert 0<=pos<len(v)
     if value:v[pos]=value
   assert ''.join(map(str,v))==c['breaks']==c['glyphs']
  if phase=='candidate':
   before=results['original']['variants'][variant]
   for name,c in cases.items():
    assert c['providers']==before[name]['providers']
    if name.startswith('bmp'):assert c==before[name]
   assert all(cases['ahom-'+part]['glyphs'][6]=='1'for part in ['whole','before-lf','after-lf'])
   differences=[i for i,(a,b)in enumerate(zip(cases['ahom-whole']['glyphs'],cases['ahom-before-lf']['glyphs']))if a!=b]
   assert all(i in [4,5]for i in differences)
  variants[variant]=cases
 results[phase]={'domain':raw['lf-complex-sa-domain'],'encoding':records,'variants':variants,'gecko_vectors':gecko.splitlines()}
lean=R/'lean/Utf16Repair.lean'
text=lean.read_text();assert not re.search(r'\b(sorry|admit|axiom|native_decide|bv_decide)\b',text)
run('lean',[tools['lean']['path'],'-o',O/'Utf16Repair.olean',lean])
names=re.findall(r'^theorem (\w+)',text,re.M)
(O/'Axioms.lean').write_text('import Utf16Repair\n'+'\n'.join('#print axioms Utf16Repair.'+n for n in names)+'\n')
ax=run('axioms',[tools['lean']['path'],O/'Axioms.lean'],env=dict(os.environ,LEAN_PATH=str(O)));assert 'sorryAx'not in ax
for group in re.findall(r'depends on axioms: \[([^]]*)\]',ax):assert set(map(str.strip,group.split(',')))<={'propext','Classical.choice','Quot.sound',''}
results['proof']={'theorems':len(names),'scope':'Valid scalar encoding widths and prefix seek coordinates; provider alignment/implementation/heap boundaries explicit'}
(O/'RESULT.json').write_text(json.dumps(results,indent=2)+'\n');print('CANDIDATE_NATIVE_REPLAY_PASSED')
