import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'development-build/full'
changes=[]
def once(text,before,after,name):
 n=text.count(before);assert n==1,(name,n);changes.append({'name':name,'before':before,'after':after});return text.replace(before,after)
for flavor in ['original','candidate','standalone']:
 text=(OUT/f'lifecycle-{flavor}.cpp').read_text()
 old='scanner.FlushFrames(false,false);auto*created=frames[0][0].GetTextRun(nsTextFrame::eInflated);assert(created);auto&run=*static_cast<nsTransformedTextRun*>(created);'
 new='\n  std::vector<BuildTextRunsScanner::MappedFlow> savedFlows(scanner.mMappedFlows.begin(),scanner.mMappedFlows.end());\n  auto savedMax=scanner.mMaxTextLength;auto savedEncoding=scanner.mDoubleByteText;\n  scanner.FlushFrames(false,false);auto*created=frames[0][0].GetTextRun(nsTextFrame::eInflated);assert(created);\n  scanner.FlushLineBreaks(created);\n  unsigned mode=id[0]-\'0\';assert(mode<5);\n  if(mode>=2)for(auto&group:frames)for(auto&f:group)f.style.mHyphenateLimitChars.total_word_length.value=f.style.mHyphenateLimitChars.total_word_length.value==5?100:5;\n  if(mode==2)for(auto&group:frames)for(auto&f:group)f.ClearTextRun(nullptr,nsTextFrame::eInflated);\n  scanner.mMaxTextLength=0;scanner.mDoubleByteText=false;\n  for(size_t i=0;i<savedFlows.size();i++){scanner.mMappedFlows.AppendElement(savedFlows[i]);for(auto&f:frames[i])scanner.AccumulateRunInfo(&f);}\n  assert(scanner.mMaxTextLength==savedMax&&scanner.mDoubleByteText==savedEncoding);scanner.mCurrentRunContextInfo=0;scanner.mNextRunContextInfo=0;\n  scanner.mCurrentFramesAllSameTextRun=mode==1||mode==3?nullptr:frames[0][0].GetTextRun(nsTextFrame::eInflated);\n  auto*before=created;\n  scanner.FlushFrames(false,false);created=frames[0][0].GetTextRun(nsTextFrame::eInflated);assert(created);\n  std::cout<<id<<" REUSED "<<(created==before)<<"\\n";\n  assert((created==before)==(mode==0||mode==4));\n  auto&run=*static_cast<nsTransformedTextRun*>(created);\n'
 text=once(text,old,new,flavor+' caller fresh/reuse/invalidation experiment')
 (OUT/f'reuse-{flavor}.cpp').write_text(text)
(OUT/'reuse-extraction.json').write_text(json.dumps({'adaptations':changes,'source':'complete lifecycle methods unchanged; runner orchestrates explicit clear or retained-pointer negative control, not PresShell event admission'},indent=2)+'\n')
