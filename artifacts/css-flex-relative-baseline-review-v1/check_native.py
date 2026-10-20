import argparse
import hashlib
import json
from pathlib import Path
import runpy
import shutil
import subprocess
import sys
import tempfile
if sys.flags.optimize:raise RuntimeError('Assertions required')
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parent

def body(s,marker):
 a=s.index(marker);b=s.index('{',a);depth=1;e=b+1
 while depth:
  if s[e]=='{':depth+=1
  if s[e]=='}':depth-=1
  e+=1
 return s[a:e]

def generated(path,mutant=None):
 source=path.read_text();provider=(ROOT/'retained-nsIFrameInlines.h').read_text()
 normal=body(provider,'nsPoint nsIFrame::GetNormalPosition(')
 logical=body(provider,'mozilla::LogicalPoint nsIFrame::GetLogicalNormalPosition(')
 if mutant=='force-current':normal=normal.replace('hasProperty ? normalPosition : GetPosition()','GetPosition()')
 if mutant=='force-property':normal=normal.replace('hasProperty ? normalPosition : GetPosition()','normalPosition')
 if mutant=='omit-frame-size':logical=logical.replace('aContainerSize - mRect.Size()','aContainerSize')
 output=source[source.index('void nsFlexContainerFrame::PopulateReflowOutput('):]
 end=output.index('ResolvedAscent(true);')+len('ResolvedAscent(true);');start=output.rfind('aFlr.mAscent =',0,end);first=output[start:end]
 start=output.index('const nscoord lastAscent =');end=output.index('aFlr.mAscentForLast =',start);end=output.index(';',end)+1;last=output[start:end]
 helper=body(source,'Maybe<nscoord> NaturalBaselineBOffset(') if 'Maybe<nscoord> NaturalBaselineBOffset(' in source else ''
 return '#include "facade.hpp"\n'+normal+'\n'+logical+'\n#define HAS_HELPER '+str(int(bool(helper)))+'\nstruct FlexLine{nsTArray<FlexItem> mItems;\n'+helper+'\n};\nstatic Result fallback(const FlexItem& item,WritingMode flexWM,nsSize physical){\nResult aFlr;const FlexItem* firstBaselineItem=&item;const FlexItem* lastBaselineItem=&item;LogicalSize desiredSizeInFlexWM(flexWM,physical);\n'+first+'\n'+last+'\nreturn aFlr;\n}\n'

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();a.out.mkdir(parents=True,exist_ok=False)
 checks=runpy.run_path(str(ROOT/'check.py'));checks['authenticate']();checks['authenticate_providers']()
 clang=Path('/usr/bin/clang++');assert hashlib.sha256(clang.read_bytes()).hexdigest()=='b8763cf250e607a778bb4603cecb5b90338814d0a3dfcba0d57b1de242f610e9'
 roles=[('shared-before',ROOT/'inputs/relative/before.cpp',36,36,True),('shared-after',ROOT/'inputs/relative/candidate.cpp',0,0,True),('natural-standalone',ROOT/'inputs/natural/standalone-92a6fddf18e5.cpp',0,36,True),('relative-standalone',ROOT/'inputs/relative/standalone-92a6fddf18e5.cpp',0,0,False)]
 runs=[]
 with tempfile.TemporaryDirectory(prefix='relative-baseline-review-') as tmp:
  t=Path(tmp)
  for name in ['main.cpp','facade.hpp']:shutil.copyfile(ROOT/name,t/name)
  for role,path,helperWrong,fallbackWrong,hasHelper in roles+[('mutant-'+m,ROOT/'inputs/relative/candidate.cpp',None,None,True) for m in ['force-current','force-property','omit-frame-size']]:
   mutant=role.removeprefix('mutant-') if role.startswith('mutant-') else None
   code=generated(path,mutant);(t/'generated.hpp').write_text(code);(a.out/(role+'.hpp')).write_text(code)
   for opt in ['0','2']:
    exe=t/'run';p=subprocess.run([str(clang),'-std=c++17','-O'+opt,'-fsanitize=undefined','-fno-sanitize-recover=undefined',str(t/'main.cpp'),'-o',str(exe)],capture_output=True,text=True)
    (a.out/(role+'-O'+opt+'-compile.log')).write_text(p.stdout+p.stderr);assert p.returncode==0,p.stdout+p.stderr
    p=subprocess.run([str(exe)],capture_output=True,text=True);(a.out/(role+'-O'+opt+'.log')).write_text(p.stdout+p.stderr);assert p.returncode==0,p.stdout+p.stderr
    result=json.loads(p.stdout);assert result['fallbackRows']==108 and result['helperRows']==(108 if hasHelper else 0)
    if mutant:assert result['providerWrong']>0 and result['helperWrong']>0 and result['fallbackWrong']>0
    else:assert result['providerWrong']==0 and result['helperWrong']==helperWrong and result['fallbackWrong']==fallbackWrong,(role,result)
    runs.append({'role':role,'optimization':opt,**result})
 (a.out/'RESULT.json').write_text(json.dumps({'runs':runs,'scope':'Exact indexed normal-position providers plus extracted changed helper/fallback expressions; logical conversion and property storage are explicit facades; no property-lifetime or full writing-mode theorem','ownedProductsRemoved':True},indent=2)+'\n');print(json.dumps(runs))
if __name__=='__main__':main()
