class TextOverflow {
 public:
  using FrameHashtable = FrameSet;
@@DECLARATIONS@@
  LogicalRect mContentArea;
  nsDisplayListBuilder* mBuilder=nullptr;
  nsBlockFrame* mBlock=nullptr;
  ScrollContainerFrame* mScrollContainerFrame=nullptr;
  nsDisplayList mMarkerList;
  nsSize mBlockSize{0,1};
  WritingMode mBlockWM{true};
  bool mCanHaveInlineAxisScrollbar=false;
  bool mAdjustForPixelSnapping=false;
  Marker mIStart,mIEnd;
  RefPtr<gfxTextRun> mEllipsisTextRun;
  void ProcessLine(const nsDisplayListSet&,nsLineBox*,uint32_t);
  LogicalRect GetLogicalScrollableOverflowRectRelativeToBlock(nsIFrame*) const;
  LogicalRect ExamineLineFrames(nsLineBox*,FrameHashtable*,AlignmentEdges*);
  void ExamineFrameSubtree(nsIFrame*,const LogicalRect&,const LogicalRect&,FrameHashtable*,AlignmentEdges*,bool*,InnerClipEdges*);
  void AnalyzeMarkerEdges(nsIFrame*,LayoutFrameType,const LogicalRect&,FrameHashtable*,AlignmentEdges*,bool*,InnerClipEdges*);
  static void AddMarker(Event& e,const Marker& m) {
    e.insert(e.end(),{m.mISize,m.mIntrinsicISize,m.mTextOverflowStyle->id,m.mHasOverflow,m.mBlockEllipsis?m.mBlockEllipsis->id:-1,m.mInitialized,m.mActive,m.mEdgeAligned});
  }
  void AddMarkers(Event& e) const { AddMarker(e,mIStart);AddMarker(e,mIEnd); }
  void ObserveAttempt(const LogicalRect& content,const LogicalRect& inside,const FrameHashtable& hide,const AlignmentEdges& a,bool visible,const InnerClipEdges& c) {
    assert(++attemptCount<=12);
    Event e{1};addRect(e,content);addRect(e,inside);AddMarkers(e);
    e.insert(e.end(),{visible,a.mIStart,a.mIEnd,a.mIEndOuter,a.mAssignedInner,c.mIStart,c.mIEnd,c.mAssignedIStart,c.mAssignedIEnd});addHidden(e,hide);events.push_back(std::move(e));
  }
  void PruneDisplayListContents(nsDisplayList* list,const FrameHashtable& hide,const LogicalRect& inside) {
    Event e{3,list->id};addRect(e,inside);AddMarkers(e);addHidden(e,hide);events.push_back(std::move(e));
  }
  void CreateMarkers(const nsLineBox*,bool start,bool end,const LogicalRect& inside,const LogicalRect& content,uint32_t number) {
    Event e{4,start,end,number};addRect(e,inside);addRect(e,content);AddMarkers(e);events.push_back(std::move(e));
  }
};

