from pathlib import Path
import hashlib
import re

BASE = Path(__file__).resolve().parent


def mask_cpp(text):
    pattern = r'//[^\n]*|/\*[\s\S]*?\*/|R"([^ ()\\\t\n]{0,16})\([\s\S]*?\)\1"|"(?:\\[\s\S]|[^"\\])*"|\'(?:\\[\s\S]|[^\'\\])*\''
    return re.sub(pattern, lambda m: " " * len(m[0]), text)


def complete(text, signature, semicolon=False):
    assert text.count(signature) == 1, signature
    start = text.index(signature)
    masked = mask_cpp(text)
    opening = masked.index("{", start)
    depth = 1
    end = opening + 1
    while depth:
        depth += (masked[end] == "{") - (masked[end] == "}")
        end += 1
    if semicolon:
        assert text[end] == ";"
        end += 1
    return text[start:end], start, end


NUMERIC = {
    'nsMathUtils.h': ['inline double NS_round(', 'inline int32_t NS_lround('],
    'nsCoord.h': ['inline nscoord NSToCoordRound(double', 'inline nscoord NSToCoordCeil(double',
        'inline nscoord NSToCoordCeilClamped(double', 'inline int32_t NSToIntRound(double',
        'inline nscoord NSCoordSaturatingAdd('],
}
FUNCTIONS = [
    ('struct TabWidth {', True), ('struct nsTextFrame::TabWidthStore {', True),
    ('struct TabwidthAdaptor {', True), ('void nsTextFrame::TabWidthStore::ApplySpacing(', False),
    ('static gfxFloat GetMinTabAdvanceAppUnits(', False),
    ('nsTextFrame::PropertyProvider::PropertyProvider(\n    gfxTextRun*', False),
    ('nsTextFrame::PropertyProvider::PropertyProvider(\n    nsTextFrame*', False),
    ('gfxFloat nsTextFrame::PropertyProvider::MinTabAdvance(', False),
    ('bool nsTextFrame::PropertyProvider::GetSpacing(', False),
    ('static bool CanAddSpacingBefore(', False), ('static bool CanAddSpacingAfter(', False),
    ('static gfxFloat ComputeTabWidthAppUnits(', False),
    ('bool nsTextFrame::PropertyProvider::GetSpacingInternal(', False),
    ('static gfxFloat AdvanceToNextTab(', False),
    ('void nsTextFrame::PropertyProvider::CalcTabWidths(', False),
    ('void nsTextFrame::AddInlineMinISizeForFlow(', False),
    ('void nsTextFrame::AddInlinePrefISizeForFlow(', False),
]
ACCESSORS = ['void SetStartOfLine(', 'bool HasSpacing() const', 'nscoord LetterSpacing() const',
             'const mozilla::dom::CharacterDataBuffer& GetCharacterDataBuffer() const']


def capsule(variant='candidate', mutation=None):
    binding=[]
    def get(path, signature, semi=False):
        text=(BASE/'source'/path).read_text()
        body,start,end=complete(text,signature,semi)
        binding.append(dict(source='source/'+path,signature=signature,start=start,end=end,
                            sha256=hashlib.sha256(body.encode()).hexdigest()))
        return body
    numeric='\n\n'.join(get(path,sig) for path,sigs in NUMERIC.items() for sig in sigs)
    accessors='\n\n'.join(get('nsTextFrame.h',sig) for sig in ACCESSORS)
    header=(BASE/'source/nsTextFrame.h').read_text()
    start=header.index('    const RefPtr<gfxTextRun> mTextRun;')
    end=header.index('\n  };',start)
    members=header[start:end]
    binding.append(dict(source='source/nsTextFrame.h',signature='PropertyProvider complete data members',start=start,end=end,
                        sha256=hashlib.sha256(members.encode()).hexdigest()))
    bodies=[get(variant+'.cpp',sig,semi) for sig,semi in FUNCTIONS]
    core='\n\n'.join(bodies)
    if mutation:core=mutation(core)
    adapter=(BASE/'adapter.cpp').read_text()
    for marker,value in [('@@NUMERIC@@',numeric),('@@MEMBERS@@',members),('@@ACCESSORS@@',accessors),('@@CORE@@',core),('@@MAIN@@',(BASE/'fixture.cpp').read_text())]:
        assert adapter.count(marker)==1
        adapter=adapter.replace(marker,value)
    return adapter,binding


if __name__ == '__main__':
    import sys
    print(capsule(sys.argv[1] if len(sys.argv)>1 else 'candidate')[0])
