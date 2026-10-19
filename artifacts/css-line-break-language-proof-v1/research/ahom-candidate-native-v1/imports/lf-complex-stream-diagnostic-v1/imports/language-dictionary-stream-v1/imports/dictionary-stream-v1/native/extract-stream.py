import json
import runpy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
helper=runpy.run_path(str(ROOT/'native/extract-full.py'))
OUT=ROOT/'development-build/full'
adaptations=[]
def replace_once(text,before,after,name):
    count=text.count(before);assert count==1,(name,count)
    adaptations.append({'name':name,'before':before,'after':after,'count':count})
    return text.replace(before,after)
for flavor in ['original','candidate','standalone']:
    text=helper['generate'](flavor).read_text()
    runner=(ROOT/'native/full-runner.cpp').read_text();assert text.endswith(runner)
    text=text[:-len(runner)]+(ROOT/'native/stream-runner.cpp').read_text()
    old_language=flavor=='standalone'
    hit='if (sLastHyphenationLanguage == aHyphenationLanguage) {'if old_language else'if (sLastLanguage == aLanguage) {'
    text=replace_once(text,hit,hit+'\n    language_trace("resolver cache hit");',flavor+' cache hit')
    entry='if (aHyphenationLanguage && !mCurrentWordLanguage) {'if old_language else'static bool IsChineseOrJapanese(nsAtom* aLanguage) {'
    value='aHyphenationLanguage->value'if old_language else'(aLanguage?aLanguage->value:"<null>")'
    text=replace_once(text,entry,entry+'\n  language_trace((std::string("resolver request ")+'+value+').c_str());',flavor+' resolver request')
    marker='void nsLineBreaker::FindHyphenationPoints('
    start=text.index('{',text.index(marker))+1
    triple='unsigned(mHyphenateLimitWord)<<":"<<unsigned(mHyphenateLimitStart)<<":"<<unsigned(mHyphenateLimitEnd)'if flavor=='original'else'unsigned(aLimits.mWord)<<":"<<unsigned(aLimits.mStart)<<":"<<unsigned(aLimits.mEnd)'
    trace='\n  std::cout<<traceCase<<" HYPHEN "<<'+triple+'<<" UNITS";for(auto p=aTextStart;p!=aTextLimit;++p)std::cout<<" "<<unsigned(*p);std::cout<<" BEFORE ";for(size_t i=0;i<size_t(aTextLimit-aTextStart);++i)std::cout<<unsigned(aBreakState[i]);std::cout<<"\\n";\n'
    trace=trace.replace('std::cout<<traceCase', 'std::cout<<currentCaseIdentity()')
    text='#include <string>\nconst std::string& currentCaseIdentity();\n'+text[:start]+trace+text[start:]
    text=replace_once(text,'static std::string traceCase;','static std::string traceCase;\nconst std::string& currentCaseIdentity(){return traceCase;}',flavor+' case identity')
    text=replace_once(text,'nsHyphenator*GetHyphenator(nsAtom*a){','nsHyphenator*GetHyphenator(nsAtom*a){std::cout<<currentCaseIdentity()<<" LOOKUP "<<(a?a->value:"<null>")<<"\\n";',flavor+' lookup event')
    capital='static void SetupCapitalization(const char16_t* aWord, uint32_t aLength,\n                                bool* aCapitalization) {'
    text=replace_once(text,capital,capital+'\n std::cout<<currentCaseIdentity()<<" CAPITALIZE";for(uint32_t i=0;i<aLength;i++)std::cout<<" "<<unsigned(aWord[i]);std::cout<<"\\n";',flavor+' capitalization event')
    (OUT/f'stream-{flavor}.cpp').write_text(text)
(OUT/'stream-extraction.json').write_text(json.dumps({'functions':helper['records'],'adaptations':adaptations},indent=2)+'\n')
