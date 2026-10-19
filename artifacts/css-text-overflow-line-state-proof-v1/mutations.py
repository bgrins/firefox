from extract import complete


def replace_once(text,old,new):
    assert text.count(old)==1,(old,text.count(old))
    return text.replace(old,new)


def edit_function(core,signature,fn):
    code,_,_=complete(core,signature)
    return replace_once(core,code,fn(code))


def native_mutation(name):
    def mutate(core,decl):
        if name in ['omit-start-restore','omit-end-restore','swap-restoration','clear-cache','omit-clamp-restoration','reverse-end-priority']:
            def edit(code):
                if name=='omit-start-restore':return replace_once(code,'  mIStart.mISize = mIStart.mIntrinsicISize;\n','')
                if name=='omit-end-restore':return replace_once(code,'  mIEnd.mISize = mIEnd.mIntrinsicISize;\n','')
                if name=='swap-restoration':
                    code=replace_once(code,'mIStart.mISize = mIStart.mIntrinsicISize;','mIStart.mISize = mIEnd.mIntrinsicISize;')
                    return replace_once(code,'mIEnd.mISize = mIEnd.mIntrinsicISize;','mIEnd.mISize = mIStart.mIntrinsicISize;')
                if name=='clear-cache':return replace_once(code,'  Maybe<Marker> prevIEnd;','  mIStart.mInitialized = false;\n  mIEnd.mInitialized = false;\n  Maybe<Marker> prevIEnd;')
                if name=='omit-clamp-restoration':return replace_once(code,'    mIEnd = prevIEnd.extract();','    (void)prevIEnd.extract();')
                return replace_once(code,'    needIStart = false;','    needIEnd = false;')
            core=edit_function(core,'void TextOverflow::ProcessLine(',edit)
        elif name=='retry-reset-destroys-clipping':
            decl=replace_once(decl,'    void Reset() {','    void Reset() {\n      mISize = mIntrinsicISize;')
        elif name=='corrupt-clipped-intrinsic':
            def edit(code):
                return replace_once(code,'          clippedIEndMarker = true;', '          clippedIEndMarker = true;\n          mIEnd.mIntrinsicISize = mIEnd.mISize;')
            core=edit_function(core,'LogicalRect TextOverflow::ExamineLineFrames(',edit)
        else:raise ValueError(name)
        return core,decl
    return mutate

NATIVE=['omit-start-restore','omit-end-restore','clear-cache',
        'omit-clamp-restoration','reverse-end-priority','corrupt-clipped-intrinsic',
        'retry-reset-destroys-clipping']
