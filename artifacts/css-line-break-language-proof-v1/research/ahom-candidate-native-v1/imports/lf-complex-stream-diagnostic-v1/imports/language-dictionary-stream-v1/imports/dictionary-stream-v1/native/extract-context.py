import json
import runpy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
helper=runpy.run_path(str(ROOT/'native/extract-full.py'))
full=helper['full'];OUT=ROOT/'development-build/full'
changes=[]
def once(text,before,after,name):
 count=text.count(before);assert count==1,(name,count)
 changes.append({'name':name,'before':before,'after':after,'count':count})
 return text.replace(before,after)
base=(OUT/'range-types-adapted.hpp').read_text()
base=once(base,'struct nsIFrame;','struct nsIFrame;struct nsTextFrame;','forward frame')
base=once(base,'bool WhiteSpaceCanWrap(const nsIFrame*)const;','bool WhiteSpaceCanWrap(const nsIFrame*)const;bool NewlineIsSignificant(const nsTextFrame*)const;','newline declaration')
base=once(base,'bool wide=true;','bool wide=true;mutable std::string byteStorage;const char*Get1b()const{byteStorage.assign(units.begin(),units.end());return byteStorage.data();}','byte storage facade')
base=once(base,'enum class TextRunType{Inflated};','enum class TextRunType{Inflated};bool ShouldSuppressLineBreak()const{return false;}','line suppression facade')
base+=full(ROOT/'source/providers/layout/style/nsStyleStructInlines.h','bool nsStyleText::NewlineIsSignificant(')
(OUT/'context-types.hpp').write_text(base)
for flavor in ['original','candidate','standalone']:
 text=(OUT/f'range-{flavor}.cpp').read_text()
 text=once(text,'#include "range-types-adapted.hpp"','#include "context-types.hpp"',flavor+' types')
 runner=(ROOT/'native/range-runner.cpp').read_text();assert text.endswith(runner)
 text=text[:-len(runner)]
 text=once(text,'void FlushLineBreaks(gfxTextRun*);','void FlushLineBreaks(gfxTextRun*);bool SetupLineBreakerContext(gfxTextRun*);uint8_t mNextRunContextInfo=0;',flavor+' context declaration')
 source=ROOT/f'source/{flavor}/layout/generic/nsTextFrame.cpp'
 methods='\n'.join(full(source,marker)for marker in ['static nsTextFrameUtils::CompressionMode GetCSSWhitespaceToCompressionMode(','static char16_t* ExpandBuffer(','bool BuildTextRunsScanner::SetupLineBreakerContext('])
 runner=once(runner,'scanner.SetupBreakSinksForTextRun(&run,encoding==16?static_cast<const void*>(transformed.data()):static_cast<const void*>(bytes.data()));','assert(scanner.SetupLineBreakerContext(&run));',flavor+' runner uses complete context')
 text+='\nconstexpr size_t BIG_TEXT_NODE_SIZE=4096;\n'+methods+'\n'+runner
 (OUT/f'context-{flavor}.cpp').write_text(text)
(OUT/'context-extraction.json').write_text(json.dumps({'functions':helper['records'],'adaptations':changes,'facades':['CharacterDataBuffer byte storage','ShouldSuppressLineBreak always false; no SVG/text-combine context admitted by runner']},indent=2)+'\n')
