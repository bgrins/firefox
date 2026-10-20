#!/usr/bin/env python3
import hashlib,itertools,json,pathlib,random,subprocess,shutil
P=pathlib.Path(__file__).resolve().parent
subprocess.run(['python3',str(P/'verify_inputs.py')],check=True)
O=P/'native-results';O.mkdir(exist_ok=True)
def extract(s,needle):
 start=s.index(needle);a=s.index('{',start);d=1;b=a+1
 while d:
  d+=(s[b]=='{')-(s[b]=='}');b+=1
 return s[start:b]
helper=extract((P/'inputs/providers/ReflowInput.h').read_text(),'template <class NumericType>\nNumericType CSSMinMax')
method=lambda name:extract((P/'inputs/native'/name).read_text(),'Maybe<nscoord> ScrollContainerFrame::GetNaturalBaselineBOffset')
old=method('before.cpp');new=method('candidate.cpp')
M=2**31-1
rows=[]
for g,c,k,h,p,w in itertools.product(range(2),range(2),range(3),range(2),range(2),range(3)):
 for o,i,bs,be,b in [(100,60,9,0,12),(100,200,0,9,12),(0,0,0,0,0),(100,200,9,11,-50),(100,200,9,11,300)]:
  rows.append([g,c,k,h,p,w,o,i,bs,be,b,-17])
small=list(rows)
for g,o,i,bs,be,b in itertools.product(range(2),[0,1,100,M],[0,1,100,M],[0,9,M],[0,11,M],[-M-1,-M,-1,0,1,M]):
 rows.append([g,1,0,0,1,2,o,i,bs,be,b,-17])
r=random.Random(20261020)
for _ in range(400):
 rows.append([r.randrange(2),1,0,0,1,r.randrange(3),r.randrange(M+1),r.randrange(M+1),r.randrange(M+1),r.randrange(M+1),r.randrange(-M-1,M+1),-17])
def oracle(row,candidate):
 g,c,k,h,p,w,o,i,bs,be,b,synth=row
 q=int(c==0 and g==1)
 if q and k==1:return [1,synth,0,q,0,0,0,0,1,-1,-1,-1]
 if h:return [0,0,1,q,0,0,0,0,0,-1,-1,-1]
 if not p:return [0,0,1,q,1,0,0,0,0,w,g,c]
 v=max(0,min(o,bs+(i-b if candidate and g else b)))
 if candidate and g:v=o-v
 return [1,v,1,q,1,int(candidate and g==1),1,1,0,w,g,c]
def run(name,body,data,expected,mutant=False):
 src=O/(name+'.cpp');src.write_text((P/'facade.hpp').read_text()+helper+'\n'+body+'\n'+(P/'main.cpp').read_text())
 receipts=[]
 for opt in ['0','2']:
  exe=O/(name+'-O'+opt)
  cmd=['/usr/bin/clang++','-std=c++17','-O'+opt,'-fsanitize=undefined,signed-integer-overflow','-fno-sanitize-recover=all',str(src),'-o',str(exe)]
  build=subprocess.run(cmd,text=True,capture_output=True)
  (O/(name+'-O'+opt+'-build.log')).write_text(build.stdout+build.stderr)
  assert build.returncode==0,(name,build.stderr)
  result=subprocess.run([str(exe)],input=''.join(' '.join(map(str,x))+'\n' for x in data),text=True,capture_output=True)
  (O/(name+'-O'+opt+'.out')).write_text(result.stdout)
  (O/(name+'-O'+opt+'.err')).write_text(result.stderr)
  exe.unlink()
  assert result.returncode==0,(name,result.stderr)
  actual=[list(map(int,line.split())) for line in result.stdout.splitlines()]
  assert len(actual)==len(expected)
  mismatches=[n for n,(a,b) in enumerate(zip(actual,expected)) if a!=b]
  assert bool(mismatches)==mutant,(name,mismatches[:3])
  receipts.append({'optimization':opt,'rows':len(data),'mismatches':len(mismatches),'first_mismatch':None if not mismatches else {'row':data[mismatches[0]],'expected':expected[mismatches[0]],'actual':actual[mismatches[0]]}})
 return receipts
out={}
(P/'CORPUS.json').write_text(json.dumps({'small':small,'wide':rows},indent=2)+'\n')
out['before']=run('before',old,small,[oracle(x,False) for x in small])
for name in ['candidate.cpp','standalone-92a6fddf18e5.cpp','standalone-976279105b2e.cpp']:
 assert method(name)==new
 out[name]=run(name[:-4],method(name),rows,[oracle(x,True) for x in rows])
mutants={
 'bend_only':new.replace('first ? int64_t(aBaseline)\n                  : int64_t(mScrolledFrame->BSize(aWM)) - aBaseline','int64_t(aBaseline)').replace('border.BStart(aWM) + fromStart','(first ? border.BStart(aWM) : border.BEnd(aWM)) + fromStart').replace('return first ? baseline : bSize - baseline;','return baseline;'),
 'omit_inner':new.replace('int64_t(mScrolledFrame->BSize(aWM)) - aBaseline','-int64_t(aBaseline)'),
 'omit_last_conversion':new.replace('return first ? baseline : bSize - baseline;','return baseline;'),
 'use_end_border':new.replace('border.BStart(aWM) + fromStart','border.BEnd(aWM) + fromStart'),
 'reverse_clamp_bounds':new.replace('int64_t(0), int64_t(bSize)','int64_t(bSize), int64_t(0)'),
 'contain_before_legacy':new.replace('  // Block containers','  if (StyleDisplay()->IsContainLayout()) { return Nothing{}; }\n  // Block containers'),
 'lose_forwarding':new.replace('->GetNaturalBaselineBOffset(aWM, aBaselineGroup, aExportContext)','->GetNaturalBaselineBOffset(aWM, BaselineSharingGroup::First, aExportContext)'),
}
for name,body in mutants.items():
 assert body!=new
 out[name]=run(name,body,rows,[oracle(x,True) for x in rows],True)
(P/'NATIVE-RESULTS.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:[(x['optimization'],x['rows'],x['mismatches']) for x in v] for k,v in out.items()},indent=2))
