import hashlib,json,runpy,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
segmenter=(ROOT/'source/providers/intl/lwbrk/Segmenter.h').read_text()
enums='\n'.join(re.search(r'enum class '+name+r' : uint8_t \{.*?\n\};',segmenter,re.S)[0] for name in ['WordBreakRule','LineBreakRule'])
(ROOT/'development-build/provider/enums.h').write_text('namespace mozilla::intl {\n'+enums+'\n}\n')
helper=runpy.run_path(str(ROOT/'native/extract-stream.py'))
OUT=ROOT/'development-build/flush-stream';OUT.mkdir(exist_ok=True,parents=True)
records=[]
for flavor in ['original','candidate']:
 source=helper['generate'](flavor)
 text=source.read_text()
 marker='void nsLineBreaker::FindHyphenationPoints('
 start=text.index(marker);brace=text.index('{',start)
 trace='\n  { std::ostringstream event;event<<"filter input "<<unsigned(mHyphenateLimitWord)<<" "<<unsigned(mHyphenateLimitStart)<<" "<<unsigned(mHyphenateLimitEnd)<<" TEXT";for(auto p=aTextStart;p!=aTextLimit;++p)event<<" "<<unsigned(*p);event<<" OLD";for(auto p=aTextStart;p!=aTextLimit;++p)event<<" "<<unsigned(aBreakState[p-aTextStart]);language_trace(event.str().c_str()); }\n'
 text=text[:brace+1]+trace+text[brace+1:]
 start=text.index('static void dump_state(');end=text.index('int main(',start)
 body=text[start:end];before=' std::cout<<"\\n";'
 assert body.count(before)==1,(flavor,body)
 after=' std::cout<<" LIMITS "<<unsigned(b.mHyphenateLimitWord)<<":"<<unsigned(b.mHyphenateLimitStart)<<":"<<unsigned(b.mHyphenateLimitEnd)<<"\\n";'
 text=text[:start]+body.replace(before,after)+text[end:]
 replacements=[
 ('nsHyphenator*GetHyphenator(nsAtom*a){','nsHyphenator*GetHyphenator(nsAtom*a){language_trace((std::string("hyphenator lookup ")+(a?a->value:"<null>")).c_str());'),
 ('                                bool* aCapitalization) {','                                bool* aCapitalization) {\n  {std::ostringstream event;event<<"capitalize input";for(uint32_t i=0;i<aLength;i++)event<<" "<<unsigned(aWord[i]);language_trace(event.str().c_str());}'),
 ]
 for before,after in replacements:
  assert text.count(before)==1,(flavor,before,text.count(before));text=text.replace(before,after)
 target=OUT/(flavor+'.cpp');target.write_text(text)
 records.append({'flavor':flavor,'base_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'output_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'filter_trace':trace,'replacements':replacements})
(OUT/'LANGUAGE-TRACE-GENERATION.json').write_text(json.dumps({'extractor':helper['adaptations'],'trace_records':records},indent=2)+'\n')
