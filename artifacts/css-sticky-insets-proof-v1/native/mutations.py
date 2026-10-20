from generate import generate,ROOT
import importlib.util

MUTATIONS={
 'auto_requires_both':('limits',[('computedOffsets->bottom != NS_AUTOOFFSET)', 'computedOffsets->bottom != NS_AUTOOFFSET)'),('||','&&')]),
 'auto_becomes_constraint':('limits',[]),
 'child_mode':('limits',[('WritingMode writingMode = cbFrame->GetWritingMode();','WritingMode writingMode = aFrame->GetWritingMode();')]),
 'omit_near_clamp':('do_position',[('position.y = std::max(position.y, std::min(stick.y, contain.YMost()));','position.y = position.y;')]),
 'missing_normal_moves':('continuations',[('if (!hadProperty) {','if (false) {')]),
 'collapse_continuations':('continuations',[('cont->GetNormalPosition() + translation','normalPosition + translation')]),
 'skip_offset_refresh':('update',[('ComputeStickyOffsets(f);','(void)f;')]),
 'earliest_strict':('timeline_earliest',[('aOffsetIgnoringSticky <= mEndSideUnstuckAt','aOffsetIgnoringSticky < mEndSideUnstuckAt')]),
}

def mutated(name):
 spec=importlib.util.spec_from_file_location('extract',ROOT/'source_extract.py')
 m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 rows={r['name']:r['body'] for r in m.selected('combined')}
 key,changes=MUTATIONS[name];old=rows[key];new=old
 if name=='auto_requires_both':
  if new.count('||')!=3:raise RuntimeError(('or roster',new.count('||')))
  new=new.replace('computedOffsets->top != NS_AUTOOFFSET ||','computedOffsets->top != NS_AUTOOFFSET &&').replace('computedOffsets->left != NS_AUTOOFFSET ||','computedOffsets->left != NS_AUTOOFFSET &&')
 elif name=='auto_becomes_constraint':
  split=new.index('  // Top\n')
  new=new[:split]+new[split:].replace('computedOffsets->','effectiveOffsets.')
 else:
  for before,after in changes:
   if new.count(before)!=1:raise RuntimeError((name,before,new.count(before)))
   new=new.replace(before,after)
 source=generate('combined','driver.cpp')
 if source.count(old)!=1 or old==new:raise RuntimeError(('mutation source binding',name))
 return source.replace(old,new)
