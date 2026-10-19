  Document* mDocument;
  ScrollerInfo mScrollerInfo;
  StyleScrollAxis mAxis;
  Maybe<StateSnapshot> mCachedStateSnapshot;
  Maybe<CurrentTimeData> mCachedCurrentTime;
  AnimationOrder mAnimationOrder;
  ScrollTimeline(Document*,const ScrollerInfo&,StyleScrollAxis);
  static already_AddRefed<ScrollTimeline> MakeNamed(Document*,Element*,const PseudoStyleRequest&,StyleScrollAxis);
  static already_AddRefed<ScrollTimeline> MakeAnonymous(Document*,const NonOwningAnimationTarget&,StyleScrollAxis,StyleScroller);
  static std::pair<const Element*,PseudoStyleRequest> FindNearestScroller(Element*,const PseudoStyleRequest&);
  Element* GetSource()const;
  StateSnapshot ComputeSnapshot()const;
  StateSnapshot GetSnapshot()const;
  bool UpdateCachedCurrentTime();
  void TimelineDataDidChange();
  Maybe<ComputedTimelineData> ComputeTimelineData()const;
  Nullable<TimeDuration> GetCurrentTimeAsDuration()const override;
  void GetCurrentTime(Nullable<OwningCSSNumberish>&)const;
  static ScrollerInfo Info(int type,Element* e,PseudoStyleRequest p){
    return type==3?ScrollerInfo::Named(e,p):ScrollerInfo::Anonymous(ScrollerInfo::Type(type),e,p);
  }
  int snapshotPseudo()const{return int(mCachedStateSnapshot->mSource.mPseudoRequest.type);}
  bool snapshotRoot()const{return mCachedStateSnapshot->mIsRoot;}
