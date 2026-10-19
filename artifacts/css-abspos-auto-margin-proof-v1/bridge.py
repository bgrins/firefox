import hashlib
from pathlib import Path

BASE = Path(__file__).resolve().parent
HELPER = 'void AbsoluteContainingBlock::ResolveAutoMarginsAfterLayout('
INLINE = 'void ReflowInput::ComputeAbsPosInlineAutoMargin('
BLOCK = 'void ReflowInput::ComputeAbsPosBlockAutoMargin('
CALL_OLD = '      ResolveAutoMarginsAfterLayout(kidReflowInput, cbSize, kidSize, margin,\n                                    offsets);\n\n'
CALL_NEW = '      ResolveAutoMarginsAfterLayout(kidReflowInput, cbSize, kidSize, margin,\n                                    offsets, iInsetAuto, bInsetAuto);\n\n'
FLAGS_END = '      const bool bInsetAuto = bStartInsetAuto || bEndInsetAuto;\n'


def extract(text, signature):
    start = text.index(signature)
    end = text.index('{', start)+1
    depth = 1
    while depth:
        depth += (text[end] == '{') - (text[end] == '}')
        end += 1
    return text[start:end]


def caller_block(text):
    scope = text.index('void AbsoluteContainingBlock::ReflowAbsoluteFrame(')
    end = text.index(FLAGS_END,scope)+len(FLAGS_END)
    start = text.rindex('      const auto* stylePos = aKidFrame->StylePosition();',scope,end)
    block = text[start:end]
    if CALL_NEW in text:
        if text[end:end+len(CALL_NEW)+1] != '\n'+CALL_NEW:
            raise ValueError('candidate caller placement mismatch')
        return block+'\n'+CALL_NEW
    if text.count(CALL_OLD) != 1 or text.index(CALL_OLD) >= start:
        raise ValueError('original caller placement mismatch')
    return CALL_OLD+block


def preservation(before,candidate,header_before,header_candidate):
    old = extract(before,HELPER)
    tags_start = old.index('    const bool startSideMarginIsAuto =')
    tags_end = old.index('    if (aAxis == LogicalAxis::Inline)',tags_start)
    tags = old[tags_start:tags_end]
    expected = old.replace(tags,'')
    expected = expected.replace('const LogicalMargin& aOffsets) {','const LogicalMargin& aOffsets, bool aIInsetAuto, bool aBInsetAuto) {')
    before_arithmetic = '    // No need to substract border sizes because aKidSize has it included'
    expected = expected.replace(before_arithmetic,tags+'    if (!startSideMarginIsAuto && !endSideMarginIsAuto) {\n      return;\n    }\n\n'+before_arithmetic)
    expected = expected.replace('    const bool autoOffset =\n','    const bool autoOffset =\n        (aAxis == LogicalAxis::Inline ? aIInsetAuto : aBInsetAuto) ||\n')
    old_arithmetic = '''      const nscoord stretchFitSize = std::max(
          0, aCBSize.Size(aAxis, outerWM) - aOffsets.StartEnd(aAxis, outerWM) -
                 aMargin.StartEnd(aAxis, outerWM));
      availMarginSpace = stretchFitSize - aKidSize.Size(aAxis, outerWM);'''
    new_arithmetic = '''      const nscoord insetModifiedSize = std::max(
          0, aCBSize.Size(aAxis, outerWM) - aOffsets.StartEnd(aAxis, outerWM));
      availMarginSpace = insetModifiedSize - aMargin.StartEnd(aAxis, outerWM) -
                         aKidSize.Size(aAxis, outerWM);'''
    if expected.count(old_arithmetic) != 1:
        raise ValueError('old arithmetic marker mismatch')
    expected = expected.replace(old_arithmetic,new_arithmetic)
    whole = before.replace(old,expected,1).replace(CALL_OLD,'',1).replace(FLAGS_END,FLAGS_END+'\n'+CALL_NEW,1)
    if whole != candidate:
        raise ValueError('whole C++ preservation mismatch')
    header = header_before.replace('                                     const LogicalMargin& aOffsets);','                                     const LogicalMargin& aOffsets,\n                                     bool aIInsetAuto, bool aBInsetAuto);',1)
    header = header.replace('   * aMargin and aOffsets are both outparams (though we only touch aOffsets if\n   * the position is overconstrained)', '   * aIInsetAuto and aBInsetAuto describe anchor-resolved styles, before auto\n   * insets are replaced with numeric offsets.\n   *\n   * aMargin is an outparam.',1)
    if header != header_candidate:
        raise ValueError('whole header preservation mismatch')
    return {'helper_sha256':hashlib.sha256(extract(candidate,HELPER).encode()).hexdigest(),
            'caller_block_sha256':hashlib.sha256(caller_block(candidate).encode()).hexdigest(),
            'caller_scope':'exact provenance/dispatch block; not entire ReflowAbsoluteFrame',
            'allowed_edits':['margin-tag queries moved before arithmetic','no-auto early return','explicit inset flags plus existing sentinels','floor IMCB before margin subtraction','caller moved after existing provenance booleans','header flags and documentation']}


def source(native,reflow):
    candidate = CALL_NEW in native
    prefix = (BASE/'bridge-prefix.cpp').read_text().replace('__FLAGS_DECL__',', bool, bool' if candidate else '')
    caller = '''std::array<bool, 2> AbsoluteContainingBlock::Caller(
    ReflowInput& kidReflowInput, const LogicalSize& cbSize, const LogicalSize& kidSize,
    LogicalMargin& margin, const LogicalMargin& offsets, nsIFrame* aKidFrame,
    AnchorPosResolutionCache* aAnchorPosResolutionCache, WritingMode outerWM) {
'''+caller_block(native)+'  return {iInsetAuto, bInsetAuto};\n}\n'
    return '\n'.join([prefix,extract(reflow,INLINE),extract(reflow,BLOCK),extract(native,HELPER),caller,(BASE/'bridge-suffix.cpp').read_text()])
