
struct ReflowOutput{};
struct nsReflowStatus{bool IsEmpty()const{return true;}};
class nsInlineFrame;
class nsLineLayout{public:bool first=false;size_t dirtyNext=0;nsIFrame*container=nullptr;bool GetInFirstLine()const{return first;}void SetInFirstLine(bool b){first=b;}nsIFrame*LineContainerFrame()const{return container;}void SetDirtyNextLine(){++dirtyNext;}};
struct ReflowInput{nsInlineFrame*mFrame;nsLineLayout*mLineLayout;};
struct AutoFrameListPtr:std::unique_ptr<nsFrameList>{AutoFrameListPtr(nsPresContext*,nsFrameList*p):std::unique_ptr<nsFrameList>(p){}};
class nsInlineFrame:public nsIFrame{public:
 enum class SetParentDuringReflow{No,Yes};
 struct InlineReflowInput{nsInlineFrame*mNextInFlow;nsIFrame*mLineContainer;nsLineLayout*mLineLayout;SetParentDuringReflow mSetParentDuringReflow;nsIFrame*mPrevFrame=nullptr;InlineReflowInput(const ReflowInput&,SetParentDuringReflow);};
 nsInlineFrame*next=nullptr,*previous=nullptr;nsPresContext*pc=nullptr;nsFrameList mFrames;std::unique_ptr<nsFrameList>overflowFrames;bool marked=false,reflowEntered=false;size_t floatReparents=0;std::vector<nsIFrame*>entryFrames;
 nsInlineFrame*GetNextInFlow()const{return next;}nsInlineFrame*GetPrevInFlow()const{return previous;}nsPresContext*PresContext()const{return pc;}nsFrameList*GetOverflowFrames(){return overflowFrames.get();}const nsFrameList*GetOverflowFrames()const{return overflowFrames.get();}nsFrameList*StealOverflowFrames(){return overflowFrames.release();}void DestroyOverflowList(){overflowFrames.reset();}
 void MarkInReflow(){marked=true;}bool IsAbsoluteContainer()const{return false;}void ReparentFloatsForInlineChild(nsIFrame*,nsIFrame*,bool){++floatReparents;}
 virtual nsIFrame*PullOneFrame(nsPresContext*,InlineReflowInput&);static bool HasFramesToPull(nsInlineFrame*);virtual bool DrainSelfOverflowList(){return false;}
 void ReflowFrames(nsPresContext*,const ReflowInput&input,InlineReflowInput&,ReflowOutput&,nsReflowStatus&){assert(input.mLineLayout->GetInFirstLine());reflowEntered=true;entryFrames=mFrames.frames;}
};
class nsFirstLineFrame:public nsInlineFrame{public:void Reflow(nsPresContext*,ReflowOutput&,const ReflowInput&,nsReflowStatus&);nsIFrame*PullOneFrame(nsPresContext*,InlineReflowInput&)override;bool DrainSelfOverflowList()override;};
