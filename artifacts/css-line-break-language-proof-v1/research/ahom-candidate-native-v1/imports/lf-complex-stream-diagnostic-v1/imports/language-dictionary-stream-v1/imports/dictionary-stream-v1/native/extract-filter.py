import json
import runpy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
helper=runpy.run_path(str(ROOT/'native/extract-full.py'))
full=helper['full']
source=helper['generate']('candidate').read_text()
runner=(ROOT/'native/full-runner.cpp').read_text();assert source.endswith(runner);source=source[:-len(runner)]
limits=full(ROOT/'source/candidate/dom/base/nsLineBreaker.h','struct HyphenationLimits {',True)
method=full(ROOT/'source/candidate/dom/base/nsLineBreaker.cpp','void nsLineBreaker::FindHyphenationPoints(')
method=method.replace('nsLineBreaker::FindHyphenationPoints','FilterHarness::FindHyphenationPoints').replace('nsHyphenator* aHyphenator','MaskFixtureProvider* aHyphenator')
facade="""struct MaskFixtureProvider { std::vector<bool> mask; nsresult Hyphenate(const nsAString& text,nsTArray<bool>& out){assert(text.Length()==mask.size());out.SetLength(mask.size());for(size_t i=0;i<mask.size();i++)out[i]=mask[i];return NS_OK;} };
class FilterHarness { public:
"""+limits+"""
void FindHyphenationPoints(MaskFixtureProvider*,const char16_t*,const char16_t*,uint8_t*,const HyphenationLimits&);
};
"""
OUT=ROOT/'development-build/full'
(OUT/'filter.cpp').write_text(source+facade+method+'\n'+(ROOT/'native/filter-runner.cpp').read_text())
(OUT/'filter-extraction.json').write_text(json.dumps({'source_extracts':helper['records'],'adaptations':['class qualifier FilterHarness; parameter type MaskFixtureProvider; method body unchanged'],'boundary':'arbitrary-mask filter test only; actual dictionary runs use the unmodified nsHyphenator path'},indent=2)+'\n')
