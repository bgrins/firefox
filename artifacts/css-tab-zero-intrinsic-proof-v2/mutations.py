NATIVE = ['remove_zero_guard','zero_returns_origin','nonpositive_guard',
          'minimum_loses_tab_assignment','preferred_loses_tab_assignment',
          'intrinsic_loses_before_spacing','intrinsic_loses_after_spacing',
          'normal_disables_tab_gate','normal_loses_after_spacing','cache_limit_not_updated',
          'minimum_loses_saturation','preferred_loses_saturation']


def replace_n(text,old,new,count):
    assert text.count(old)==count,(old,text.count(old),count)
    return text.replace(old,new)


def native_mutation(name):
    def apply(text):
        guard='  if (aTabWidth == 0.0) {\n    return aX;\n  }\n'
        if name=='remove_zero_guard':return replace_n(text,guard,'',1)
        if name=='zero_returns_origin':return replace_n(text,guard,guard.replace('return aX;','return 0.0;'),1)
        if name=='nonpositive_guard':return replace_n(text,guard,guard.replace('== 0.0','<= 0.0'),1)
        if name in ['minimum_loses_saturation','preferred_loses_saturation']:
            target='aData->mCurrentLine = NSCoordSaturatingAdd(aData->mCurrentLine, width);'
            assert text.count(target)==2
            pieces=text.split(target);i=0 if name.startswith('minimum') else 1
            replacement='aData->mCurrentLine += width;'
            return pieces[0]+(replacement if i==0 else target)+pieces[1]+(replacement if i==1 else target)+pieces[2]
        target='aData->mCurrentLine = nscoord(afterTab + spacing.mAfter);'
        if name in ['minimum_loses_tab_assignment','preferred_loses_tab_assignment']:
            assert text.count(target)==2
            pieces=text.split(target);i=0 if name.startswith('minimum') else 1
            replacement='(void)afterTab;'
            return pieces[0]+(replacement if i==0 else target)+pieces[1]+(replacement if i==1 else target)+pieces[2]
        if name=='intrinsic_loses_before_spacing':return replace_n(text,'aData->mCurrentLine += nscoord(spacing.mBefore);','aData->mCurrentLine += 0;',2)
        if name=='intrinsic_loses_after_spacing':return replace_n(text,target,'aData->mCurrentLine = nscoord(afterTab);',2)
        if name=='normal_disables_tab_gate':return replace_n(text,'if (tabWidth > 0) {','if (tabWidth > 100000) {',1)
        if name=='normal_loses_after_spacing':return replace_n(text,'mOffsetFromBlockOriginForTabs += spacing.mAfter;','mOffsetFromBlockOriginForTabs += 0;',1)
        if name=='cache_limit_not_updated':return replace_n(text,'mTabWidths->mLimit = aRange.end - startOffset;','mTabWidths->mLimit = 0;',1)
        raise ValueError(name)
    return apply
