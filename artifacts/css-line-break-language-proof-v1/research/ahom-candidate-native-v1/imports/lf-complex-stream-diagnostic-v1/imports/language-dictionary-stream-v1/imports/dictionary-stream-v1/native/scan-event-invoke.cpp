scanner.ScanFrame(&container);scanner.FlushFrames(false,false);
auto*created=frames[0][0].GetTextRun(nsTextFrame::eInflated);assert(created);scanner.FlushLineBreaks(created);
for(auto&group:frames)for(auto&f:group)assert(f.GetTextRun(nsTextFrame::eInflated)==created);
unsigned mode=id[0]-'0';assert(mode<5);
if(mode>=2)for(auto&group:frames)for(auto&f:group)f.style.mHyphenateLimitChars.total_word_length.value=f.style.mHyphenateLimitChars.total_word_length.value==5?100:5;
if(mode==1||mode==3)for(auto&group:frames)for(auto&f:group)f.ClearTextRun(nullptr,nsTextFrame::eInflated);
if(mode==2){
 PresShell shell;container.shell=&shell;container.children.resize(1);
 for(size_t i=0;i<ancestors.size();i++){auto*p=ancestors[i].get();p->shell=&shell;p->children.resize(1);container.children[0].mList.push_back(p);for(auto&f:frames[i]){f.shell=&shell;p->children[0].mList.push_back(&f);}}
 nsStyleText before=container.style,after=before;after.mHyphenateLimitChars.total_word_length.value=100;
 auto hint=before.CalcDifference(after);assert(hint&nsChangeHint_ClearDescendantIntrinsics);StyleChangeReflow(&container,hint);
 for(auto&group:frames)for(auto&f:group)assert(!f.GetTextRun(nsTextFrame::eInflated)&&f.intrinsicMarks);
}
scanner.mCurrentRunContextInfo=0;scanner.mNextRunContextInfo=0;scanner.mStartOfLine=true;scanner.mCommonAncestorWithLastFrame=nullptr;
scanner.ScanFrame(&container);scanner.FlushFrames(false,false);
auto*before=created;created=frames[0][0].GetTextRun(nsTextFrame::eInflated);assert(created);
for(auto&group:frames)for(auto&f:group)assert(f.GetTextRun(nsTextFrame::eInflated)==created);
assert((created==before)==(mode==0||mode==4));std::cout<<id<<" REUSED "<<(created==before)<<"\n";
auto&run=*static_cast<nsTransformedTextRun*>(created);
