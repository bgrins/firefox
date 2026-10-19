MUTATIONS=[
('host-mode','ComputePhysicalAxis(scrollContainerFrame->GetWritingMode())','ComputePhysicalAxis(mSource.mElement->GetPrimaryFrame()->GetWritingMode())'),
('logical-swap','(!aWritingMode.IsVertical() &&\n                  mAxis == StyleScrollAxis::Inline) ||\n                 (aWritingMode.IsVertical() && mAxis == StyleScrollAxis::Block)', '(aWritingMode.IsVertical() &&\n                  mAxis == StyleScrollAxis::Inline) ||\n                 (!aWritingMode.IsVertical() && mAxis == StyleScrollAxis::Block)'),
('physical-mode','mAxis == StyleScrollAxis::X ||','(mAxis == StyleScrollAxis::X && !aWritingMode.IsVertical()) || (mAxis == StyleScrollAxis::Y && aWritingMode.IsVertical()) ||'),
('lose-named-pseudo','case Type::Name:\n      return NonOwningAnimationTarget{mSourceOrTarget};','case Type::Name:\n      return {mSourceOrTarget.mElement, PseudoStyleRequest::NotPseudo()};'),
('skip-nearest','return AnimationUtils::GetElementPseudoPair(element);','continue;'),
('skip-target','scrollContainerFrame->GetScrollTargetFrame()','static_cast<ScrollContainerFrame*>(scrollContainerFrame)'),
('retain-cache','mCachedCurrentTime.reset();','mCachedCurrentTime = prevCachedCurrentTime;'),
('wrong-coordinate','? scrollPosition.x\n                                                          : scrollPosition.y','? scrollPosition.y\n                                                          : scrollPosition.x'),
('stale-snapshot','mCachedStateSnapshot = Some(ComputeSnapshot());','if (!mCachedStateSnapshot) mCachedStateSnapshot = Some(ComputeSnapshot());'),
('position-notifies','mCachedCurrentTime->mMaxScrollOffset !=\n                                    prevCachedCurrentTime->mMaxScrollOffset','(mCachedCurrentTime->mMaxScrollOffset !=\n                                    prevCachedCurrentTime->mMaxScrollOffset || mCachedCurrentTime->mPosition != prevCachedCurrentTime->mPosition)'),
('nonzero-start','ComputedTimelineData{mCachedCurrentTime->mPosition, 0,','ComputedTimelineData{mCachedCurrentTime->mPosition, 1,')]

def mutate(code,index):
    name,before,after=MUTATIONS[index]
    assert code.count(before)==1,(name,code.count(before))
    offset=code.index(before)
    changed=code[:offset]+after+code[offset+len(before):]
    assert changed[:offset]+before+changed[offset+len(after):]==code
    return changed,dict(name=name,before=before,after=after,offset=offset,count=1,reversed=True)
