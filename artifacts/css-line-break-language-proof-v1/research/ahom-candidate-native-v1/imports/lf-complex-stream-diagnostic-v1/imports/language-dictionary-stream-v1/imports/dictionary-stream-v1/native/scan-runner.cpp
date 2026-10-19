
std::string BuildTextRunsScanner::Snapshot()const{
 std::ostringstream o;o<<mMaxTextLength<<','<<mDoubleByteText<<','<<mStartOfLine<<','<<mNextRunContextInfo<<','<<mCurrentRunContextInfo<<','<<uintptr_t(mCurrentFramesAllSameTextRun)<<','<<(mLastFrame?mLastFrame->id:0)<<','<<(mCommonAncestorWithLastFrame?mCommonAncestorWithLastFrame->id:0)<<'|';
 for(auto&f:mMappedFlows)o<<f.mStartFrame->id<<':'<<(f.mEndFrame?f.mEndFrame->id:0)<<':'<<(f.mAncestorControllingInitialBreak?f.mAncestorControllingInitialBreak->id:0)<<';';o<<'|';for(auto*f:mLineBreakBeforeFrames)o<<f->id<<';';return o.str();
}
void BuildTextRunsScanner::FlushFrames(bool line,bool trailing){flushes.push_back(std::to_string(line)+std::to_string(trailing)+"@"+Snapshot());ResetRunInfo();}
int main(){std::string line;while(std::getline(std::cin,line)){
 std::istringstream in(line);std::string id;unsigned n;in>>id>>n;assert(n&&n<1000);
 std::vector<std::unique_ptr<nsIFrame>>nodes(n+1);std::vector<ComputedStyle>styles(n+1);std::vector<CharacterDataBuffer>buffers(n+1);std::vector<std::vector<unsigned>>rows(n+1,std::vector<unsigned>(15));nsPresContext pc;
 for(unsigned i=1;i<=n;i++){for(auto&x:rows[i])in>>x;auto&r=rows[i];assert(r[0]<6&&r[8]<=n&&r[11]<=n);if(r[0]==0)nodes[i]=std::make_unique<nsTextFrame>();else if(r[0]==4)nodes[i]=std::make_unique<nsPlaceholderFrame>();else nodes[i]=std::make_unique<nsIFrame>();}
 assert(in);
 for(unsigned i=0;i<=n;i++)styles[i].text.hyphenLimit=5+10*i;for(unsigned i=1;i<=n;i++)if(rows[i][0]==0){auto&r=rows[i];buffers[r[8]].text.resize(std::max(size_t(r[9]+r[10]),buffers[r[8]].text.size()),u'a');}
 for(unsigned i=1;i<=n;i++){auto&r=rows[i];auto*f=nodes[i].get();f->id=i;f->type=LayoutFrameType(r[0]);f->parent=nodes[r[1]].get();f->sibling=nodes[r[2]].get();f->principal.first=nodes[r[3]].get();f->overflow.first=nodes[r[4]].get();f->content=r[8];f->style=&styles[r[11]];f->canContinue=r[12];f->block=!r[1];f->state=r[7]?NS_FRAME_IS_FLUID_CONTINUATION:0;if(r[14]&1)f->state|=PLACEHOLDER_FOR_ABSPOS;if(r[14]&2)f->state|=PLACEHOLDER_FOR_FIXEDPOS;
  if(r[0]==4)static_cast<nsPlaceholderFrame*>(f)->outOfFlow=nodes[r[5]].get();
  if(r[0]==0){auto*t=static_cast<nsTextFrame*>(f);t->continuation=static_cast<nsTextFrame*>(nodes[r[6]].get());t->next=r[7]?t->continuation:nullptr;t->start=r[9];t->end=r[9]+r[10];t->buffer=&buffers[r[8]];t->context=&pc;t->run=r[13];if(r[14]&4){t->buffer->text.at(t->end-1)=char16_t(10);t->style->text.newline=true;}if(r[14]&8)t->buffer->doubleByte=true;}
 }
 BuildTextRunsScanner scanner;scanner.mCommonAncestorWithLastFrame=nodes[1].get();scanner.ScanFrame(nodes[1].get());
 std::cout<<id<<" STATE "<<scanner.Snapshot();for(auto&s:scanner.flushes)std::cout<<" FLUSH "<<s;std::cout<<'\n';
}}
