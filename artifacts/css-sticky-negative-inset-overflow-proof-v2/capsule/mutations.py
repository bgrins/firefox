MUTANTS={
 'normalization-sign':('limits','-=\n          delta;','+=\n          delta;',2),
 'auto-activation':('limits','!= NS_AUTOOFFSET ||','!= NS_AUTOOFFSET &&',2),
 'wrong-logical-end':('limits','LogicalSide::IEnd : LogicalSide::BEnd','LogicalSide::BEnd : LogicalSide::IEnd',1),
 'far-border-sign':('limits','-\n                                rect.height','+\n                                rect.height',1),
 'parent-offset-sign':('limits','- sfOffset.y + frameOffset.y','+ sfOffset.y + frameOffset.y',2),
 'position-direction':('do_position','std::max(position.y, std::min(stick.Y(), contain.YMost()))','std::min(position.y, std::min(stick.Y(), contain.YMost()))',1),
 'omit-intersection':('scroll_ranges','*aInner = aInner->Intersect(*aOuter);',';',1),
 'first-continuation':('scroll_ranges','nsLayoutUtils::FirstContinuationOrIBSplitSibling(aFrame)','aFrame',1),
 'omit-clamp':('scroll_ranges','*aInner = aInner->MoveInsideAndClamp(*aOuter);',';',1),
}

def change(records,name):
    fn,old,new,count=MUTANTS[name]
    if records[fn].count(old)!=count:raise RuntimeError('mutation source count '+name)
    records[fn]=records[fn].replace(old,new)
