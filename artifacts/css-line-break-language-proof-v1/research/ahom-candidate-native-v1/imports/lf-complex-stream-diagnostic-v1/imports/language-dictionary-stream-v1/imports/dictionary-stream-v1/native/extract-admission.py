import json,runpy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'development-build/full'
helper=runpy.run_path(str(ROOT/'native/extract-full.py'));full=helper['full'];frame=ROOT/'source/candidate/layout/generic/nsTextFrame.cpp';utils=ROOT/'source/providers/layout/base/nsLayoutUtils.cpp'
text=(ROOT/'native/admission-prefix.hpp').read_text()
text+='\nnamespace gfx{'+full(ROOT/'provider-bridge-v1/source/providers/gfx/thebes/gfxFont.h','enum class ShapedTextFlags : uint16_t',True)
text+='\ninline ShapedTextFlags operator|(ShapedTextFlags a,ShapedTextFlags b){return ShapedTextFlags(uint16_t(a)|uint16_t(b));}inline ShapedTextFlags&operator|=(ShapedTextFlags&a,ShapedTextFlags b){return a=a|b;} }\n'
text+='namespace nsLayoutUtils{const nsIFrame*FindNearestCommonAncestorFrameWithinBlock(const nsTextFrame*,const nsTextFrame*);gfx::ShapedTextFlags GetTextRunOrientFlagsForStyle(const ComputedStyle*);gfx::ShapedTextFlags GetTextRunFlagsForStyle(const ComputedStyle*,nsPresContext*,const nsStyleFont*,const nsStyleText*,nscoord); }\n'
for path,marker in [(ROOT/'source/providers/layout/style/nsStyleStructInlines.h','bool nsStyleText::NewlineIsSignificant('),(frame,'static bool HasTerminalNewline('),(frame,'static bool HasDefaultVerticalAlignment('),(frame,'static nscoord ResolveLetterSpacing('),(utils,'const nsIFrame* nsLayoutUtils::FindNearestCommonAncestorFrameWithinBlock('),(utils,'gfx::ShapedTextFlags nsLayoutUtils::GetTextRunFlagsForStyle('),(utils,'gfx::ShapedTextFlags nsLayoutUtils::GetTextRunOrientFlagsForStyle('),(frame,'bool BuildTextRunsScanner::ContinueTextRunAcrossFrames(')]:text+=full(path,marker)+'\n'
text+=(ROOT/'native/admission-runner.cpp').read_text()
(OUT/'admission.cpp').write_text(text)
(OUT/'admission-extraction.json').write_text(json.dumps({'functions':helper['records'],'scope':'Complete continuation admission, newline/style/vertical-boundary/nearest-common-ancestor and text-run flag native bodies. Primitive frame tree, computed style property, writing-mode physical-side, length resolution, SVG scale, font and context representations remain explicit providers. No live scanner traversal or shaping implied.'},indent=2)+'\n')
